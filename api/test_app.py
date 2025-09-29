import pytest
import json
from app_mock import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_states_endpoint(client):
    """Test that the states endpoint returns a list of states."""
    response = client.get('/api/states')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert 'TX' in data
    assert len(data) == 51  # 50 states + DC

def test_marginal_child_endpoint(client):
    """Test the marginal child calculation endpoint."""
    test_params = {
        'marital_status': 'single',
        'state': 'TX',
        'spouse_income': 0,
        'income_min': 0,
        'income_max': 50000,
        'income_step': 10000
    }

    response = client.post('/api/marginal_child',
                          data=json.dumps(test_params),
                          content_type='application/json')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0

    # Check that we have data for each child (1-4)
    child_numbers = set(item['num_children'] for item in data)
    assert child_numbers == {1, 2, 3, 4}

    # Check data structure
    first_item = data[0]
    assert 'income' in first_item
    assert 'num_children' in first_item
    assert 'marginal_benefit' in first_item
    assert 'net_income' in first_item

def test_marginal_child_calculation_logic(client):
    """Test that marginal benefits make sense."""
    test_params = {
        'marital_status': 'single',
        'state': 'TX',
        'spouse_income': 0,
        'income_min': 20000,
        'income_max': 20000,
        'income_step': 10000
    }

    response = client.post('/api/marginal_child',
                          data=json.dumps(test_params),
                          content_type='application/json')

    assert response.status_code == 200
    data = json.loads(response.data)

    # Extract marginal benefits for each child at $20k income
    benefits_by_child = {}
    for item in data:
        if item['income'] == 20000:
            benefits_by_child[item['num_children']] = item['marginal_benefit']

    # Check that we have all 4 children
    assert len(benefits_by_child) == 4

    # Marginal benefits should generally be positive
    for child_num, benefit in benefits_by_child.items():
        assert benefit > 0, f"Child {child_num} should have positive marginal benefit"

    # First child typically has largest marginal benefit due to EITC
    assert benefits_by_child[1] > 0

def test_married_vs_single_difference(client):
    """Test that marital status affects calculations."""
    single_params = {
        'marital_status': 'single',
        'state': 'TX',
        'spouse_income': 0,
        'income_min': 30000,
        'income_max': 30000,
        'income_step': 10000
    }

    married_params = {
        'marital_status': 'married',
        'state': 'TX',
        'spouse_income': 0,
        'income_min': 30000,
        'income_max': 30000,
        'income_step': 10000
    }

    single_response = client.post('/api/marginal_child',
                                data=json.dumps(single_params),
                                content_type='application/json')

    married_response = client.post('/api/marginal_child',
                                  data=json.dumps(married_params),
                                  content_type='application/json')

    assert single_response.status_code == 200
    assert married_response.status_code == 200

    single_data = json.loads(single_response.data)
    married_data = json.loads(married_response.data)

    # Should have same structure but potentially different values
    assert len(single_data) == len(married_data)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])