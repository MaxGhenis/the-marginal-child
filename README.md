# The Marginal Child

An interactive web application that analyzes how government benefits change with each additional child, powered by [PolicyEngine-US](https://github.com/PolicyEngine/policyengine-us).

## Features

- **Dynamic Benefit Calculations**: Uses PolicyEngine-US for accurate, up-to-date calculations of:
  - SNAP (Food Stamps)
  - WIC
  - Medicaid
  - CHIP (Children's Health Insurance Program)
  - Premium Tax Credits (ACA Marketplace)
  - EITC (Earned Income Tax Credit)
  - Child Tax Credit
  - Child and Dependent Care Credit
  - Housing subsidies

- **Interactive Visualizations**:
  - Benefit cliff analysis showing how benefits phase out with income
  - Net income vs employment income comparison
  - Marginal benefit per additional child across income ranges

- **State-Specific Analysis**: Calculate benefits for all 50 states plus DC

- **Customizable Household Configuration**:
  - Marital status
  - Number and ages of children
  - Housing and childcare costs
  - Employment income for both spouses

## Installation

### Prerequisites

- Python 3.10+
- Node.js 22+
- uv (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/the-marginal-child.git
cd the-marginal-child
```

2. Install Python dependencies:
```bash
cd api
uv venv
uv pip install -r requirements.txt
cd ..
```

3. Install Node dependencies:
```bash
npm install
```

## Running the Application

You'll need to run both the Python API backend and the React frontend:

### Terminal 1: Start the API server
```bash
cd api
uv run python app.py
```
The API will run on http://localhost:5000

### Terminal 2: Start the React development server
```bash
npm run dev
```
The app will open at http://localhost:5173

## Usage

1. **Configure Household**: Set your household parameters including marital status, state, number of children, and income.

2. **Add Child Ages**: Specify ages for each child (affects benefit eligibility).

3. **Set Analysis Parameters**: Choose the income range and step size for the analysis.

4. **Run Analysis**:
   - **Calculate Current Benefits**: See benefits at your specified income level
   - **Analyze Benefit Cliff**: Visualize how benefits change across income ranges
   - **Analyze Marginal Child**: See the marginal benefit of each additional child

## How It Works

The application uses PolicyEngine-US's microsimulation model to calculate benefits based on actual federal and state policy rules. Unlike simple calculators with hard-coded values, this app:

- Uses actual policy parameters (Federal Poverty Guidelines, benefit formulas, etc.) from PolicyEngine
- Accounts for interactions between programs
- Includes state-specific variations
- Updates automatically as PolicyEngine updates its models

## Technology Stack

- **Backend**: Flask API with PolicyEngine-US
- **Frontend**: React with Vite
- **UI Components**: Material-UI
- **Charts**: Plotly.js
- **Calculations**: PolicyEngine-US microsimulation engine

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT

## Acknowledgments

Built using [PolicyEngine-US](https://policyengine.org), the open-source microsimulation model for US tax and benefit policy.
