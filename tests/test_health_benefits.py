"""Test health benefits calculation with axes."""

from policyengine_us import Simulation


def test_health_benefits_variable_exists():
    """Test that the health benefits variable exists."""
    from policyengine_us import CountryTaxBenefitSystem

    tbs = CountryTaxBenefitSystem()
    assert "household_net_income_including_health_benefits" in tbs.variables


def test_health_benefits_without_axes():
    """Test that health benefits calculation works without axes."""
    situation = {
        "people": {"adult": {"age": {2024: 30}}},
        "families": {"family": {"members": ["adult"]}},
        "households": {
            "household": {"members": ["adult"], "state_code": {2024: "CA"}}
        },
        "tax_units": {"tax_unit": {"members": ["adult"]}},
        "spm_units": {"spm_unit": {"members": ["adult"]}},
    }

    sim = Simulation(situation=situation)
    result = sim.calculate(
        "household_net_income_including_health_benefits", 2024
    )

    assert len(result) == 1
    assert isinstance(result[0], (int, float))


def test_health_benefits_with_axes():
    """Test that health benefits calculation works WITH axes.

    This is the critical test - it currently fails with dtype error.
    """
    situation = {
        "people": {"adult": {"age": {2024: 30}}},
        "families": {"family": {"members": ["adult"]}},
        "households": {
            "household": {"members": ["adult"], "state_code": {2024: "CA"}}
        },
        "tax_units": {"tax_unit": {"members": ["adult"]}},
        "spm_units": {"spm_unit": {"members": ["adult"]}},
        "axes": [
            [{"name": "employment_income", "count": 3, "min": 0, "max": 50000}]
        ],
    }

    sim = Simulation(situation=situation)
    result = sim.calculate(
        "household_net_income_including_health_benefits", 2024
    )

    # Should return 3 values (one for each income point in axes)
    assert len(result) == 3
    # All values should be numeric
    for val in result:
        assert isinstance(val, (int, float))
        assert not float("inf") == val  # No infinities
        assert val == val  # No NaN


def test_household_net_income_with_axes():
    """Test that regular net income works with axes (baseline test)."""
    situation = {
        "people": {"adult": {"age": {2024: 30}}},
        "families": {"family": {"members": ["adult"]}},
        "households": {
            "household": {"members": ["adult"], "state_code": {2024: "CA"}}
        },
        "tax_units": {"tax_unit": {"members": ["adult"]}},
        "spm_units": {"spm_unit": {"members": ["adult"]}},
        "axes": [
            [{"name": "employment_income", "count": 3, "min": 0, "max": 50000}]
        ],
    }

    sim = Simulation(situation=situation)
    result = sim.calculate("household_net_income", 2024)

    assert len(result) == 3
    for val in result:
        assert isinstance(val, (int, float))
