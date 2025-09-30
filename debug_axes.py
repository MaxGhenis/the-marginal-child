"""Debug script to test axes behavior - runs through Streamlit's env."""

import sys
sys.path.insert(0, '/Users/maxghenis/PolicyEngine/marginal-child')

from calculations import create_household_situation
from policyengine_us import Simulation


def test_axes_employment_income():
    """Test how employment income is distributed with axes."""

    # Test with 2 children - one with explicit 0, one without
    situation = create_household_situation(
        num_children=2,
        marital_status="single",
        state_code="CA",
        spouse_income=0
    )

    # Add axes
    situation["axes"] = [[{
        "name": "employment_income",
        "count": 3,
        "min": 0,
        "max": 100000,
    }]]

    print("Situation before simulation:")
    print("=" * 60)
    for person_id, person_data in situation["people"].items():
        income = person_data.get("employment_income", {}).get(2024, "NOT SET")
        print(f"{person_id}: employment_income = {income}")

    # Create simulation
    sim = Simulation(situation=situation)

    # Get employment income for each person
    adult_income = sim.calculate("employment_income", 2024, map_to="person")

    print("\n" + "=" * 60)
    print("After simulation with axes:")
    print("=" * 60)
    print(f"Total values returned: {len(adult_income)}")
    print(f"Expected: 3 people × 3 axis points = 9 values")

    # Try to extract by person
    # The values should be ordered as: [adult_point1, adult_point2, adult_point3, child1_point1, ...]
    num_people = 3  # adult + 2 children
    num_points = 3

    print("\nIncome values per person across axis points:")
    person_names = ["adult", "child_1", "child_2"]
    for i, name in enumerate(person_names):
        start_idx = i * num_points
        end_idx = start_idx + num_points
        values = adult_income[start_idx:end_idx]
        print(f"  {name}: {values}")

        if name == "adult" and len(set(values)) > 1:
            print(f"    ✓ Varies (axes applied)")
        elif name.startswith("child"):
            if all(v == 0 for v in values):
                print(f"    ✓ All zeros (axes NOT applied)")
            else:
                print(f"    ✗ NON-ZERO (axes INCORRECTLY applied!)")


if __name__ == "__main__":
    test_axes_employment_income()