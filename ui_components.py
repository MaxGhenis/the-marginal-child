"""UI components for the Marginal Child application."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from calculations import get_child_ordinal
from constants import COLORS, DEFAULT_STATE_INDEX, US_STATES


def render_header():
    """Render the application header with branding."""
    st.markdown(
        """
        <style>
        .stApp {
            font-family: 'Roboto', 'Helvetica', 'Arial', sans-serif;
        }
        h1 {
            color: #2C6496;
            font-weight: 600;
        }
        .subtitle {
            color: #666;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("The Marginal Child")
        st.markdown(
            '<p class="subtitle">Analyze how government benefits change with each additional child</p>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            '<div style="text-align: right; padding-top: 1rem;">Powered by PolicyEngine</div>',
            unsafe_allow_html=True,
        )


def render_sidebar() -> tuple:
    """Render the sidebar configuration panel.

    Returns:
        Tuple of (marital_status, state_code, spouse_income, include_health_benefits, calculate_button)
    """
    with st.sidebar:
        st.header("Household Configuration")

        marital_status = st.selectbox(
            "Marital Status",
            options=["single", "married"],
            format_func=lambda x: x.title(),
            key="marital_status",
        )

        state_code = st.selectbox(
            "State",
            options=[code for code, _ in US_STATES],
            format_func=lambda x: next(
                name for code, name in US_STATES if code == x
            ),
            index=DEFAULT_STATE_INDEX,  # Default to Texas
            key="state",
        )

        spouse_income = 0
        if marital_status == "married":
            spouse_income = st.number_input(
                "Spouse Income ($)",
                min_value=0,
                max_value=500000,
                value=0,
                step=1000,
                key="spouse_income",
                help="Annual employment income of spouse",
            )

        st.markdown("---")

        include_health_benefits = st.checkbox(
            "Include health insurance value (Medicaid, CHIP, ACA subsidies)",
            value=True,
            help="When checked, includes the monetary value of health insurance benefits in the net income calculation",
        )

        st.markdown(
            "**Note:** All children are assumed to be age 10 for benefit calculations."
        )

        calculate_button = st.button(
            "Calculate Marginal Benefits",
            type="primary",
            use_container_width=True,
        )

    return (
        marital_status,
        state_code,
        spouse_income,
        include_health_benefits,
        calculate_button,
    )


def create_benefits_plot(df: pd.DataFrame) -> go.Figure:
    """Create the marginal benefits plot.

    Args:
        df: DataFrame with calculation results

    Returns:
        Plotly figure object
    """
    fig = go.Figure()

    # Add traces for each child
    for i, child_num in enumerate(sorted(df["num_children"].unique())):
        child_data = df[df["num_children"] == child_num]
        fig.add_trace(
            go.Scatter(
                x=child_data["income"],
                y=child_data["marginal_benefit"],
                mode="lines",
                name=f"{get_child_ordinal(child_num)} child",
                line=dict(
                    color=COLORS["gradient"][i % len(COLORS["gradient"])],
                    width=3,
                ),
                hovertemplate="Income: $%{x:,.0f}<br>Marginal Benefit: $%{y:,.0f}<extra></extra>",
            )
        )

    # Update layout
    fig.update_layout(
        title={
            "text": "Net Income Change from Taxes and Benefits per Additional Child",
            "font": {"size": 20, "color": COLORS["primary"]},
        },
        xaxis=dict(
            title="Earnings",
            tickformat="$,.0f",
            gridcolor="rgba(0,0,0,0.1)",
        ),
        yaxis=dict(
            title="Net Income Change for Additional Child",
            tickformat="$,.0f",
            rangemode="tozero",
            gridcolor="rgba(0,0,0,0.1)",
        ),
        hovermode="x unified",
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Roboto, sans-serif"),
        legend=dict(
            title="Child Number",
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
        ),
        height=600,
    )

    return fig


def render_summary_statistics(df: pd.DataFrame):
    """Render summary statistics cards.

    Args:
        df: DataFrame with calculation results
    """
    st.header("Summary Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        avg_benefit_1st = df[df["num_children"] == 1][
            "marginal_benefit"
        ].mean()
        st.metric("Average - 1st Child", f"${avg_benefit_1st:,.0f}")

    with col2:
        avg_benefit_2nd = df[df["num_children"] == 2][
            "marginal_benefit"
        ].mean()
        st.metric("Average - 2nd Child", f"${avg_benefit_2nd:,.0f}")

    with col3:
        avg_benefit_3rd = df[df["num_children"] == 3][
            "marginal_benefit"
        ].mean()
        st.metric("Average - 3rd Child", f"${avg_benefit_3rd:,.0f}")

    with col4:
        avg_benefit_4th = df[df["num_children"] == 4][
            "marginal_benefit"
        ].mean()
        st.metric("Average - 4th Child", f"${avg_benefit_4th:,.0f}")
