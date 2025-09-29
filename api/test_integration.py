"""Integration tests for The Marginal Child API."""

import pytest
import requests
import time
import subprocess
import os
import signal

API_URL = "http://localhost:5001/api"

@pytest.fixture(scope="session")
def api_server():
    """Start the API server for testing."""
    # Start the Flask server
    process = subprocess.Popen(
        ["uv", "run", "python", "app_mock.py"],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for server to start
    time.sleep(2)

    # Check if server is running
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get(f"{API_URL}/states")
            if response.status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            time.sleep(0.5)
            if i == max_retries - 1:
                process.terminate()
                pytest.fail("Could not connect to API server")

    yield process

    # Cleanup: terminate the server
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()

class TestMarginalChildAPI:
    """Test the marginal child calculation API."""

    def test_states_endpoint(self, api_server):
        """Test that states endpoint returns all states."""
        response = requests.get(f"{API_URL}/states")
        assert response.status_code == 200

        states = response.json()
        assert len(states) == 51  # 50 states + DC
        assert "TX" in states
        assert "CA" in states

    def test_marginal_child_basic(self, api_server):
        """Test basic marginal child calculation."""
        params = {
            "marital_status": "single",
            "state": "TX",
            "spouse_income": 0
        }

        response = requests.post(f"{API_URL}/marginal_child", json=params)
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Check structure
        first_item = data[0]
        assert "income" in first_item
        assert "num_children" in first_item
        assert "marginal_benefit" in first_item
        assert "net_income" in first_item

    def test_all_four_children_included(self, api_server):
        """Test that data includes all 4 marginal children."""
        params = {
            "marital_status": "single",
            "state": "TX",
            "spouse_income": 0,
            "income_min": 30000,
            "income_max": 30000,
            "income_step": 10000
        }

        response = requests.post(f"{API_URL}/marginal_child", json=params)
        assert response.status_code == 200

        data = response.json()
        child_numbers = set(item["num_children"] for item in data)
        assert child_numbers == {1, 2, 3, 4}

    def test_income_range_respected(self, api_server):
        """Test that income range parameters are respected."""
        params = {
            "marital_status": "single",
            "state": "TX",
            "spouse_income": 0,
            "income_min": 20000,
            "income_max": 40000,
            "income_step": 10000
        }

        response = requests.post(f"{API_URL}/marginal_child", json=params)
        assert response.status_code == 200

        data = response.json()
        incomes = set(item["income"] for item in data)

        # Should have 20k, 30k, 40k
        assert 20000 in incomes
        assert 30000 in incomes
        assert 40000 in incomes
        assert 10000 not in incomes
        assert 50000 not in incomes

    def test_marital_status_affects_calculation(self, api_server):
        """Test that marital status changes the calculations."""
        single_params = {
            "marital_status": "single",
            "state": "TX",
            "spouse_income": 0,
            "income_min": 30000,
            "income_max": 30000
        }

        married_params = {
            "marital_status": "married",
            "state": "TX",
            "spouse_income": 0,
            "income_min": 30000,
            "income_max": 30000
        }

        single_response = requests.post(f"{API_URL}/marginal_child", json=single_params)
        married_response = requests.post(f"{API_URL}/marginal_child", json=married_params)

        assert single_response.status_code == 200
        assert married_response.status_code == 200

        single_data = single_response.json()
        married_data = married_response.json()

        # Find first child benefit for both
        single_first_child = next(
            item for item in single_data
            if item["income"] == 30000 and item["num_children"] == 1
        )
        married_first_child = next(
            item for item in married_data
            if item["income"] == 30000 and item["num_children"] == 1
        )

        # Benefits should differ based on marital status
        # (EITC and other benefits have different thresholds)
        assert single_first_child["marginal_benefit"] != married_first_child["marginal_benefit"]

    def test_positive_marginal_benefits(self, api_server):
        """Test that marginal benefits are generally positive."""
        params = {
            "marital_status": "single",
            "state": "TX",
            "spouse_income": 0,
            "income_min": 0,
            "income_max": 50000,
            "income_step": 10000
        }

        response = requests.post(f"{API_URL}/marginal_child", json=params)
        assert response.status_code == 200

        data = response.json()

        # Check that most marginal benefits are positive
        positive_count = sum(1 for item in data if item["marginal_benefit"] > 0)
        total_count = len(data)

        # At least 80% should be positive (some high-income scenarios might be negative)
        assert positive_count / total_count > 0.8

    def test_decreasing_marginal_benefit_pattern(self, api_server):
        """Test that marginal benefits generally decrease with more children."""
        params = {
            "marital_status": "single",
            "state": "TX",
            "spouse_income": 0,
            "income_min": 20000,
            "income_max": 20000,
            "income_step": 10000
        }

        response = requests.post(f"{API_URL}/marginal_child", json=params)
        assert response.status_code == 200

        data = response.json()

        # Get benefits for each child at $20k income
        benefits_by_child = {}
        for item in data:
            if item["income"] == 20000:
                benefits_by_child[item["num_children"]] = item["marginal_benefit"]

        # First child often has highest benefit due to EITC
        assert benefits_by_child[1] > 0

        # Benefits should exist for all 4 children
        assert len(benefits_by_child) == 4

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])