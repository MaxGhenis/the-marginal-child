import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Box,
  Paper,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
  ThemeProvider,
  createTheme,
  CssBaseline,
  Chip
} from '@mui/material';
import Plot from 'react-plotly.js';
import axios from 'axios';
import Header from './components/Header';
import { colors } from './styles/colors';
import './App.css';

const API_URL = 'http://localhost:5001/api';

// Create PolicyEngine theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#2C6496', // PolicyEngine Blue
    },
    secondary: {
      main: '#39C6C0', // PolicyEngine Teal
    },
    success: {
      main: '#4CAF50',
    },
    background: {
      default: colors.background.default,
      paper: colors.background.paper,
    },
    text: {
      primary: colors.text.primary,
      secondary: colors.text.secondary,
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h3: {
      fontWeight: 600,
    },
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 500,
    },
    h6: {
      fontWeight: 500,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
          fontWeight: 500,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
  },
});


function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [initialized, setInitialized] = useState(false);

  const [params, setParams] = useState({
    marital_status: 'single',
    state: 'TX',
    spouse_income: 0,
    income_min: 0,
    income_max: 200000,
    income_step: 2500,
  });

  const [marginalChildData, setMarginalChildData] = useState(null);
  const [states, setStates] = useState([]);

  useEffect(() => {
    const init = async () => {
      try {
        // Fetch states first
        const response = await axios.get(`${API_URL}/states`);
        setStates(response.data);

        // Then calculate marginal child
        const calcResponse = await axios.post(`${API_URL}/marginal_child`, params);
        setMarginalChildData(calcResponse.data);
        setInitialized(true);
      } catch (err) {
        console.error('Initialization error:', err);
        setError('Failed to initialize. Please refresh the page.');
      }
    };

    if (!initialized) {
      init();
    }
  }, [initialized]);

  const fetchStates = async () => {
    try {
      const response = await axios.get(`${API_URL}/states`);
      setStates(response.data);
    } catch (err) {
      console.error('Failed to fetch states:', err);
    }
  };


  const calculateMarginalChild = async (overrideParams = null) => {
    // Prevent duplicate calls
    if (loading) return;

    setLoading(true);
    setError(null);
    try {
      const paramsToUse = overrideParams || params;
      console.log('Calling API with params:', paramsToUse);

      const response = await axios.post(`${API_URL}/marginal_child`, paramsToUse);
      console.log('API response:', response.data.length, 'items');

      if (response.data && response.data.length > 0) {
        setMarginalChildData(response.data);
        setError(null);
      } else {
        throw new Error('No data returned from API');
      }
    } catch (err) {
      console.error('API Error details:', err.response || err);
      const errorMessage = err.response?.data?.error ||
                          err.message ||
                          'Failed to calculate marginal child benefits. Make sure the API is running.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleParamChange = (key, value) => {
    const newParams = { ...params, [key]: value };
    setParams(newParams);

    // Auto-recalculate when state or marital status changes
    if (key === 'state' || key === 'marital_status') {
      setTimeout(() => {
        calculateMarginalChild(newParams);
      }, 100);
    }
  };


  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };


  const renderMarginalChildChart = () => {
    if (!marginalChildData) return null;

    const childNumbers = [...new Set(marginalChildData.map(d => d.num_children))].sort();

    const traces = childNumbers.map((childNum, index) => {
      const data = marginalChildData.filter(d => d.num_children === childNum);
      return {
        x: data.map(d => d.income),
        y: data.map(d => d.marginal_benefit),
        name: `Child ${childNum}`,
        type: 'scatter',
        mode: 'lines',
        line: {
          color: colors.chart.gradient[index % colors.chart.gradient.length],
          width: 3
        },
      };
    });

    const layout = {
      title: {
        text: 'Net Income Change from Taxes and Benefits per Additional Child',
        font: { family: 'Roboto, sans-serif', size: 20, color: colors.text.primary }
      },
      xaxis: {
        title: 'Earnings',
        tickformat: '$,.0f',
        font: { family: 'Roboto, sans-serif' }
      },
      yaxis: {
        title: 'Net Income Change for Additional Child',
        tickformat: '$,.0f',
        font: { family: 'Roboto, sans-serif' },
        rangemode: 'tozero'  // Force Y-axis to start at 0
      },
      hovermode: 'x unified',
      paper_bgcolor: colors.background.paper,
      plot_bgcolor: colors.background.paper,
      font: { family: 'Roboto, sans-serif' },
      legend: {
        title: { text: 'Child Number' },
        font: { family: 'Roboto, sans-serif' }
      },
    };

    return <Plot data={traces} layout={layout} style={{ width: '100%', height: '500px' }} />;
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ minHeight: '100vh', backgroundColor: colors.background.default }}>
        <Header />
        <Container maxWidth="xl">
          <Box sx={{ my: 4 }}>
            <Typography
              variant="h6"
              align="center"
              color="text.secondary"
              gutterBottom
              sx={{ mb: 3 }}
            >
              Analyze how government benefits change with each additional child
            </Typography>

            {error && (
              <Alert severity="error" sx={{ mt: 2, mb: 2 }}>
                {error}
              </Alert>
            )}

            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h5" gutterBottom color="primary">
                Household Configuration
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6} md={3}>
                  <FormControl fullWidth>
                    <InputLabel>Marital Status</InputLabel>
                    <Select
                      value={params.marital_status}
                      onChange={(e) => handleParamChange('marital_status', e.target.value)}
                      label="Marital Status"
                    >
                      <MenuItem value="single">Single</MenuItem>
                      <MenuItem value="married">Married</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                  <FormControl fullWidth>
                    <InputLabel>State</InputLabel>
                    <Select
                      value={params.state}
                      onChange={(e) => handleParamChange('state', e.target.value)}
                      label="State"
                    >
                      {states.map(state => (
                        <MenuItem key={state} value={state}>{state}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>


                {params.marital_status === 'married' && (
                  <Grid item xs={12} sm={6} md={3}>
                    <TextField
                      fullWidth
                      label="Spouse Income"
                      type="number"
                      value={params.spouse_income}
                      onChange={(e) => handleParamChange('spouse_income', parseInt(e.target.value) || 0)}
                      inputProps={{ min: 0 }}
                    />
                  </Grid>
                )}
              </Grid>


              <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={calculateMarginalChild}
                  disabled={loading}
                  size="large"
                  sx={{
                    px: 6,
                    py: 1.5,
                    fontSize: '1.1rem',
                  }}
                >
                  Calculate Marginal Child Benefits
                </Button>
              </Box>
            </Paper>

            {loading && (
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
                <CircularProgress />
              </Box>
            )}


            {marginalChildData && (
              <Box sx={{ mt: 3 }}>
                <Paper sx={{ p: 3 }}>
                  {renderMarginalChildChart()}
                </Paper>
              </Box>
            )}
          </Box>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;