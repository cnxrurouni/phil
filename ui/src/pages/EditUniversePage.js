import React, { useState, useEffect } from 'react';
import { Typography, Box, Toolbar, Button } from '@mui/material';
import StockListDropdown from '../modules/StockListDropdown';
import CalendarDatePicker from '../modules/CalendarDatePicker';
import dayjs from 'dayjs';
import EnterNameForm from '../modules/EnterNameForm';
import { useNavigate, useLocation } from 'react-router-dom';

const apiServerUrl = process.env.REACT_APP_API_SERVER_URL;

const EditUniversePage = ({ style }) => {
  const location = useLocation();
  const navigate = useNavigate();

  // Destructure the state passed from the previous page
  const { universe } = location.state || {};

  // Initialize state with default values or fallbacks
  const [name, setName] = useState(universe?.name || '');
  const [tickers, setTickers] = useState(universe?.tickers || []);
  const [beginDate, setBeginDate] = useState(universe?.date_range?.lower ? dayjs(universe.date_range.lower) : null);
  const [endDate, setEndDate] = useState(universe?.date_range?.upper ? dayjs(universe.date_range.upper) : null);
  const [error, setError] = useState(null);

  // Validation for date range
  const validateDates = (begin, end) => {
    if (begin && end && dayjs(begin).isAfter(dayjs(end))) {
      setError("Start date must be earlier than end date.");
    } else {
      setError(null); // Clear error if valid
    }
  };

  // Validate dates whenever beginDate or endDate changes
  useEffect(() => {
    validateDates(beginDate, endDate);
  }, [beginDate, endDate]);

  const handleBeginChange = (newValue) => {
    setBeginDate(newValue); // Update the begin date
  };

  const handleEndChange = (newValue) => {
    setEndDate(newValue); // Update the end date
  };

  const handleOnClick = () => {
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

    setError(null); // Clear previous error if all validations pass

    const putData = {
      name: name,
      tickers: Array.isArray(tickers) ? tickers : [],
      date_range: `[${beginDate.format('YYYY-MM-DD')}, ${endDate.format('YYYY-MM-DD')}]`,
    };

    // Make the PUT request to update the universe
    const url = `${apiServerUrl}/edit_universe/${universe.id}`;
    console.log("url: ", url);
    fetch(url, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(putData)
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      console.log('Success:', data);
      navigate(`/universe/${universe.name}`, { state: { universe: data.universe } });
    })
    .catch(error => {
      console.error('Error:', error);
    });
  };

  return (
    <Box component="main" sx={style}>
      <Toolbar />
      <Typography variant="h6">1. Universe Name:</Typography>

      <Box sx={{ mt: 2, mb: 2 }}>
        <EnterNameForm name={name} setName={setName} />
      </Box>

      <Typography variant="h6">2. Select stocks:</Typography>

      <Box sx={{ mb: 2, mt: 2 }}>
        <StockListDropdown tickers={tickers} setTickers={setTickers} />
      </Box>

      <Typography variant="h6">3. Select date range:</Typography>

      <Box sx={{ mb: 2, mt: 2 }}>
        <CalendarDatePicker date={beginDate} setDateHandler={handleBeginChange} label={"Begin Date"} />
        <CalendarDatePicker date={endDate} setDateHandler={handleEndChange} label={"End Date"} />
      </Box>

      {error && (
        <Typography variant="body2" color="error" sx={{ mt: 2 }}>
          {error}
        </Typography>
      )}

      <Button variant="contained" onClick={handleOnClick}>
        Save Changes
      </Button>
    </Box>
  );
};

export default EditUniversePage;
