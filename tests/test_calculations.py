"""Test calculations for the Marginal Child application."""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest


def test_calculate_marginal_child_benefits():
    """Test the marginal child benefit calculation."""
    # Import here to avoid issues if module structure changes
    from app import calculate_marginal_child_benefits

    # Mock the Simulation class to avoid actual PolicyEngine API calls
    with patch("app.Simulation") as MockSimulation:
        # Setup mock simulation
        mock_sim = MagicMock()
        MockSimulation.return_value = mock_sim

        # Mock the calculation results
        mock_sim.calc.return_value = [0, 25000, 50000, 75000, 100000]
        mock_sim.calculate.return_value = [15000, 35000, 55000, 70000, 85000]

        # Test single person household
        result = calculate_marginal_child_benefits(
            marital_status="single",
            state_code="TX",
            spouse_income=0,
            include_health_benefits=False,
        )

        # Verify result is a DataFrame
        assert isinstance(result, pd.DataFrame)

        # Verify columns exist
        expected_columns = [
            "income",
            "num_children",
            "marginal_benefit",
            "net_income",
        ]
        assert all(col in result.columns for col in expected_columns)

        # Verify we have data for children 1-4
        assert set(result["num_children"].unique()) == {1, 2, 3, 4}


def test_state_code_validation():
    """Test that all US state codes are valid options."""
    from app import calculate_marginal_child_benefits

    # Test with a valid state code
    with patch("app.Simulation") as MockSimulation:
        mock_sim = MagicMock()
        MockSimulation.return_value = mock_sim
        mock_sim.calc.return_value = [0]
        mock_sim.calculate.return_value = [15000]

        # Should not raise an error with valid state
        try:
            calculate_marginal_child_benefits(
                marital_status="single",
                state_code="CA",
                spouse_income=0,
                include_health_benefits=False,
            )
        except Exception as e:
            pytest.fail(f"Valid state code raised an exception: {e}")


def test_married_household_configuration():
    """Test that married households include spouse correctly."""
    from app import calculate_marginal_child_benefits

    with patch("app.Simulation") as MockSimulation:
        # Capture the situation passed to Simulation
        situations_created = []

        def simulation_init(situation=None, **kwargs):
            situations_created.append(situation)
            mock_sim = MagicMock()
            mock_sim.calc.return_value = [0, 25000]
            mock_sim.calculate.return_value = [15000, 35000]
            return mock_sim

        MockSimulation.side_effect = simulation_init

        # Test married household
        calculate_marginal_child_benefits(
            marital_status="married",
            state_code="TX",
            spouse_income=30000,
            include_health_benefits=False,
        )

        # Verify spouse was included in at least one situation
        assert len(situations_created) > 0
        # Check first situation (0 children case)
        first_situation = situations_created[0]
        assert "spouse" in first_situation["people"]
        assert (
            first_situation["people"]["spouse"]["employment_income"][2024]
            == 30000
        )


def test_health_benefits_inclusion():
    """Test that health benefits are calculated when requested."""
    from app import calculate_marginal_child_benefits

    with patch("app.Simulation") as MockSimulation:
        mock_sim = MagicMock()
        MockSimulation.return_value = mock_sim

        # Setup different values for with/without health benefits
        mock_sim.calc.return_value = [0, 25000]

        # Track which variable was calculated
        calculated_variables = []

        def mock_calculate(variable_name, year):
            calculated_variables.append(variable_name)
            if "health" in variable_name:
                return [20000, 40000]  # Higher with health benefits
            else:
                return [15000, 35000]  # Regular net income

        mock_sim.calculate = mock_calculate

        # Test with health benefits
        result_with_health = calculate_marginal_child_benefits(
            marital_status="single",
            state_code="TX",
            spouse_income=0,
            include_health_benefits=True,
        )

        # Verify the right variable was calculated
        assert (
            "household_net_income_including_health_benefits"
            in calculated_variables
        )
