"""Test correct PolicyEngine axes implementation"""

from policyengine_us import Simulation
import numpy as np

def test_axes_correct_format():
    """Test axes with correct format - using multiple situations"""

    # Create list of income values
    income_values = [0, 10000, 20000, 30000]

    # Create a list of situations - one for each income value
    situations = []
    for income in income_values:
        situation = {
            "people": {
                "adult": {
                    "age": {2024: 30},
                    "employment_income": {2024: income}
                },
                "child_1": {
                    "age": {2024: 10}
                }
            },
            "families": {
                "family": {"members": ["adult", "child_1"]}
            },
            "households": {
                "household": {
                    "members": ["adult", "child_1"],
                    "state_code": {2024: "TX"}
                }
            },
            "tax_units": {
                "tax_unit": {"members": ["adult", "child_1"]}
            },
            "spm_units": {
                "spm_unit": {"members": ["adult", "child_1"]}
            }
        }
        situations.append(situation)

    # Use axes parameter with list of situations
    try:
        sim = Simulation(situations=situations)
        net_incomes = sim.calculate("household_net_income", 2024)
        print(f"Success with situations list! Got {len(net_incomes)} results")
        print(f"Net incomes: {net_incomes}")
        return True
    except Exception as e:
        print(f"Error with situations list: {e}")

    # Alternative: Try with axes parameter directly
    base_situation = {
        "people": {
            "adult": {
                "age": {2024: 30},
                "employment_income": {2024: 0}  # Will be overridden by axes
            },
            "child_1": {
                "age": {2024: 10}
            }
        },
        "families": {
            "family": {"members": ["adult", "child_1"]}
        },
        "households": {
            "household": {
                "members": ["adult", "child_1"],
                "state_code": {2024: "TX"}
            }
        },
        "tax_units": {
            "tax_unit": {"members": ["adult", "child_1"]}
        },
        "spm_units": {
            "spm_unit": {"members": ["adult", "child_1"]}
        }
    }

    # Create axes as list of dicts with overrides
    axes = [[
        {"people": {"adult": {"employment_income": {2024: income}}}}
        for income in income_values
    ]]

    try:
        sim = Simulation(situation=base_situation, axes=axes)
        net_incomes = sim.calculate("household_net_income", 2024)
        print(f"Success with axes parameter! Got {len(net_incomes)} results")
        print(f"Net incomes: {net_incomes}")
        return True
    except Exception as e:
        print(f"Error with axes parameter: {e}")
        import traceback
        traceback.print_exc()

    return False

if __name__ == "__main__":
    print("Testing correct PolicyEngine axes implementation...")
    print("-" * 50)
    test_axes_correct_format()