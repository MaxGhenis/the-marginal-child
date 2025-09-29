"""Test PolicyEngine axes implementation"""

from policyengine_us import Simulation
import numpy as np

def test_basic_axes():
    """Test basic axes functionality with PolicyEngine"""

    # Test with simple situation varying income
    income_values = [0, 10000, 20000, 30000]

    situation = {
        "people": {
            "adult": {
                "age": 30,
                "employment_income": {2024: income_values}  # Pass array directly
            }
        },
        "families": {
            "family": {"members": ["adult"]}
        },
        "households": {
            "household": {
                "members": ["adult"],
                "state_code": {2024: "TX"}
            }
        },
        "tax_units": {
            "tax_unit": {"members": ["adult"]}
        },
        "spm_units": {
            "spm_unit": {"members": ["adult"]}
        }
    }

    try:
        sim = Simulation(situation=situation)
        net_incomes = sim.calculate("household_net_income", 2024)
        print(f"Success! Got {len(net_incomes)} results")
        print(f"Net incomes: {net_incomes}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_axes_with_children():
    """Test axes with children"""

    income_values = [0, 10000, 20000, 30000]

    situation = {
        "people": {
            "adult": {
                "age": 30,
                "employment_income": {2024: income_values}
            },
            "child_1": {
                "age": 10
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

    try:
        sim = Simulation(situation=situation)
        net_incomes = sim.calculate("household_net_income", 2024)
        print(f"With children - Success! Got {len(net_incomes)} results")
        print(f"Net incomes: {net_incomes}")
        return True
    except Exception as e:
        print(f"With children - Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing PolicyEngine axes implementation...")
    print("-" * 50)

    print("Test 1: Basic axes")
    test_basic_axes()

    print("\nTest 2: Axes with children")
    test_axes_with_children()