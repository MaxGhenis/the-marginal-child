"""The Marginal Child - PolicyEngine Benefit Calculator"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

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

# Federal Poverty Guidelines 2024
FPG_2024 = {
    1: 15060, 2: 20440, 3: 25820, 4: 31200,
    5: 36580, 6: 41960, 7: 47340, 8: 52720
}

def get_fpg(household_size):
    if household_size <= 8:
        return FPG_2024.get(household_size, FPG_2024[8])
    return FPG_2024[8] + (household_size - 8) * 5380

def calculate_snap(income, household_size):
    monthly_income = income / 12
    fpg = get_fpg(household_size)
    gross_limit = fpg * 1.3

    if income > gross_limit:
        return 0

    # Simplified SNAP calculation
    max_benefit = {1: 291, 2: 535, 3: 766, 4: 973, 5: 1155, 6: 1386}
    max_monthly = max_benefit.get(household_size, 1386 + (household_size - 6) * 200)
    benefit = max(0, max_monthly - (monthly_income * 0.3))
    return benefit * 12

def calculate_medicaid_value(income, household_size, num_children):
    fpg = get_fpg(household_size)

    # Children usually eligible up to 200% FPG
    if num_children > 0 and income < fpg * 2:
        return num_children * 3000  # Estimated annual value per child

    # Adults in expansion states eligible up to 138% FPG
    if income < fpg * 1.38:
        return 6000  # Estimated annual value

    return 0

def calculate_eitc(income, num_children, married):
    # Simplified EITC calculation
    if num_children == 0:
        max_credit = 600
        phase_in_rate = 0.0765
        plateau_start = 7830
        phase_out_start = 17640 if married else 9800
        phase_out_rate = 0.0765
    elif num_children == 1:
        max_credit = 3995
        phase_in_rate = 0.34
        plateau_start = 11750
        phase_out_start = 29550 if married else 22300
        phase_out_rate = 0.1598
    elif num_children == 2:
        max_credit = 6604
        phase_in_rate = 0.4
        plateau_start = 16510
        phase_out_start = 29550 if married else 22300
        phase_out_rate = 0.2106
    else:  # 3 or more
        max_credit = 7430
        phase_in_rate = 0.45
        plateau_start = 16510
        phase_out_start = 29550 if married else 22300
        phase_out_rate = 0.2106

    if income <= plateau_start:
        return min(income * phase_in_rate, max_credit)
    elif income <= phase_out_start:
        return max_credit
    else:
        phase_out = max_credit - (income - phase_out_start) * phase_out_rate
        return max(0, phase_out)

def calculate_ctc(num_children):
    # Simplified CTC - $2000 per child
    return num_children * 2000

def calculate_wic(income, household_size, num_young_children):
    fpg = get_fpg(household_size)
    if income > fpg * 1.85:
        return 0
    # Estimated WIC benefit
    return num_young_children * 600  # ~$50/month per eligible child

def calculate_ptc(income, household_size):
    fpg = get_fpg(household_size)

    if income < fpg:
        return 0  # Medicaid eligible
    if income > fpg * 4:
        return 0  # Above 400% FPG

    # Simplified premium calculation
    benchmark_premium = 5000  # Simplified benchmark

    # Calculate expected contribution based on FPG %
    fpg_percent = income / fpg
    if fpg_percent <= 1.5:
        contribution_rate = 0.02
    elif fpg_percent <= 2.0:
        contribution_rate = 0.04
    elif fpg_percent <= 2.5:
        contribution_rate = 0.06
    elif fpg_percent <= 3.0:
        contribution_rate = 0.08
    else:
        contribution_rate = 0.085

    expected_contribution = income * contribution_rate
    return max(0, benchmark_premium - expected_contribution)

def calculate_marginal_child_benefits(marital_status, state, spouse_income):
    """Calculate marginal benefits for children 1-4 across income range"""

    max_children = 4
    income_min = 0
    income_max = 200000
    income_step = 2500

    results = []

    for test_income in range(income_min, income_max + 1, income_step):
        prev_net_income = None

        for num_kids in range(max_children + 1):
            total_income = test_income + spouse_income

            household_size = 1
            if marital_status == 'married':
                household_size += 1
            household_size += num_kids

            # Calculate all benefits
            snap = calculate_snap(total_income, household_size)
            wic = calculate_wic(total_income, household_size, min(num_kids, 2))
            medicaid = calculate_medicaid_value(total_income, household_size, num_kids)
            chip = 0
            ptc = calculate_ptc(total_income, household_size) if medicaid == 0 else 0
            eitc = calculate_eitc(total_income, num_kids, marital_status == 'married')
            ctc = calculate_ctc(num_kids)
            cdcc = min(num_kids * 1000, 3000) if num_kids > 0 else 0

            total_benefits = snap + wic + medicaid + chip + ptc + eitc + ctc + cdcc
            net_income = total_income + total_benefits

            if prev_net_income is not None and num_kids > 0:
                marginal_benefit = net_income - prev_net_income

                results.append({
                    'income': test_income,
                    'num_children': num_kids,
                    'marginal_benefit': marginal_benefit,
                    'net_income': net_income
                })

            prev_net_income = net_income

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
            format_func=lambda x: x.title()
        )

        # List of US states
        states = [
            "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL",
            "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME",
            "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH",
            "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
            "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
        ]

        state = st.selectbox(
            "State",
            options=states,
            index=states.index("TX")
        )

        spouse_income = 0
        if marital_status == 'married':
            spouse_income = st.number_input(
                "Spouse Income ($)",
                min_value=0,
                max_value=500000,
                value=0,
                step=1000
            )

        st.markdown("---")
        st.markdown("**Note:** All children are assumed to be age 10 for benefit calculations.")

    # Calculate results
    with st.spinner('Calculating marginal child benefits...'):
        df = calculate_marginal_child_benefits(marital_status, state, spouse_income)

    # Create the plot
    fig = go.Figure()

    # Add traces for each child
    for i, child_num in enumerate(sorted(df['num_children'].unique())):
        child_data = df[df['num_children'] == child_num]
        fig.add_trace(go.Scatter(
            x=child_data['income'],
            y=child_data['marginal_benefit'],
            mode='lines',
            name=f'Child {child_num}',
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