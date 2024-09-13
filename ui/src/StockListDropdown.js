import React, { useEffect, useState } from 'react';
import TextField from '@mui/material/TextField';
import { Autocomplete } from '@mui/material';
import './stockListDropdown.css';

const apiServerUrl = process.env.REACT_APP_API_SERVER_URL;

function StockListDropdown() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [tickers, setSelectedTicker] = useState(new Set());

  const SxProps = {
    width: '300px',         // Set the width of the Autocomplete component
    backgroundColor: '#f5f5f5', // Set background color
    borderRadius: '4px',    // Set border radius
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)', // Add a subtle shadow
    '& .MuiAutocomplete-input': { // Style the input element
      padding: '8px 16px',  // Add padding to the input field
    },
    '& .MuiAutocomplete-option': { // Style the options in the dropdown
      fontSize: '14px',     // Set font size
      '&:hover': {          // Add hover effect
        backgroundColor: '#e0e0e0',
      },
    },
  };

  const handleChange = (event, selectedTicker) => {
    const updatedSet = new Set(tickers);

    if (selectedTicker) {
      updatedSet.add(selectedTicker);
    }

    setSelectedTicker(updatedSet);
    console.log('Tickers: ', updatedSet);
  };

  useEffect(() => {
    // Make HTTP GET request when the component mounts
    const url = `${apiServerUrl}/tickers`;
    fetch(url)
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        const stocks = [];
        data.tickers.forEach(stock => {
          stocks.push(stock.ticker);
        });
        setData(stocks.sort());
      }
    )
      .catch(error => setError(error));
  }, []);

  return (
    <Autocomplete
    onChange={handleChange}
    disablePortal
    id="demo"
    options={data}
    sx={{
      position: 'absolute',
      left: 500,
      top: '500px', // Adjust top position as needed
      width: 300 // Adjust width as needed
    }}
    renderInput={(params) => <TextField {...params} label="Stocks" />}
    />
  );
}

export default StockListComponent;