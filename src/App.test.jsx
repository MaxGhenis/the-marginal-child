import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from './App';
import axios from 'axios';

// Mock axios
jest.mock('axios');

describe('The Marginal Child App', () => {
  beforeEach(() => {
    // Mock states endpoint
    axios.get.mockImplementation((url) => {
      if (url.includes('/states')) {
        return Promise.resolve({
          data: ['AL', 'TX', 'CA', 'NY']
        });
      }
      return Promise.reject(new Error('Not found'));
    });

    // Mock marginal child endpoint
    axios.post.mockImplementation((url, data) => {
      if (url.includes('/marginal_child')) {
        return Promise.resolve({
          data: [
            { income: 0, num_children: 1, marginal_benefit: 3000, net_income: 10000 },
            { income: 0, num_children: 2, marginal_benefit: 5000, net_income: 15000 },
            { income: 10000, num_children: 1, marginal_benefit: 2500, net_income: 12500 },
            { income: 10000, num_children: 2, marginal_benefit: 4500, net_income: 17000 }
          ]
        });
      }
      return Promise.reject(new Error('Not found'));
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders header with PolicyEngine branding', () => {
    render(<App />);
    expect(screen.getByText('The Marginal Child')).toBeInTheDocument();
    expect(screen.getByText('Powered by PolicyEngine')).toBeInTheDocument();
  });

  test('renders household configuration section', () => {
    render(<App />);
    expect(screen.getByText('Household Configuration')).toBeInTheDocument();
  });

  test('loads states on mount', async () => {
    render(<App />);

    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith(expect.stringContaining('/states'));
    });
  });

  test('automatically calculates marginal child benefits on load', async () => {
    render(<App />);

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining('/marginal_child'),
        expect.any(Object)
      );
    }, { timeout: 3000 });
  });

  test('displays chart when data is loaded', async () => {
    render(<App />);

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalled();
    }, { timeout: 3000 });

    // The chart should be rendered after data loads
    await waitFor(() => {
      const chartTitle = screen.queryByText(/Net Income Change/);
      expect(chartTitle).toBeInTheDocument();
    });
  });

  test('shows only marital status and state inputs', () => {
    render(<App />);

    // Should have marital status dropdown
    expect(screen.getByLabelText(/Marital Status/)).toBeInTheDocument();

    // Should have state dropdown
    expect(screen.getByLabelText(/State/)).toBeInTheDocument();

    // Should NOT have number of children or income inputs
    expect(screen.queryByLabelText(/Number of Children/)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/Employment Income/)).not.toBeInTheDocument();
  });

  test('calculate button triggers API call', async () => {
    render(<App />);

    const button = screen.getByText('Calculate Marginal Child Benefits');
    await userEvent.click(button);

    expect(axios.post).toHaveBeenCalledWith(
      expect.stringContaining('/marginal_child'),
      expect.objectContaining({
        marital_status: 'single',
        state: 'TX'
      })
    );
  });

  test('handles API errors gracefully', async () => {
    axios.post.mockRejectedValueOnce(new Error('API Error'));

    render(<App />);

    const button = screen.getByText('Calculate Marginal Child Benefits');
    await userEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(/Failed to calculate/)).toBeInTheDocument();
    });
  });
});