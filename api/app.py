from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np

# Import PolicyEngine after other imports to avoid circular dependencies
import sys
import warnings
warnings.filterwarnings('ignore')

try:
    from policyengine_us import Simulation
except ImportError as e:
    print(f"Warning: Could not import policyengine_us directly: {e}")
    # Try alternative import
    from policyengine_us.system import system
    from policyengine_core.simulations import Simulation as CoreSimulation

    class Simulation(CoreSimulation):
        def __init__(self, *args, **kwargs):
            super().__init__(tax_benefit_system=system, *args, **kwargs)

app = Flask(__name__)
CORS(app)

def create_situation(params):
    """Create a PolicyEngine situation based on input parameters."""
    people = {
        "parent1": {
            "age": {"2024": params.get("parent1_age", 30)},
            "employment_income": {"2024": params.get("employment_income", 0)},
        }
    }

    families = {"family": {"members": ["parent1"]}}
    marital_units = {"marital_unit": {"members": ["parent1"]}}
    tax_units = {"tax_unit": {"members": ["parent1"]}}
    spm_units = {"spm_unit": {"members": ["parent1"]}}
    households = {
        "household": {
            "members": ["parent1"],
            "state_name": {"2024": params.get("state", "TX")},
        }
    }

    # Add spouse if married
    if params.get("marital_status") == "married":
        people["parent2"] = {
            "age": {"2024": params.get("parent2_age", 30)},
            "employment_income": {"2024": params.get("spouse_income", 0)},
        }
        families["family"]["members"].append("parent2")
        marital_units["marital_unit"]["members"].append("parent2")
        tax_units["tax_unit"]["members"].append("parent2")
        spm_units["spm_unit"]["members"].append("parent2")
        households["household"]["members"].append("parent2")

    # Add children
    num_children = params.get("num_children", 0)
    for i in range(num_children):
        child_key = f"child{i+1}"
        child_age = params.get(f"child{i+1}_age", 5)
        people[child_key] = {"age": {"2024": child_age}}
        families["family"]["members"].append(child_key)
        tax_units["tax_unit"]["members"].append(child_key)
        spm_units["spm_unit"]["members"].append(child_key)
        households["household"]["members"].append(child_key)

        # Create separate marital unit for child
        marital_units[f"{child_key}_marital_unit"] = {
            "members": [child_key],
            "marital_unit_id": {"2024": i + 2}
        }

    # Add pregnant women if specified
    if params.get("pregnant_women", 0) > 0:
        people["parent1"]["is_pregnant"] = {"2024": True}

    # Add housing costs if specified
    if params.get("housing_cost", 0) > 0:
        spm_units["spm_unit"]["spm_unit_pre_subsidy_rent"] = {"2024": params.get("housing_cost", 0) * 12}

    # Add childcare costs if specified
    if params.get("childcare_cost", 0) > 0:
        spm_units["spm_unit"]["spm_unit_pre_subsidy_childcare_expenses"] = {"2024": params.get("childcare_cost", 0) * 12}

    return {
        "people": people,
        "families": families,
        "marital_units": marital_units,
        "tax_units": tax_units,
        "spm_units": spm_units,
        "households": households,
    }

@app.route('/api/calculate', methods=['POST'])
def calculate_benefits():
    """Calculate benefits for a single income point."""
    params = request.json

    try:
        situation = create_situation(params)
        sim = Simulation(situation=situation)

        # Calculate key benefits
        year = 2024

        # Get federal poverty guideline
        fpg = sim.calculate("spm_unit_fpg", year)

        # Calculate individual benefits
        snap = sim.calculate("snap", year)
        wic = sim.calculate("wic", year)

        # Healthcare programs
        medicaid = sim.calculate("medicaid", year)
        chip = sim.calculate("chip", year)
        premium_tax_credit = sim.calculate("premium_tax_credit", year)

        # Tax credits
        eitc = sim.calculate("eitc", year)
        ctc = sim.calculate("ctc", year)
        cdcc = sim.calculate("cdcc", year)

        # Housing assistance
        housing_subsidy = sim.calculate("housing_subsidy", year)

        # Get household net income
        net_income = sim.calculate("household_net_income", year)
        market_income = sim.calculate("household_market_income", year)

        # Calculate marginal tax rate
        mtr = sim.calculate("marginal_tax_rate", year)

        results = {
            "federal_poverty_guideline": float(fpg),
            "snap": float(snap),
            "wic": float(wic),
            "medicaid": float(medicaid),
            "chip": float(chip),
            "premium_tax_credit": float(premium_tax_credit),
            "eitc": float(eitc),
            "ctc": float(ctc),
            "cdcc": float(cdcc),
            "housing_subsidy": float(housing_subsidy),
            "net_income": float(net_income),
            "market_income": float(market_income),
            "marginal_tax_rate": float(mtr.mean()) if hasattr(mtr, 'mean') else float(mtr),
            "total_benefits": float(snap + wic + medicaid + chip + premium_tax_credit +
                                  eitc + ctc + cdcc + housing_subsidy),
        }

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/calculate_cliff', methods=['POST'])
def calculate_cliff():
    """Calculate benefit cliff data across income range."""
    params = request.json

    try:
        income_min = params.get("income_min", 0)
        income_max = params.get("income_max", 100000)
        income_step = params.get("income_step", 1000)

        results = []

        for income in range(income_min, income_max + 1, income_step):
            params_copy = params.copy()
            params_copy["employment_income"] = income

            situation = create_situation(params_copy)
            sim = Simulation(situation=situation)

            year = 2024

            # Calculate all benefits
            snap = float(sim.calculate("snap", year))
            wic = float(sim.calculate("wic", year))
            medicaid = float(sim.calculate("medicaid", year))
            chip = float(sim.calculate("chip", year))
            premium_tax_credit = float(sim.calculate("premium_tax_credit", year))
            eitc = float(sim.calculate("eitc", year))
            ctc = float(sim.calculate("ctc", year))
            cdcc = float(sim.calculate("cdcc", year))
            housing_subsidy = float(sim.calculate("housing_subsidy", year))
            net_income = float(sim.calculate("household_net_income", year))

            results.append({
                "income": income,
                "snap": snap,
                "wic": wic,
                "medicaid": medicaid,
                "chip": chip,
                "premium_tax_credit": premium_tax_credit,
                "eitc": eitc,
                "ctc": ctc,
                "cdcc": cdcc,
                "housing_subsidy": housing_subsidy,
                "total_benefits": snap + wic + medicaid + chip + premium_tax_credit +
                                eitc + ctc + cdcc + housing_subsidy,
                "net_income": net_income,
            })

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/marginal_child', methods=['POST'])
def calculate_marginal_child():
    """Calculate the marginal benefit of each additional child."""
    params = request.json

    try:
        max_children = params.get("max_children", 5)
        income_min = params.get("income_min", 0)
        income_max = params.get("income_max", 200000)
        income_step = params.get("income_step", 5000)

        results = []

        for income in range(income_min, income_max + 1, income_step):
            prev_net_income = None

            for num_children in range(max_children + 1):
                params_copy = params.copy()
                params_copy["employment_income"] = income
                params_copy["num_children"] = num_children

                situation = create_situation(params_copy)
                sim = Simulation(situation=situation)

                year = 2024
                net_income = float(sim.calculate("household_net_income", year))

                if prev_net_income is not None and num_children > 0:
                    marginal_benefit = net_income - prev_net_income

                    results.append({
                        "income": income,
                        "num_children": num_children,
                        "marginal_benefit": marginal_benefit,
                        "net_income": net_income,
                    })

                prev_net_income = net_income

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/states', methods=['GET'])
def get_states():
    """Get list of available states."""
    states = [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL",
        "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME",
        "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH",
        "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
        "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
    ]
    return jsonify(states)

if __name__ == '__main__':
    app.run(debug=True, port=5000)