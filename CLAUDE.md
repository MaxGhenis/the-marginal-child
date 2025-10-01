# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Marginal Child is a Streamlit application that analyzes how government benefits change with each additional child using PolicyEngine-US microsimulation. It visualizes marginal benefits across different income levels for various household configurations.

## Commands

### Development
```bash
# Install dependencies
make install
# or
pip install -r requirements.txt

# Run the Streamlit application
make run
# or
streamlit run app.py

# Clean up cache and temporary files
make clean
```

### Testing
```bash
# Run individual test files (no test framework required)
python test_axes_final.py
python test_health_benefits.py
```

## Architecture

### Core Calculation Engine
The app uses PolicyEngine-US's `axes` feature for efficient income variation calculations:
- **Axes must be embedded INSIDE the situation dictionary** (not passed separately)
- Creates multiple income scenarios in a single simulation for performance
- Format: `situation["axes"] = [[{"name": "employment_income", "count": N, "min": 0, "max": 200000}]]`

### Key Functions in app.py
- `calculate_marginal_child_benefits()`: Main calculation function using PolicyEngine axes
  - Calculates net income for 0-4 children across income range ($0-$200k)
  - Returns marginal benefit per additional child
  - Handles both single and married households
  - Optionally includes health insurance value in net income

### State Management
- Uses Streamlit's native state management
- Key inputs: marital status, state code, spouse income, health benefits toggle
- Real-time recalculation on input change

### Visualization
- Uses Plotly for interactive charts
- PolicyEngine brand colors defined in COLORS dict
- Shows marginal benefits for 1st, 2nd, and 3rd child
- Displays average benefit statistics

## PolicyEngine-US Integration

### Situation Structure
All PolicyEngine simulations require these entity groups:
- `people`: Individual entities (adults, children)
- `families`: Family groupings
- `households`: Household entity with state_code
- `tax_units`: Tax filing units
- `spm_units`: Supplemental Poverty Measure units

### Performance Optimization
- Uses axes for income variation (81x faster than individual simulations)
- Calculates all income points in single simulation per child count
- Progress bars for user feedback during calculations

## Testing Approach
- Standalone Python test files (no pytest/unittest framework)
- Direct execution: `python test_filename.py`
- Tests verify axes functionality and benefit calculations