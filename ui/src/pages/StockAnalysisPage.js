import React, { useState, useEffect } from 'react';
import { 
  Typography, 
  Box, 
  Toolbar, 
  TextField, 
  Button, 
  Grid, 
  Paper, 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem, 
  Card, 
  CardContent, 
  CardMedia,
  Divider,
  CircularProgress,
  Autocomplete,
  Alert
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import dayjs from 'dayjs';

const StockAnalysisPage = ({ style }) => {
  // State variables
  const [stocks, setStocks] = useState([]);
  const [selectedStock, setSelectedStock] = useState('');
  const [selectedIndex, setSelectedIndex] = useState('^IXIC'); // Default to NASDAQ
  const [startDate, setStartDate] = useState(dayjs().subtract(1, 'year'));
  const [endDate, setEndDate] = useState(dayjs());
  const [stockInput, setStockInput] = useState('');
  const [updateDays, setUpdateDays] = useState(60);
  const [loading, setLoading] = useState(false);
  const [updateLoading, setUpdateLoading] = useState(false);
  const [error, setError] = useState('');
  const [volatilityData, setVolatilityData] = useState(null);
  const [correlationData, setCorrelationData] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');

  // Fetch tickers when component mounts
  useEffect(() => {
    fetchTickers();
  }, []);

  // Fetch all available tickers from the API
  const fetchTickers = async () => {
    try {
      const response = await fetch('http://localhost:8000/tickers');
      const data = await response.json();
      setStocks(data.tickers.map(ticker => ticker.ticker));
    } catch (err) {
      setError('Failed to fetch tickers. Please try again later.');
      console.error('Error fetching tickers:', err);
    }
  };

  // Handle stock update
  const handleUpdateStocks = async () => {
    if (!stockInput) {
      setError('Please enter at least one stock symbol');
      return;
    }

    setUpdateLoading(true);
    setError('');
    setSuccessMessage('');

    try {
      const response = await fetch('http://localhost:8000/update_stock_data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symbols: stockInput,
          index: selectedIndex,
          days: updateDays
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setSuccessMessage(`Successfully updated stock data: ${data.message}`);
      // Refresh ticker list after update
      fetchTickers();
    } catch (err) {
      setError(`Failed to update stock data: ${err.message}`);
      console.error('Error updating stocks:', err);
    } finally {
      setUpdateLoading(false);
    }
  };

  // Handle volatility analysis
  const handleVolatilityAnalysis = async () => {
    if (!selectedStock) {
      setError('Please select a stock symbol');
      return;
    }

    setLoading(true);
    setError('');
    setVolatilityData(null);

    try {
      const formattedStartDate = startDate.format('YYYY-MM-DD');
      const formattedEndDate = endDate.format('YYYY-MM-DD');
      
      const response = await fetch(
        `http://localhost:8000/stock_volatility?symbol=${selectedStock}&start_date=${formattedStartDate}&end_date=${formattedEndDate}`
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setVolatilityData(data);
    } catch (err) {
      setError(`Failed to fetch volatility data: ${err.message}`);
      console.error('Error fetching volatility:', err);
    } finally {
      setLoading(false);
    }
  };

  // Handle correlation analysis
  const handleCorrelationAnalysis = async () => {
    if (!selectedStock) {
      setError('Please select a stock symbol');
      return;
    }

    setLoading(true);
    setError('');
    setCorrelationData(null);

    try {
      const formattedStartDate = startDate.format('YYYY-MM-DD');
      const formattedEndDate = endDate.format('YYYY-MM-DD');
      
      const response = await fetch(
        `http://localhost:8000/stock_correlation?symbol=${selectedStock}&index=${selectedIndex}&start_date=${formattedStartDate}&end_date=${formattedEndDate}`
      );

      if (!response.ok) {
        // Parse error message from response if possible
        const errorData = await response.json().catch(() => null);
        const errorMessage = errorData?.detail || `HTTP error! status: ${response.status}`;
        
        if (response.status === 404) {
          throw new Error(`No data found for ${selectedStock} or ${selectedIndex} in the selected date range. Please update stock data first.`);
        } else {
          throw new Error(errorMessage);
        }
      }

      const data = await response.json();
      setCorrelationData(data);
    } catch (err) {
      setError(`Failed to fetch correlation data: ${err.message}`);
      console.error('Error fetching correlation:', err);
    } finally {
      setLoading(false);
    }
  };

  // Add a debug function to check if index data exists
  const checkIndexData = async () => {
    setError('');
    setSuccessMessage('');
    try {
      const formattedStartDate = startDate.format('YYYY-MM-DD');
      const formattedEndDate = endDate.format('YYYY-MM-DD');
      
      // Make a GET request to check if the index data exists
      const response = await fetch(
        `http://localhost:8000/stock_volatility?symbol=${selectedIndex}&start_date=${formattedStartDate}&end_date=${formattedEndDate}`
      );
      
      if (!response.ok) {
        // If 404, means the index data doesn't exist
        if (response.status === 404) {
          setError(`Index data for ${selectedIndex} not found in database. Try updating it again.`);
        } else {
          const errorData = await response.json().catch(() => null);
          setError(`Error checking index data: ${errorData?.detail || response.statusText}`);
        }
      } else {
        const data = await response.json();
        setSuccessMessage(`Index data exists for ${selectedIndex} with ${data.trading_days} trading days.`);
      }
    } catch (err) {
      setError(`Failed to check index data: ${err.message}`);
    }
  };

  // Add a button to specifically update only the index
  const updateIndexData = async () => {
    setUpdateLoading(true);
    setError('');
    setSuccessMessage('');
    
    try {
      const response = await fetch('http://localhost:8000/update_stock_data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symbols: selectedIndex,
          index: null,
          days: updateDays
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setSuccessMessage(`Successfully updated index data: ${data.message}`);
    } catch (err) {
      setError(`Failed to update index data: ${err.message}`);
    } finally {
      setUpdateLoading(false);
    }
  };

  // Index options
  const indices = [
    { value: '^IXIC', label: 'NASDAQ Composite' },
    { value: '^GSPC', label: 'S&P 500' },
    { value: '^DJI', label: 'Dow Jones Industrial Average' },
    { value: '^RUT', label: 'Russell 2000' }
  ];

  return (
    <Box component="main" sx={style}>
      <Toolbar /> {/* This aligns the content below the AppBar */}
      
      <Typography variant="h4" gutterBottom>
        Stock Analysis Tools
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {successMessage && <Alert severity="success" sx={{ mb: 2 }}>{successMessage}</Alert>}

      {/* Stock Data Update Section */}
      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <Typography variant="h5" gutterBottom>
          Update Stock Data
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="Stock Symbols (comma-separated)"
              value={stockInput}
              onChange={(e) => setStockInput(e.target.value)}
              placeholder="AAPL,MSFT,GOOGL"
              margin="normal"
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <FormControl fullWidth margin="normal">
              <InputLabel>Market Index</InputLabel>
              <Select
                value={selectedIndex}
                onChange={(e) => setSelectedIndex(e.target.value)}
                label="Market Index"
              >
                {indices.map((index) => (
                  <MenuItem key={index.value} value={index.value}>
                    {index.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={2}>
            <TextField
              fullWidth
              label="Days of History"
              type="number"
              value={updateDays}
              onChange={(e) => setUpdateDays(Number(e.target.value))}
              margin="normal"
              InputProps={{ inputProps: { min: 1, max: 1000 } }}
            />
          </Grid>
          <Grid item xs={12} sm={2}>
            <Button
              variant="contained"
              color="primary"
              onClick={handleUpdateStocks}
              disabled={updateLoading}
              sx={{ mt: 3 }}
              fullWidth
            >
              {updateLoading ? <CircularProgress size={24} /> : 'Update Data'}
            </Button>
          </Grid>
          <Grid item xs={12} sm={2}>
            <Button
              variant="outlined"
              color="secondary"
              onClick={updateIndexData}
              disabled={updateLoading}
              sx={{ mt: 3, ml: 2 }}
            >
              Update Index Only
            </Button>
          </Grid>
          <Grid item xs={12} sm={2}>
            <Button
              variant="outlined"
              color="info"
              onClick={checkIndexData}
              disabled={updateLoading}
              sx={{ mt: 3, ml: 2 }}
            >
              Check Index Data
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Analysis Form Section */}
      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <Typography variant="h5" gutterBottom>
          Analysis Parameters
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} sm={4}>
            <Autocomplete
              options={stocks}
              value={selectedStock}
              onChange={(_, newValue) => setSelectedStock(newValue)}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Select Stock"
                  margin="normal"
                  fullWidth
                />
              )}
            />
          </Grid>
          <Grid item xs={12} sm={3}>
            <DatePicker
              label="Start Date"
              value={startDate}
              onChange={(newValue) => setStartDate(newValue)}
              slotProps={{ textField: { margin: 'normal', fullWidth: true } }}
            />
          </Grid>
          <Grid item xs={12} sm={3}>
            <DatePicker
              label="End Date"
              value={endDate}
              onChange={(newValue) => setEndDate(newValue)}
              slotProps={{ textField: { margin: 'normal', fullWidth: true } }}
            />
          </Grid>
          <Grid item xs={12} sm={2}>
            <FormControl fullWidth margin="normal">
              <InputLabel>Index (for Correlation)</InputLabel>
              <Select
                value={selectedIndex}
                onChange={(e) => setSelectedIndex(e.target.value)}
                label="Index (for Correlation)"
              >
                {indices.map((index) => (
                  <MenuItem key={index.value} value={index.value}>
                    {index.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        <Grid container spacing={2} sx={{ mt: 2 }}>
          <Grid item xs={6}>
            <Button
              variant="contained"
              color="primary"
              onClick={handleVolatilityAnalysis}
              disabled={loading || !selectedStock}
              fullWidth
            >
              Run Volatility Analysis
            </Button>
          </Grid>
          <Grid item xs={6}>
            <Button
              variant="contained"
              color="secondary"
              onClick={handleCorrelationAnalysis}
              disabled={loading || !selectedStock}
              fullWidth
            >
              Run Correlation Analysis
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Results Section */}
      <Grid container spacing={3}>
        {/* Volatility Results */}
        {volatilityData && (
          <Grid item xs={12} md={6}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Volatility Analysis: {volatilityData.stock_symbol}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Period: {volatilityData.start_date} to {volatilityData.end_date}
                </Typography>
                <Divider sx={{ my: 1 }} />
                <Typography variant="body2">
                  <strong>Daily Volatility:</strong> {volatilityData.daily_volatility.toFixed(2)}%
                </Typography>
                <Typography variant="body2">
                  <strong>Mean Daily Return:</strong> {volatilityData.mean_daily_return.toFixed(2)}%
                </Typography>
                <Typography variant="body2">
                  <strong>Min Daily Return:</strong> {volatilityData.min_daily_return.toFixed(2)}%
                </Typography>
                <Typography variant="body2">
                  <strong>Max Daily Return:</strong> {volatilityData.max_daily_return.toFixed(2)}%
                </Typography>
                <Typography variant="body2">
                  <strong>Trading Days:</strong> {volatilityData.trading_days}
                </Typography>
              </CardContent>
              {volatilityData.plot && (
                <CardMedia
                  component="img"
                  sx={{ maxHeight: 300, objectFit: 'contain', p: 2 }}
                  image={`data:image/png;base64,${volatilityData.plot}`}
                  alt="Volatility Distribution"
                />
              )}
            </Card>
          </Grid>
        )}

        {/* Correlation Results */}
        {correlationData && (
          <Grid item xs={12} md={6}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Correlation Analysis: {correlationData.stock_symbol} vs {correlationData.index}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Period: {correlationData.start_date} to {correlationData.end_date}
                </Typography>
                <Divider sx={{ my: 1 }} />
                <Typography variant="body2">
                  <strong>Correlation:</strong> {correlationData.correlation.toFixed(3)}
                </Typography>
                <Typography variant="body2">
                  <strong>Beta:</strong> {correlationData.beta.toFixed(3)}
                </Typography>
                <Typography variant="body2">
                  <strong>Trading Days:</strong> {correlationData.trading_days}
                </Typography>
              </CardContent>
              {correlationData.plot && (
                <CardMedia
                  component="img"
                  sx={{ maxHeight: 300, objectFit: 'contain', p: 2 }}
                  image={`data:image/png;base64,${correlationData.plot}`}
                  alt="Correlation Scatter Plot"
                />
              )}
            </Card>
          </Grid>
        )}
      </Grid>

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      )}
    </Box>
  );
};
  
export default StockAnalysisPage; 