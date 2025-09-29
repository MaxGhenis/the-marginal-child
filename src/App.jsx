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
  Slider,
  FormControlLabel,
  Switch,
  Tabs,
  Tab,
  CircularProgress,
  Alert
} from '@mui/material';
import Plot from 'react-plotly.js';
import axios from 'axios';
import './App.css';

const API_URL = 'http://localhost:5000/api';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div hidden={value !== index} {...other}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function App() {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Input parameters
  const [params, setParams] = useState({
    marital_status: 'single',
    num_children: 0,
    state: 'TX',
    employment_income: 30000,
    spouse_income: 0,
    parent1_age: 30,
    parent2_age: 30,
    housing_cost: 1000,
    childcare_cost: 500,
    income_min: 0,
    income_max: 150000,
    income_step: 2000,
    max_children: 4,
  });

  const [childAges, setChildAges] = useState([5, 5, 5, 5, 5]);

  const [cliffData, setCliffData] = useState(null);
  const [marginalChildData, setMarginalChildData] = useState(null);
  const [currentBenefits, setCurrentBenefits] = useState(null);
  const [states, setStates] = useState([]);

  useEffect(() => {
    fetchStates();
  }, []);

  const fetchStates = async () => {
    try {
      const response = await axios.get(`${API_URL}/states`);
      setStates(response.data);
    } catch (err) {
      console.error('Failed to fetch states:', err);
    }
  };

  const calculateCurrentBenefits = async () => {
    setLoading(true);
    setError(null);
    try {
      const requestParams = {
        ...params,
        ...childAges.reduce((acc, age, index) => {
          if (index < params.num_children) {
            acc[`child${index + 1}_age`] = age;
          }
          return acc;
        }, {})
      };

      const response = await axios.post(`${API_URL}/calculate`, requestParams);
      setCurrentBenefits(response.data);
    } catch (err) {
      setError('Failed to calculate benefits. Make sure the API is running.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const calculateCliff = async () => {
    setLoading(true);
    setError(null);
    try {
      const requestParams = {
        ...params,
        ...childAges.reduce((acc, age, index) => {
          if (index < params.num_children) {
            acc[`child${index + 1}_age`] = age;
          }
          return acc;
        }, {})
      };

      const response = await axios.post(`${API_URL}/calculate_cliff`, requestParams);
      setCliffData(response.data);
    } catch (err) {
      setError('Failed to calculate benefit cliff. Make sure the API is running.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const calculateMarginalChild = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`${API_URL}/marginal_child`, params);
      setMarginalChildData(response.data);
    } catch (err) {
      setError('Failed to calculate marginal child benefits. Make sure the API is running.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleParamChange = (key, value) => {
    setParams(prev => ({ ...prev, [key]: value }));
  };

  const handleChildAgeChange = (index, age) => {
    setChildAges(prev => {
      const newAges = [...prev];
      newAges[index] = age;
      return newAges;
    });
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const renderCliffChart = () => {
    if (!cliffData) return null;

    const traces = [
      {
        x: cliffData.map(d => d.income),
        y: cliffData.map(d => d.snap),
        name: 'SNAP',
        type: 'scatter',
        mode: 'lines',
        stackgroup: 'one',
      },
      {
        x: cliffData.map(d => d.income),
        y: cliffData.map(d => d.wic),
        name: 'WIC',
        type: 'scatter',
        mode: 'lines',
        stackgroup: 'one',
      },
      {
        x: cliffData.map(d => d.income),
        y: cliffData.map(d => d.medicaid),
        name: 'Medicaid',
        type: 'scatter',
        mode: 'lines',
        stackgroup: 'one',
      },
      {
        x: cliffData.map(d => d.income),
        y: cliffData.map(d => d.chip),
        name: 'CHIP',
        type: 'scatter',
        mode: 'lines',
        stackgroup: 'one',
      },
      {
        x: cliffData.map(d => d.income),
        y: cliffData.map(d => d.premium_tax_credit),
        name: 'PTC',
        type: 'scatter',
        mode: 'lines',
        stackgroup: 'one',
      },
      {
        x: cliffData.map(d => d.income),
        y: cliffData.map(d => d.eitc),
        name: 'EITC',
        type: 'scatter',
        mode: 'lines',
        stackgroup: 'one',
      },
      {
        x: cliffData.map(d => d.income),
        y: cliffData.map(d => d.ctc),
        name: 'CTC',
        type: 'scatter',
        mode: 'lines',
        stackgroup: 'one',
      },
    ];

    const layout = {
      title: 'Benefit Cliff Analysis',
      xaxis: { title: 'Employment Income ($)', tickformat: '$,.0f' },
      yaxis: { title: 'Annual Benefit Amount ($)', tickformat: '$,.0f' },
      hovermode: 'x unified',
    };

    return <Plot data={traces} layout={layout} style={{ width: '100%', height: '500px' }} />;
  };

  const renderNetIncomeChart = () => {
    if (!cliffData) return null;

    const traces = [
      {
        x: cliffData.map(d => d.income),
        y: cliffData.map(d => d.income),
        name: 'Employment Income',
        type: 'scatter',
        mode: 'lines',
      },
      {
        x: cliffData.map(d => d.income),
        y: cliffData.map(d => d.net_income),
        name: 'Net Income (with benefits)',
        type: 'scatter',
        mode: 'lines',
      },
    ];

    const layout = {
      title: 'Net Income vs Employment Income',
      xaxis: { title: 'Employment Income ($)', tickformat: '$,.0f' },
      yaxis: { title: 'Income ($)', tickformat: '$,.0f' },
      hovermode: 'x unified',
    };

    return <Plot data={traces} layout={layout} style={{ width: '100%', height: '500px' }} />;
  };

  const renderMarginalChildChart = () => {
    if (!marginalChildData) return null;

    const childNumbers = [...new Set(marginalChildData.map(d => d.num_children))].sort();
    const colors = ['#D1E5F0', '#92C5DE', '#2166AC', '#053061'];

    const traces = childNumbers.map((childNum, index) => {
      const data = marginalChildData.filter(d => d.num_children === childNum);
      return {
        x: data.map(d => d.income),
        y: data.map(d => d.marginal_benefit),
        name: `Child ${childNum}`,
        type: 'scatter',
        mode: 'lines',
        line: { color: colors[index % colors.length], width: 2 },
      };
    });

    const layout = {
      title: 'Marginal Benefit per Additional Child',
      xaxis: { title: 'Employment Income ($)', tickformat: '$,.0f' },
      yaxis: { title: 'Marginal Benefit ($)', tickformat: '$,.0f' },
      hovermode: 'x unified',
    };

    return <Plot data={traces} layout={layout} style={{ width: '100%', height: '500px' }} />;
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ my: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom align="center">
          The Marginal Child
        </Typography>
        <Typography variant="subtitle1" align="center" color="text.secondary" gutterBottom>
          Analyze how benefits change with each additional child using PolicyEngine
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}

        <Paper sx={{ mt: 3, p: 3 }}>
          <Typography variant="h5" gutterBottom>
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

            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                label="Number of Children"
                type="number"
                value={params.num_children}
                onChange={(e) => handleParamChange('num_children', parseInt(e.target.value))}
                inputProps={{ min: 0, max: 10 }}
              />
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                label="Employment Income"
                type="number"
                value={params.employment_income}
                onChange={(e) => handleParamChange('employment_income', parseInt(e.target.value))}
                inputProps={{ min: 0 }}
              />
            </Grid>

            {params.marital_status === 'married' && (
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  fullWidth
                  label="Spouse Income"
                  type="number"
                  value={params.spouse_income}
                  onChange={(e) => handleParamChange('spouse_income', parseInt(e.target.value))}
                  inputProps={{ min: 0 }}
                />
              </Grid>
            )}

            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                label="Monthly Housing Cost"
                type="number"
                value={params.housing_cost}
                onChange={(e) => handleParamChange('housing_cost', parseInt(e.target.value))}
                inputProps={{ min: 0 }}
              />
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                label="Monthly Childcare Cost"
                type="number"
                value={params.childcare_cost}
                onChange={(e) => handleParamChange('childcare_cost', parseInt(e.target.value))}
                inputProps={{ min: 0 }}
              />
            </Grid>
          </Grid>

          {params.num_children > 0 && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" gutterBottom>
                Children Ages
              </Typography>
              <Grid container spacing={2}>
                {Array.from({ length: params.num_children }).map((_, index) => (
                  <Grid item xs={6} sm={3} md={2} key={index}>
                    <TextField
                      fullWidth
                      label={`Child ${index + 1} Age`}
                      type="number"
                      value={childAges[index]}
                      onChange={(e) => handleChildAgeChange(index, parseInt(e.target.value))}
                      inputProps={{ min: 0, max: 18 }}
                    />
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}

          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              Analysis Parameters
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Income Range Min"
                  type="number"
                  value={params.income_min}
                  onChange={(e) => handleParamChange('income_min', parseInt(e.target.value))}
                  inputProps={{ min: 0 }}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Income Range Max"
                  type="number"
                  value={params.income_max}
                  onChange={(e) => handleParamChange('income_max', parseInt(e.target.value))}
                  inputProps={{ min: 0 }}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Income Step"
                  type="number"
                  value={params.income_step}
                  onChange={(e) => handleParamChange('income_step', parseInt(e.target.value))}
                  inputProps={{ min: 100 }}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Max Children for Marginal Analysis"
                  type="number"
                  value={params.max_children}
                  onChange={(e) => handleParamChange('max_children', parseInt(e.target.value))}
                  inputProps={{ min: 1, max: 10 }}
                />
              </Grid>
            </Grid>
          </Box>

          <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
            <Button
              variant="contained"
              color="primary"
              onClick={calculateCurrentBenefits}
              disabled={loading}
            >
              Calculate Current Benefits
            </Button>
            <Button
              variant="contained"
              color="secondary"
              onClick={calculateCliff}
              disabled={loading}
            >
              Analyze Benefit Cliff
            </Button>
            <Button
              variant="contained"
              color="success"
              onClick={calculateMarginalChild}
              disabled={loading}
            >
              Analyze Marginal Child
            </Button>
          </Box>
        </Paper>

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
            <CircularProgress />
          </Box>
        )}

        {currentBenefits && (
          <Paper sx={{ mt: 3, p: 3 }}>
            <Typography variant="h5" gutterBottom>
              Current Benefits at {formatCurrency(params.employment_income)}
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6} sm={4} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      SNAP
                    </Typography>
                    <Typography variant="h6">
                      {formatCurrency(currentBenefits.snap)}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6} sm={4} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      WIC
                    </Typography>
                    <Typography variant="h6">
                      {formatCurrency(currentBenefits.wic)}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6} sm={4} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      Medicaid
                    </Typography>
                    <Typography variant="h6">
                      {formatCurrency(currentBenefits.medicaid)}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6} sm={4} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      CHIP
                    </Typography>
                    <Typography variant="h6">
                      {formatCurrency(currentBenefits.chip)}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6} sm={4} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      Premium Tax Credit
                    </Typography>
                    <Typography variant="h6">
                      {formatCurrency(currentBenefits.premium_tax_credit)}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6} sm={4} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      EITC
                    </Typography>
                    <Typography variant="h6">
                      {formatCurrency(currentBenefits.eitc)}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6} sm={4} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      Child Tax Credit
                    </Typography>
                    <Typography variant="h6">
                      {formatCurrency(currentBenefits.ctc)}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6} sm={4} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      Total Benefits
                    </Typography>
                    <Typography variant="h6" color="primary">
                      {formatCurrency(currentBenefits.total_benefits)}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6} sm={4} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      Net Income
                    </Typography>
                    <Typography variant="h6" color="success.main">
                      {formatCurrency(currentBenefits.net_income)}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6} sm={4} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      Marginal Tax Rate
                    </Typography>
                    <Typography variant="h6">
                      {(currentBenefits.marginal_tax_rate * 100).toFixed(1)}%
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Paper>
        )}

        <Box sx={{ mt: 3 }}>
          <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
            <Tab label="Benefit Cliff" />
            <Tab label="Net Income" />
            <Tab label="Marginal Child" />
          </Tabs>

          <TabPanel value={tabValue} index={0}>
            {renderCliffChart()}
          </TabPanel>
          <TabPanel value={tabValue} index={1}>
            {renderNetIncomeChart()}
          </TabPanel>
          <TabPanel value={tabValue} index={2}>
            {renderMarginalChildChart()}
          </TabPanel>
        </Box>
      </Box>
    </Container>
  );
}

export default App
