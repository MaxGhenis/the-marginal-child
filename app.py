"""The Marginal Child - PolicyEngine Benefit Calculator"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from policyengine_us import Simulation

# Page configuration
st.set_page_config(
    page_title="The Marginal Child",
    page_icon="👶",
    layout="wide"
)

# PolicyEngine colors
COLORS = {
    'primary': '#2C6496',
    'secondary': '#39C6C0',
    'gradient': ['#D1E5F0', '#92C5DE', '#2166AC', '#053061'],
}

def calculate_marginal_child_benefits(marital_status, state_code, spouse_income, include_health_benefits):
    """Calculate marginal benefits for children 1-4 across income range using PolicyEngine-US with axes"""

    max_children = 4
    income_min = 0
    income_max = 200000
    income_step = 2500

    results = []

    # Progress bar for calculation
    progress_bar = st.progress(0)
    status_text = st.empty()

    income_points = list(range(income_min, income_max + 1, income_step))

    # Store net incomes for each number of children
    all_net_incomes = {}

    # Calculate for each number of children using axes for income
    for num_kids in range(max_children + 1):
        # Update progress
        progress = (num_kids + 1) / (max_children + 1)
        progress_bar.progress(progress)
        status_text.text(f'Calculating with {num_kids} children across all income levels...')

        # Create base situation
        situation = {
            "people": {
                "adult": {
                    "age": {2024: 30},
                }
            }
        }

        # Add spouse if married
        if marital_status == 'married':
            situation["people"]["spouse"] = {
                "age": {2024: 30},
                "employment_income": {2024: spouse_income}
            }

        # Add children (all age 10)
        for i in range(num_kids):
            situation["people"][f"child_{i+1}"] = {
                "age": {2024: 10}
            }

        # Create family and household structure
        members = ["adult"]
        if marital_status == 'married':
            members.append("spouse")
        members.extend([f"child_{i+1}" for i in range(num_kids)])

        situation["families"] = {
            "family": {"members": members}
        }

        situation["households"] = {
            "household": {
                "members": members,
                "state_code": {2024: state_code}
            }
        }

        situation["tax_units"] = {
            "tax_unit": {"members": members}
        }

        situation["spm_units"] = {
            "spm_unit": {"members": members}
        }

        # Add axes for employment income variation
        situation["axes"] = [[{
            "name": "employment_income",
            "count": len(income_points),
            "min": income_min,
            "max": income_max
        }]]

        # Run simulation with axes
        sim = Simulation(situation=situation)

        # Get net income - either with or without health benefits value based on checkbox
        if include_health_benefits:
            # Use the comprehensive measure that includes health insurance value
            net_incomes = sim.calculate("household_net_income_including_health_benefits", 2024)
        else:
            # Use regular net income (cash benefits only)
            net_incomes = sim.calculate("household_net_income", 2024)

        # Store results
        all_net_incomes[num_kids] = net_incomes

    # Calculate marginal benefits (difference between N and N-1 children)
    for num_kids in range(1, max_children + 1):
        current_net_incomes = all_net_incomes[num_kids]
        previous_net_incomes = all_net_incomes[num_kids - 1]  # Compare with N-1 children

        for i, income in enumerate(income_points):
            marginal_benefit = float(current_net_incomes[i] - previous_net_incomes[i])

            results.append({
                'income': income,
                'num_children': num_kids,
                'marginal_benefit': marginal_benefit,
                'net_income': float(current_net_incomes[i])
            })

    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()

    return pd.DataFrame(results)

def main():
    # Custom CSS for PolicyEngine styling
    st.markdown("""
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
    """, unsafe_allow_html=True)

    # Header with PolicyEngine branding
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("The Marginal Child")
        st.markdown('<p class="subtitle">Analyze how government benefits change with each additional child</p>', unsafe_allow_html=True)
    with col2:
        st.markdown(
            '<div style="text-align: right; padding-top: 1rem;">Powered by PolicyEngine</div>',
            unsafe_allow_html=True
        )

    # Sidebar for configuration
    with st.sidebar:
        st.header("Household Configuration")

        marital_status = st.selectbox(
            "Marital Status",
            options=['single', 'married'],
            format_func=lambda x: x.title(),
            key='marital_status'
        )

        # List of US states
        states = [
            ("AL", "Alabama"), ("AK", "Alaska"), ("AZ", "Arizona"), ("AR", "Arkansas"),
            ("CA", "California"), ("CO", "Colorado"), ("CT", "Connecticut"), ("DE", "Delaware"),
            ("DC", "District of Columbia"), ("FL", "Florida"), ("GA", "Georgia"), ("HI", "Hawaii"),
            ("ID", "Idaho"), ("IL", "Illinois"), ("IN", "Indiana"), ("IA", "Iowa"),
            ("KS", "Kansas"), ("KY", "Kentucky"), ("LA", "Louisiana"), ("ME", "Maine"),
            ("MD", "Maryland"), ("MA", "Massachusetts"), ("MI", "Michigan"), ("MN", "Minnesota"),
            ("MS", "Mississippi"), ("MO", "Missouri"), ("MT", "Montana"), ("NE", "Nebraska"),
            ("NV", "Nevada"), ("NH", "New Hampshire"), ("NJ", "New Jersey"), ("NM", "New Mexico"),
            ("NY", "New York"), ("NC", "North Carolina"), ("ND", "North Dakota"), ("OH", "Ohio"),
            ("OK", "Oklahoma"), ("OR", "Oregon"), ("PA", "Pennsylvania"), ("RI", "Rhode Island"),
            ("SC", "South Carolina"), ("SD", "South Dakota"), ("TN", "Tennessee"), ("TX", "Texas"),
            ("UT", "Utah"), ("VT", "Vermont"), ("VA", "Virginia"), ("WA", "Washington"),
            ("WV", "West Virginia"), ("WI", "Wisconsin"), ("WY", "Wyoming")
        ]

        state_code = st.selectbox(
            "State",
            options=[code for code, _ in states],
            format_func=lambda x: next(name for code, name in states if code == x),
            index=43,  # Default to Texas
            key='state'
        )

        spouse_income = 0
        if marital_status == 'married':
            spouse_income = st.number_input(
                "Spouse Income ($)",
                min_value=0,
                max_value=500000,
                value=0,
                step=1000,
                key='spouse_income'
            )

        st.markdown("---")

        # Add checkbox for including health benefits
        include_health_benefits = st.checkbox(
            "Include health insurance value (Medicaid, CHIP, ACA subsidies)",
            value=True,
            help="When checked, includes the monetary value of health insurance benefits in the net income calculation"
        )

        st.markdown("**Note:** All children are assumed to be age 10 for benefit calculations.")

        calculate_button = st.button(
            "Calculate Marginal Benefits",
            type="primary",
            use_container_width=True
        )

    # Main content
    if calculate_button or 'df' not in st.session_state:
        with st.spinner('Calculating marginal child benefits using PolicyEngine-US...'):
            df = calculate_marginal_child_benefits(marital_status, state_code, spouse_income, include_health_benefits)
            st.session_state.df = df
    else:
        df = st.session_state.df

    # Create the plot
    fig = go.Figure()

    # Add traces for each child
    for i, child_num in enumerate(sorted(df['num_children'].unique())):
        child_data = df[df['num_children'] == child_num]
        fig.add_trace(go.Scatter(
            x=child_data['income'],
            y=child_data['marginal_benefit'],
            mode='lines',
            name=f'{child_num}{"st" if child_num == 1 else "nd" if child_num == 2 else "rd" if child_num == 3 else "th"} child',
            line=dict(
                color=COLORS['gradient'][i % len(COLORS['gradient'])],
                width=3
            ),
            hovertemplate='Income: $%{x:,.0f}<br>Marginal Benefit: $%{y:,.0f}<extra></extra>'
        ))

    # Update layout
    fig.update_layout(
        title={
            'text': 'Net Income Change from Taxes and Benefits per Additional Child',
            'font': {'size': 20, 'color': COLORS['primary']}
        },
        xaxis=dict(
            title='Earnings',
            tickformat='$,.0f',
            gridcolor='rgba(0,0,0,0.1)'
        ),
        yaxis=dict(
            title='Net Income Change for Additional Child',
            tickformat='$,.0f',
            rangemode='tozero',
            gridcolor='rgba(0,0,0,0.1)'
        ),
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Roboto, sans-serif'),
        legend=dict(
            title='Child Number',
            orientation='v',
            yanchor='top',
            y=1,
            xanchor='left',
            x=1.02
        ),
        height=600
    )

    # Display the plot
    st.plotly_chart(fig, use_container_width=True)

    # Summary statistics
    st.header("Summary Statistics")

    col1, col2, col3 = st.columns(3)

    with col1:
        avg_benefit_1st = df[df['num_children'] == 1]['marginal_benefit'].mean()
        st.metric("Average Benefit - 1st Child", f"${avg_benefit_1st:,.0f}")

    with col2:
        avg_benefit_2nd = df[df['num_children'] == 2]['marginal_benefit'].mean()
        st.metric("Average Benefit - 2nd Child", f"${avg_benefit_2nd:,.0f}")

    with col3:
        avg_benefit_3rd = df[df['num_children'] == 3]['marginal_benefit'].mean()
        st.metric("Average Benefit - 3rd Child", f"${avg_benefit_3rd:,.0f}")

if __name__ == "__main__":
    main()