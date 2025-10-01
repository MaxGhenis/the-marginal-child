# The Marginal Child

A Streamlit application that analyzes how government benefits change with each additional child, powered by PolicyEngine.

## Overview

This application visualizes the marginal benefit of having additional children across different income levels, taking into account various government programs including:

- SNAP (Food Stamps)
- WIC (Women, Infants, and Children nutrition program)
- Medicaid/CHIP (Healthcare)
- Premium Tax Credits
- EITC (Earned Income Tax Credit)
- Child Tax Credit
- Child and Dependent Care Credit

## Features

- **Interactive Visualizations**: Real-time chart updates showing net income changes per additional child
- **State-Specific Analysis**: Calculate benefits for all 50 US states plus DC
- **Customizable Household Configuration**:
  - Marital status (single/married)
  - State selection
  - Spouse income (if married)
- **Summary Statistics**: Average benefits for 1st, 2nd, and 3rd children

## Installation

### Prerequisites

- Python 3.9+

### Setup

1. Clone the repository:
```bash
git clone https://github.com/PolicyEngine/the-marginal-child.git
cd the-marginal-child
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

```bash
streamlit run app.py
```

The app will open in your browser at http://localhost:8501

## How It Works

The application calculates the marginal benefit of each additional child by:
1. Computing net income (earnings + benefits) for households with 0-4 children
2. Calculating the difference in net income for each additional child
3. Displaying these marginal benefits across the full income range ($0-$200,000)

All children are assumed to be age 10 for benefit calculation purposes.

## Technology Stack

- **Framework**: Streamlit for rapid prototyping and deployment
- **Visualization**: Plotly for interactive charts
- **Data Processing**: Pandas and NumPy
- **Styling**: PolicyEngine brand colors and design system

## Deployment

The app can be deployed to:
- Streamlit Cloud (recommended for quick deployment)
- Any cloud provider supporting Python web apps
- Docker containers

For Streamlit Cloud deployment:
1. Push to GitHub
2. Connect repository to Streamlit Cloud
3. Deploy with one click

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT

## Acknowledgments

Powered by [PolicyEngine](https://policyengine.org), the open-source microsimulation infrastructure for tax and benefit policy.
