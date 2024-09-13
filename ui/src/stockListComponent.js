import React, { useEffect, useState } from 'react';
import TextField from '@mui/material/TextField';
import { Autocomplete } from '@mui/material';

const apiServerUrl = process.env.REACT_APP_API_SERVER_URL;

function StockListComponent() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [tickers, setSelectedTicker] = useState(new Set());
  console.log(JSON.stringify(process.env, null, 2));

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
    sx={{ width: 300 }}
    renderInput={(params) => <TextField {...params} label="Stocks" />}
    />
  );
}

export default StockListComponent;