from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

POLICYENGINE_API_URL = "https://api.policyengine.org/us"

def create_household_json(params):
    """Create household JSON for PolicyEngine API."""

    people = {
        "parent1": {
            "age": {"2024": params.get("parent1_age", 30)},
            "employment_income": {"2024": params.get("employment_income", 0)},
        }
    }

    members = ["parent1"]

    # Add spouse if married
    if params.get("marital_status") == "married":
        people["parent2"] = {
            "age": {"2024": params.get("parent2_age", 30)},
            "employment_income": {"2024": params.get("spouse_income", 0)},
        }
        members.append("parent2")

    # Add children
    num_children = params.get("num_children", 0)
    for i in range(num_children):
        child_key = f"child{i+1}"
        child_age = params.get(f"child{i+1}_age", 5)
        people[child_key] = {"age": {"2024": child_age}}
        members.append(child_key)

    household = {
        "people": people,
        "households": {
            "household": {
                "members": members,
                "state_code": {"2024": params.get("state", "TX")},
                "snap": {"2024": None},
                "wic": {"2024": None},
                "medicaid": {"2024": None},
                "household_net_income": {"2024": None},
            }
        },
        "families": {
            "family": {
                "members": members,
            }
        },
        "tax_units": {
            "tax_unit": {
                "members": members,
                "premium_tax_credit": {"2024": None},
            }
        },
        "spm_units": {
            "spm_unit": {
                "members": members,
                "spm_unit_fpg": {"2024": None},
            }
        },
        "marital_units": {}
    }

    # Create marital units
    if params.get("marital_status") == "married":
        household["marital_units"]["marital_unit_parents"] = {
            "members": ["parent1", "parent2"]
        }
    else:
        household["marital_units"]["marital_unit_parent1"] = {
            "members": ["parent1"]
        }

    # Add separate marital units for children
    for i in range(num_children):
        child_key = f"child{i+1}"
        household["marital_units"][f"marital_unit_{child_key}"] = {
            "members": [child_key]
        }

    return household

@app.route('/api/calculate', methods=['POST'])
def calculate_benefits():
    """Calculate benefits using PolicyEngine API."""
    params = request.json

    try:
        household = create_household_json(params)

        # Call PolicyEngine API
        response = requests.post(
            f"{POLICYENGINE_API_URL}/calculate",
            json={"household": household}
        )

        if response.status_code != 200:
            return jsonify({"error": "PolicyEngine API error"}), 500

        result = response.json()

        # Extract relevant values
        return jsonify({
            "snap": result.get("snap", {}).get("2024", 0),
            "wic": result.get("wic", {}).get("2024", 0),
            "medicaid": result.get("medicaid", {}).get("2024", 0),
            "chip": result.get("chip", {}).get("2024", 0),
            "premium_tax_credit": result.get("premium_tax_credit", {}).get("2024", 0),
            "eitc": result.get("eitc", {}).get("2024", 0),
            "ctc": result.get("ctc", {}).get("2024", 0),
            "cdcc": result.get("cdcc", {}).get("2024", 0),
            "housing_subsidy": result.get("housing_subsidy", {}).get("2024", 0),
            "net_income": result.get("household_net_income", {}).get("2024", 0),
            "market_income": result.get("household_market_income", {}).get("2024", 0),
            "federal_poverty_guideline": result.get("spm_unit_fpg", {}).get("2024", 0),
            "marginal_tax_rate": result.get("marginal_tax_rate", {}).get("2024", 0),
            "total_benefits": sum([
                result.get("snap", {}).get("2024", 0),
                result.get("wic", {}).get("2024", 0),
                result.get("medicaid", {}).get("2024", 0),
                result.get("chip", {}).get("2024", 0),
                result.get("premium_tax_credit", {}).get("2024", 0),
                result.get("eitc", {}).get("2024", 0),
                result.get("ctc", {}).get("2024", 0),
                result.get("cdcc", {}).get("2024", 0),
                result.get("housing_subsidy", {}).get("2024", 0),
            ])
        })

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

            household = create_household_json(params_copy)

            response = requests.post(
                f"{POLICYENGINE_API_URL}/calculate",
                json={"household": household}
            )

            if response.status_code != 200:
                continue

            result = response.json()

            results.append({
                "income": income,
                "snap": result.get("snap", {}).get("2024", 0),
                "wic": result.get("wic", {}).get("2024", 0),
                "medicaid": result.get("medicaid", {}).get("2024", 0),
                "chip": result.get("chip", {}).get("2024", 0),
                "premium_tax_credit": result.get("premium_tax_credit", {}).get("2024", 0),
                "eitc": result.get("eitc", {}).get("2024", 0),
                "ctc": result.get("ctc", {}).get("2024", 0),
                "cdcc": result.get("cdcc", {}).get("2024", 0),
                "housing_subsidy": result.get("housing_subsidy", {}).get("2024", 0),
                "net_income": result.get("household_net_income", {}).get("2024", 0),
                "total_benefits": sum([
                    result.get("snap", {}).get("2024", 0),
                    result.get("wic", {}).get("2024", 0),
                    result.get("medicaid", {}).get("2024", 0),
                    result.get("chip", {}).get("2024", 0),
                    result.get("premium_tax_credit", {}).get("2024", 0),
                    result.get("eitc", {}).get("2024", 0),
                    result.get("ctc", {}).get("2024", 0),
                    result.get("cdcc", {}).get("2024", 0),
                    result.get("housing_subsidy", {}).get("2024", 0),
                ])
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

                household = create_household_json(params_copy)

                response = requests.post(
                    f"{POLICYENGINE_API_URL}/calculate",
                    json={"household": household}
                )

                if response.status_code != 200:
                    continue

                result = response.json()
                net_income = result.get("household_net_income", {}).get("2024", 0)

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