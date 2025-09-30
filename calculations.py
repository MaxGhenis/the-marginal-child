"""Calculation logic for the Marginal Child application."""

import logging
from typing import Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st
from policyengine_us import Simulation

from constants import (
    DEFAULT_ADULT_AGE,
    DEFAULT_CHILD_AGE,
    INCOME_MAX,
    INCOME_MIN,
    INCOME_STEP,
    MAX_CHILDREN,
    US_STATES,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_inputs(
    marital_status: str,
    state_code: str,
    spouse_income: float,
    include_health_benefits: bool,
) -> None:
    """Validate input parameters.

    Args:
        marital_status: Either 'single' or 'married'
        state_code: Two-letter US state code
        spouse_income: Annual income of spouse
        include_health_benefits: Whether to include health insurance value

    Raises:
        ValueError: If any input is invalid
    """
    if marital_status not in ["single", "married"]:
        raise ValueError(f"Invalid marital status: {marital_status}")

    valid_states = [code for code, _ in US_STATES]
    if state_code not in valid_states:
        raise ValueError(f"Invalid state code: {state_code}")

    if spouse_income < 0:
        raise ValueError(f"Spouse income cannot be negative: {spouse_income}")

    if spouse_income > 0 and marital_status == "single":
        logger.warning(
            "Spouse income provided for single household, will be ignored"
        )

    if not isinstance(include_health_benefits, bool):
        raise ValueError(
            f"include_health_benefits must be boolean: {include_health_benefits}"
        )


def create_household_situation(
    num_children: int,
    marital_status: str,
    state_code: str,
    spouse_income: float,
) -> Dict:
    """Create a household situation dictionary for PolicyEngine.

    Args:
        num_children: Number of children in the household
        marital_status: Either 'single' or 'married'
        state_code: Two-letter US state code
        spouse_income: Income of spouse (0 if single)

    Returns:
        Dictionary representing the household situation

    Raises:
        ValueError: If num_children is negative or exceeds MAX_CHILDREN
    """
    if num_children < 0:
        raise ValueError(f"Number of children cannot be negative: {num_children}")

    if num_children > MAX_CHILDREN:
        raise ValueError(
            f"Number of children cannot exceed {MAX_CHILDREN}: {num_children}"
        )
    situation = {
        "people": {
            "adult": {
                "age": {2024: DEFAULT_ADULT_AGE},
            }
        }
    }

    # Add spouse if married
    if marital_status == "married":
        situation["people"]["spouse"] = {
            "age": {2024: DEFAULT_ADULT_AGE},
            "employment_income": {2024: spouse_income},
        }

    # Add children (all age 10)
    for i in range(num_children):
        situation["people"][f"child_{i+1}"] = {
            "age": {2024: DEFAULT_CHILD_AGE}
        }

    # Create family and household structure
    members = ["adult"]
    if marital_status == "married":
        members.append("spouse")
    members.extend([f"child_{i+1}" for i in range(num_children)])

    situation["families"] = {"family": {"members": members}}

    situation["households"] = {
        "household": {"members": members, "state_code": {2024: state_code}}
    }

    situation["tax_units"] = {"tax_unit": {"members": members}}

    situation["spm_units"] = {"spm_unit": {"members": members}}

    return situation


@st.cache_data(show_spinner=False)
def calculate_marginal_child_benefits(
    marital_status: str,
    state_code: str,
    spouse_income: float,
    include_health_benefits: bool,
) -> pd.DataFrame:
    """Calculate marginal benefits for children 1-4 across income range.

    This function uses PolicyEngine-US with axes to efficiently calculate
    net income across multiple income levels for households with 0-4 children.

    Args:
        marital_status: Either 'single' or 'married'
        state_code: Two-letter US state code
        spouse_income: Annual income of spouse (0 if single)
        include_health_benefits: Whether to include health insurance value

    Returns:
        DataFrame with columns: income, num_children, marginal_benefit, net_income

    Raises:
        ValueError: If inputs are invalid
        Exception: If PolicyEngine calculation fails
    """
    # Validate inputs
    try:
        validate_inputs(
            marital_status, state_code, spouse_income, include_health_benefits
        )
    except ValueError as e:
        logger.error(f"Input validation failed: {e}")
        raise
    results = []

    # Progress bar for calculation
    progress_bar = st.progress(0)
    status_text = st.empty()

    income_points = list(range(INCOME_MIN, INCOME_MAX + 1, INCOME_STEP))

    # Store net incomes for each number of children
    all_net_incomes = {}

    # Calculate for each number of children using axes for income
    for num_kids in range(MAX_CHILDREN + 1):
        # Update progress
        progress = (num_kids + 1) / (MAX_CHILDREN + 1)
        progress_bar.progress(progress)
        status_text.text(
            f"Calculating with {num_kids} children across all income levels..."
        )

        # Create base situation
        situation = create_household_situation(
            num_kids, marital_status, state_code, spouse_income
        )

        # Add axes for employment income variation
        situation["axes"] = [
            [
                {
                    "name": "employment_income",
                    "count": len(income_points),
                    "min": INCOME_MIN,
                    "max": INCOME_MAX,
                }
            ]
        ]

        # Run simulation with the situation containing axes
        try:
            sim = Simulation(situation=situation)
        except Exception as e:
            logger.error(f"Failed to create simulation: {e}")
            status_text.error(f"Calculation error: {str(e)}")
            progress_bar.empty()
            raise

        # Get net income - either with or without health benefits value
        try:
            if include_health_benefits:
                # Calculate net income including health benefits value
                # This includes Medicaid, CHIP, and ACA premium tax credits
                net_incomes = sim.calculate(
                    "household_net_income_including_health_benefits", 2024
                )
            else:
                # Use regular net income (cash benefits only)
                net_incomes = sim.calculate("household_net_income", 2024)

        except Exception as e:
            logger.error(f"Failed to calculate net income: {e}")
            status_text.error(f"Calculation error: {str(e)}")
            progress_bar.empty()
            raise

        # Store results
        all_net_incomes[num_kids] = net_incomes

    # Calculate marginal benefits (difference between N and N-1 children)
    for num_kids in range(1, MAX_CHILDREN + 1):
        current_net_incomes = all_net_incomes[num_kids]
        previous_net_incomes = all_net_incomes[
            num_kids - 1
        ]  # Compare with N-1 children

        for i, income in enumerate(income_points):
            marginal_benefit = float(
                current_net_incomes[i] - previous_net_incomes[i]
            )

            results.append(
                {
                    "income": income,
                    "num_children": num_kids,
                    "marginal_benefit": marginal_benefit,
                    "net_income": float(current_net_incomes[i]),
                }
            )

    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()

    return pd.DataFrame(results)


def get_child_ordinal(num: int) -> str:
    """Get ordinal string for a child number.

    Args:
        num: Child number (1-4)

    Returns:
        Ordinal string (1st, 2nd, 3rd, 4th)
    """
    ordinals = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th"}
    return ordinals.get(num, f"{num}th")