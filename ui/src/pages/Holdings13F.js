import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  TextField, 
  Button, 
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Alert,
} from '@mui/material';
import { update13FData, getHoldings, getTickers } from '../modules/api13F';

const Holdings13F = () => {
  const [selectedQuarter, setSelectedQuarter] = useState('');
  const [selectedTicker, setSelectedTicker] = useState('');
  const [tickers, setTickers] = useState([]);
  const [holdings, setHoldings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Generate quarters for dropdown (current quarter and previous 3)
  const getQuarterOptions = () => {
    const quarters = [];
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth();
    
    // Get the current quarter (0-3)
    const currentQuarter = Math.floor(month / 3);
    
    // Generate the last 4 quarters
    for (let i = 0; i < 4; i++) {
      const targetQuarter = (currentQuarter - i + 4) % 4; // Ensure positive number
      const yearOffset = Math.floor((currentQuarter - i) / 4); // Calculate year offset
      const targetYear = year + yearOffset;
      
      // Map quarter to end date
      let monthEnd, dayEnd;
      switch(targetQuarter) {
        case 0: // Q1
          monthEnd = '03';
          dayEnd = '31';
          break;
        case 1: // Q2
          monthEnd = '06';
          dayEnd = '30';
          break;
        case 2: // Q3
          monthEnd = '09';
          dayEnd = '30';
          break;
        case 3: // Q4
          monthEnd = '12';
          dayEnd = '31';
          break;
      }
      
      quarters.push(`${monthEnd}-${dayEnd}-${targetYear}`);
    }
    
    return quarters;
  };

  useEffect(() => {
    const fetchTickers = async () => {
      try {
        const fetchedTickers = await getTickers();
        setTickers(fetchedTickers);
      } catch (err) {
        setError('Failed to fetch tickers');
      }
    };
    fetchTickers();
  }, []);

  const handleUpdateData = async () => {
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      await update13FData(selectedQuarter, true);
      setSuccess('13F data updated successfully');
    } catch (err) {
      setError('Failed to update 13F data');
    } finally {
      setLoading(false);
    }
  };

  const handleViewHoldings = async () => {
    if (!selectedTicker) {
      setError('Please select a ticker');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const data = await getHoldings(selectedTicker, selectedQuarter);
      setHoldings(data.holdings);
    } catch (err) {
      setError('Failed to fetch holdings');
      setHoldings([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          13F Holdings Manager
        </Typography>

        <Box sx={{ mb: 4 }}>
          <FormControl sx={{ mr: 2, minWidth: 200 }}>
            <InputLabel>Quarter</InputLabel>
            <Select
              value={selectedQuarter}
              label="Quarter"
              onChange={(e) => setSelectedQuarter(e.target.value)}
            >
              {getQuarterOptions().map((quarter) => (
                <MenuItem key={quarter} value={quarter}>
                  {quarter}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Button
            variant="contained"
            onClick={handleUpdateData}
            disabled={loading}
            sx={{ mr: 2 }}
          >
            {loading ? <CircularProgress size={24} /> : 'Update 13F Data'}
          </Button>
        </Box>

        <Box sx={{ mb: 4 }}>
          <FormControl sx={{ mr: 2, minWidth: 200 }}>
            <InputLabel>Company</InputLabel>
            <Select
              value={selectedTicker}
              label="Company"
              onChange={(e) => setSelectedTicker(e.target.value)}
            >
              {tickers.map((company) => (
                <MenuItem key={company.ticker} value={company.ticker}>
                  {company.ticker} - {company.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Button
            variant="contained"
            onClick={handleViewHoldings}
            disabled={loading || !selectedTicker}
          >
            View Holdings
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {success}
          </Alert>
        )}

        {holdings.length > 0 && (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Institution</TableCell>
                  <TableCell align="right">Shares</TableCell>
                  <TableCell>Filing Date</TableCell>
                  <TableCell>Quarter</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {holdings.map((holding, index) => (
                  <TableRow key={index}>
                    <TableCell>{holding.holder_name}</TableCell>
                    <TableCell align="right">
                      {new Intl.NumberFormat().format(holding.shares)}
                    </TableCell>
                    <TableCell>{holding.filing_date}</TableCell>
                    <TableCell>{holding.quarter}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Box>
    </Container>
  );
};

export default Holdings13F;