import React, { useState, useEffect } from 'react';
import { Typography, Box, Toolbar, Button } from '@mui/material';
import StockListDropdown from '../modules/StockListDropdown';
import CalendarDatePicker from '../modules/CalendarDatePicker';
import dayjs from 'dayjs';
import EnterNameForm from '../modules/EnterNameForm';

const apiServerUrl = process.env.REACT_APP_API_SERVER_URL;

const CreateUniversePage = ({ style }) => {
  const [name, setName] = useState("");
  const [tickers, setTickers] = useState([]);
  const [beginDate, setBeginDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  const [error, setError] = useState(null);

  const handleBeginChange = (newValue) => {
    setBeginDate(newValue); // Update the begin date
  };

  const handleEndChange = (newValue) => {
    setEndDate(newValue); // Update the end date
  };

  const handleOnClick = () => {
    // Validate all fields
    if (!name.trim()) {
      setError("Universe name is required.");
      return;
    }

    if (tickers.length === 0) {
      setError("At least one stock must be selected.");
      return;
    }

    if (!beginDate || !endDate) {
      setError("Both begin and end dates are required.");
      return;
    }

    if (dayjs(beginDate).isAfter(dayjs(endDate))) {
      setError("Start date must be earlier than end date.");
      return;
    }

    // Clear previous error if all validations pass
    setError(null);

    const postData = {
      name: name,
      tickers: Array.isArray(tickers) ? tickers : [],
      date_range: `[${beginDate.format('YYYY-MM-DD')}, ${endDate.format('YYYY-MM-DD')}]`,
    };

    // Make the POST request
    fetch(`${apiServerUrl}/create_universe`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(postData)
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      console.log('Success:', data);
      // Optionally handle success (e.g., navigate to another page or clear form)
    })
    .catch(error => {
      console.error('Error:', error);
    });
  };

  return (
    <Box component="main" sx={style}>
      <Toolbar /> {/* This aligns the content below the AppBar */}
      <Typography variant="h6">
        1. Universe Name:
      </Typography>

      <Box sx={{ mt: 2, mb: 2 }}>
        <EnterNameForm name={name} setName={setName} />
      </Box>

      <Typography variant="h6">
        2. Select stocks:
      </Typography>

      <Box sx={{ mb: 2, mt: 2 }}>
        <StockListDropdown tickers={tickers} setTickers={setTickers} />
      </Box>

      <Typography variant="h6">
        3. Select date range:
      </Typography>

      <Box sx={{ mb: 2, mt: 2 }}>
        <CalendarDatePicker date={beginDate} setDateHandler={handleBeginChange} label={"Begin Date"} />
        <CalendarDatePicker date={endDate} setDateHandler={handleEndChange} label={"End Date"} />
      </Box>

      {/* Display error message if any validation fails */}
      {error && (
        <Typography variant="body2" color="error" sx={{ mt: 2 }}>
          {error}
        </Typography>
      )}

      <Button variant="contained" onClick={handleOnClick}>
        Save Universe
      </Button>
    </Box>
  );
};

export default CreateUniversePage;