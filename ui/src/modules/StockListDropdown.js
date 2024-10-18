import React, { useEffect, useState } from 'react';
import TextField from '@mui/material/TextField';
import { Autocomplete, Chip, Box } from '@mui/material';

const apiServerUrl = process.env.REACT_APP_API_SERVER_URL;

export default function StockListDropdown({ tickers, setTickers }) {
  const [data, setData] = useState([]); // Store fetched stock data
  const [error, setError] = useState(null);

  const handleChange = (event, newValue) => {
    setTickers(newValue);
    // console.log('Tickers: ', newValue);
  };

  useEffect(() => {
    // Make HTTP GET request when the component mounts
    const url = `${apiServerUrl}/tickers`;
    fetch(url)
      .then(response => {
        if (!response.ok) {
          throw new Error('Unable to get stock list');
        }
        return response.json();
      })
      .then(data => {
        const stocks = data.tickers.map(stock => stock.ticker);
        setData(stocks.sort());
      })
      .catch(error => setError(error));
  }, []);

  return (
    <Box sx={{ width: 400}}>
      {/* Autocomplete Dropdown */}
      <Autocomplete
        multiple
        value={tickers} // Use tickers from props
        onChange={handleChange}
        disablePortal
        id="tickers-autocomplete"
        options={data}
        getOptionLabel={(option) => option} // Get ticker label
        renderTags={(selected, getTagProps) =>
          selected.map((option, index) => (
            <Chip 
              key={option} 
              label={option} 
              {...getTagProps({ index })} 
            />
          ))
        }
        sx={{
          width: '100%',
          mb: 2, // Adjust margin for spacing
        }}
        renderInput={(params) => <TextField {...params} label="Select Stocks" />}
      />

      {/* Displaying Selected Tickers
      <TextField
        label="Selected Tickers"
        variant="outlined"
        fullWidth
        multiline
        value={Array.isArray(tickers) ? tickers.join(', ') : ''} // Ensure tickers is an array before joining
      />
      */}
    </Box>
  );
}