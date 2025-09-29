from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np

app = Flask(__name__)
CORS(app)

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

@app.route('/api/calculate', methods=['POST'])
def calculate_benefits():
    params = request.json

    income = params.get('employment_income', 0)
    spouse_income = params.get('spouse_income', 0)
    total_income = income + spouse_income

    household_size = 1
    if params.get('marital_status') == 'married':
        household_size += 1

    num_children = params.get('num_children', 0)
    household_size += num_children

    # Calculate benefits
    snap = calculate_snap(total_income, household_size)
    wic = calculate_wic(total_income, household_size, min(num_children, 2))  # WIC for young children
    medicaid = calculate_medicaid_value(total_income, household_size, num_children)
    chip = 0  # Would calculate if not Medicaid eligible
    ptc = calculate_ptc(total_income, household_size) if medicaid == 0 else 0
    eitc = calculate_eitc(total_income, num_children, params.get('marital_status') == 'married')
    ctc = calculate_ctc(num_children)
    cdcc = min(num_children * 1000, 3000) if num_children > 0 else 0  # Simplified CDCC

    total_benefits = snap + wic + medicaid + chip + ptc + eitc + ctc + cdcc
    net_income = total_income + total_benefits

    # Calculate marginal tax rate (simplified)
    marginal_rate = 0.12  # Federal rate
    if total_income > 44726:
        marginal_rate = 0.22
    if total_income > 95376:
        marginal_rate = 0.24

    return jsonify({
        'snap': snap,
        'wic': wic,
        'medicaid': medicaid,
        'chip': chip,
        'premium_tax_credit': ptc,
        'eitc': eitc,
        'ctc': ctc,
        'cdcc': cdcc,
        'housing_subsidy': 0,
        'total_benefits': total_benefits,
        'net_income': net_income,
        'market_income': total_income,
        'federal_poverty_guideline': get_fpg(household_size),
        'marginal_tax_rate': marginal_rate
    })

@app.route('/api/calculate_cliff', methods=['POST'])
def calculate_cliff():
    params = request.json

    income_min = params.get('income_min', 0)
    income_max = params.get('income_max', 100000)
    income_step = params.get('income_step', 1000)

    results = []

    for test_income in range(income_min, income_max + 1, income_step):
        params_copy = params.copy()
        params_copy['employment_income'] = test_income

        # Get base parameters
        spouse_income = params_copy.get('spouse_income', 0)
        total_income = test_income + spouse_income

        household_size = 1
        if params_copy.get('marital_status') == 'married':
            household_size += 1

        num_children = params_copy.get('num_children', 0)
        household_size += num_children

        # Calculate benefits
        snap = calculate_snap(total_income, household_size)
        wic = calculate_wic(total_income, household_size, min(num_children, 2))
        medicaid = calculate_medicaid_value(total_income, household_size, num_children)
        chip = 0
        ptc = calculate_ptc(total_income, household_size) if medicaid == 0 else 0
        eitc = calculate_eitc(total_income, num_children, params_copy.get('marital_status') == 'married')
        ctc = calculate_ctc(num_children)
        cdcc = min(num_children * 1000, 3000) if num_children > 0 else 0

        total_benefits = snap + wic + medicaid + chip + ptc + eitc + ctc + cdcc
        net_income = total_income + total_benefits

        results.append({
            'income': test_income,
            'snap': snap,
            'wic': wic,
            'medicaid': medicaid,
            'chip': chip,
            'premium_tax_credit': ptc,
            'eitc': eitc,
            'ctc': ctc,
            'cdcc': cdcc,
            'housing_subsidy': 0,
            'total_benefits': total_benefits,
            'net_income': net_income
        })

    return jsonify(results)

@app.route('/api/marginal_child', methods=['POST'])
def calculate_marginal_child():
    params = request.json

    max_children = 4  # Always show 4 children
    income_min = params.get('income_min', 0)
    income_max = params.get('income_max', 200000)
    income_step = params.get('income_step', 2500)

    results = []

    for test_income in range(income_min, income_max + 1, income_step):
        prev_net_income = None

        for num_kids in range(max_children + 1):
            params_copy = params.copy()
            params_copy['employment_income'] = test_income
            params_copy['num_children'] = num_kids

            spouse_income = params_copy.get('spouse_income', 0)
            total_income = test_income + spouse_income

            household_size = 1
            if params_copy.get('marital_status') == 'married':
                household_size += 1
            household_size += num_kids

            # Calculate all benefits
            snap = calculate_snap(total_income, household_size)
            wic = calculate_wic(total_income, household_size, min(num_kids, 2))
            medicaid = calculate_medicaid_value(total_income, household_size, num_kids)
            chip = 0
            ptc = calculate_ptc(total_income, household_size) if medicaid == 0 else 0
            eitc = calculate_eitc(total_income, num_kids, params_copy.get('marital_status') == 'married')
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

    return jsonify(results)

@app.route('/api/states', methods=['GET'])
def get_states():
    states = [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL",
        "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME",
        "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH",
        "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
        "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
    ]
    return jsonify(states)

if __name__ == '__main__':
    app.run(debug=True, port=5000)