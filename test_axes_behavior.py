"""Test to verify how PolicyEngine axes apply to people with/without explicit values."""

from policyengine_us import Simulation


def test_axes_with_explicit_zero():
    """Test that setting employment_income=0 prevents axes from applying."""

    # Create a household with adult and two children
    # Adult: no employment_income set (should get axes)
    # Child 1: employment_income explicitly set to 0 (should NOT get axes)
    # Child 2: no employment_income set (should get axes if our assumption is wrong)

    situation = {
        "people": {
            "adult": {
                "age": {2024: 30},
                # No employment_income set - axes should apply
            },
            "child_1": {
                "age": {2024: 10},
                "employment_income": {2024: 0},  # Explicitly 0
            },
            "child_2": {
                "age": {2024: 10},
                # No employment_income set - will axes apply?
            },
        },
        "families": {"family": {"members": ["adult", "child_1", "child_2"]}},
        "households": {
            "household": {
                "members": ["adult", "child_1", "child_2"],
                "state_code": {2024: "CA"},
            }
        },
        "tax_units": {
            "tax_unit": {"members": ["adult", "child_1", "child_2"]}
        },
        "spm_units": {
            "spm_unit": {"members": ["adult", "child_1", "child_2"]}
        },
        "axes": [
            [
                {
                    "name": "employment_income",
                    "count": 3,
                    "min": 0,
                    "max": 100000,
                }
            ]
        ],
    }

    sim = Simulation(situation=situation)

    # Get employment income for each person
    adult_income = sim.calculate("employment_income", 2024, map_to="person")

    print("Test: Axes behavior with explicit zero values")
    print("=" * 60)
    print(f"\nNumber of simulation variants: {len(adult_income) // 3}")
    print(f"Expected: 3 variants (one per axis point)")

    # Extract income by person
    print("\nAdult employment income across axes:")
    print(f"  {adult_income[0:3]}")

    print("\nChild 1 employment income (explicit 0):")
    print(f"  {adult_income[3:6]}")

    print("\nChild 2 employment income (not set):")
    print(f"  {adult_income[6:9]}")

    # Verify expectations
    print("\n" + "=" * 60)
    print("Analysis:")

    # Adult should have varying income
    adult_values = adult_income[0:3]
    if len(set(adult_values)) > 1:
        print("✓ Adult income varies (axes applied)")
    else:
        print("✗ Adult income does NOT vary (axes NOT applied)")

    # Child 1 (explicit 0) should stay at 0
    child1_values = adult_income[3:6]
    if all(v == 0 for v in child1_values):
        print("✓ Child 1 stays at 0 (explicit value prevents axes)")
    else:
        print(
            f"✗ Child 1 varies: {child1_values} (explicit 0 does NOT prevent axes!)"
        )

    # Child 2 (not set) - this will reveal the default behavior
    child2_values = adult_income[6:9]
    if len(set(child2_values)) > 1:
        print(
            f"✗ Child 2 varies: {child2_values} (axes applied when not set!)"
        )
    else:
        print(f"✓ Child 2 stays at {child2_values[0]} (axes not applied)")


if __name__ == "__main__":
    test_axes_with_explicit_zero()
