"""The Marginal Child - PolicyEngine Benefit Calculator.

A Streamlit application that analyzes how government benefits change
with each additional child, powered by PolicyEngine.
"""

import streamlit as st

from calculations import calculate_marginal_child_benefits
from ui_components import (
    create_benefits_plot,
    render_header,
    render_sidebar,
    render_summary_statistics,
)

# Page configuration
st.set_page_config(
    page_title="The Marginal Child", page_icon="👶", layout="wide"
)


def main():
    """Main application entry point."""
    # Render header
    render_header()

    # Get sidebar inputs
    (
        marital_status,
        state_code,
        spouse_income,
        include_health_benefits,
        calculate_button,
    ) = render_sidebar()

    # Main content
    if calculate_button or "df" not in st.session_state:
        try:
            with st.spinner(
                "Calculating marginal child benefits using PolicyEngine-US..."
            ):
                df = calculate_marginal_child_benefits(
                    marital_status,
                    state_code,
                    spouse_income,
                    include_health_benefits,
                )
                st.session_state.df = df
        except ValueError as e:
            st.error(f"Invalid input: {str(e)}")
            st.stop()
        except Exception as e:
            st.error(
                f"An error occurred during calculation: {str(e)}\n\n"
                "Please try again or contact support if the issue persists."
            )
            st.stop()
    else:
        df = st.session_state.df

    # Create and display the plot
    fig = create_benefits_plot(df)
    st.plotly_chart(fig, use_container_width=True)

    # Display summary statistics
    render_summary_statistics(df)


if __name__ == "__main__":
    main()