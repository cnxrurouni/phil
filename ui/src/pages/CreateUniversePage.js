import React, { useReducer } from 'react';
import { Typography, Box, Toolbar, Button } from '@mui/material';
import StockListDropdown from '../modules/StockListDropdown';
import CalendarDatePicker from '../modules/CalendarDatePicker';
import dayjs from 'dayjs';
import EnterNameForm from '../modules/EnterNameForm';
import { useNavigate } from 'react-router-dom';
import MeasurementPeriodDropdown from '../modules/MeasurementPeriodDrowndown';


// Form initial state
const initialState = {
  name: '',
  tickers: [],
  beginDate: null,
  endDate: null,
  measurementPeriod: 4,
  error: null
};

// Form reducer function to manage complex state
const formReducer = (state, action) => {
  switch (action.type) {
    case 'SET_FIELD':
      return { ...state, [action.field]: action.value };
    case 'SET_ERROR':
      return { ...state, error: action.error };
    case 'CLEAR_ERROR':
      return { ...state, error: null };
    default:
      return state;
  }
};

const CreateUniversePage = ({ style }) => {
  const [state, dispatch] = useReducer(formReducer, initialState);
  const navigate = useNavigate();

  // Handle field change
  const handleFieldChange = (field, value) => {
    dispatch({ type: 'SET_FIELD', field, value });
  };

  // Validate form
  const validateForm = () => {
    const { name, tickers, beginDate, endDate } = state;

    if (!name.trim()) {
      dispatch({ type: 'SET_ERROR', error: "Universe name is required." });
      return false;
    }

    if (tickers.length === 0) {
      dispatch({ type: 'SET_ERROR', error: "At least one stock must be selected." });
      return false;
    }

    if (!beginDate || !endDate) {
      dispatch({ type: 'SET_ERROR', error: "Both begin and end dates are required." });
      return false;
    }

    if (dayjs(beginDate).isAfter(dayjs(endDate))) {
      dispatch({ type: 'SET_ERROR', error: "Start date must be earlier than end date." });
      return false;
    }

    dispatch({ type: 'CLEAR_ERROR' });
    return true;
  };

  // Handle form submission
  const handleOnClick = () => {
    if (!validateForm()) return;

    const { name, tickers, beginDate, endDate, measurementPeriod } = state;
    const postData = {
      name: name,
      tickers: Array.isArray(tickers) ? tickers : [],
      date_range: `[${dayjs(beginDate).format('YYYY-MM-DD')}, ${dayjs(endDate).format('YYYY-MM-DD')}]`,
      measurement_period: measurementPeriod,
    };

    fetch(`${process.env.REACT_APP_API_SERVER_URL}/create_universe`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(postData),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then((data) => {
        console.log('Success:', data);
        navigate('/universes');
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  };

  return (
    <Box component="main" sx={style}>
      <Toolbar /> {/* This aligns the content below the AppBar */}

      <Typography variant="h6">1. Universe name:</Typography>
      <Box sx={{ mt: 2, mb: 2 }}>
        <EnterNameForm
          name={state.name}
          setName={(value) => handleFieldChange('name', value)}
        />
      </Box>

      <Typography variant="h6">2. Select stocks:</Typography>
      <Box sx={{ mb: 2, mt: 2 }}>
        <StockListDropdown
          tickers={state.tickers}
          setTickers={(value) => handleFieldChange('tickers', value)}
        />
      </Box>

      <Typography variant="h6">3. Select date range:</Typography>
      <Box sx={{ mb: 2, mt: 2 }}>
        <CalendarDatePicker
          date={state.beginDate}
          setDateHandler={(value) => handleFieldChange('beginDate', value)}
          label="Begin Date"
        />
        <CalendarDatePicker
          date={state.endDate}
          setDateHandler={(value) => handleFieldChange('endDate', value)}
          label="End Date"
        />
      </Box>

      <Typography variant="h6">4. Select measurement period:</Typography>
      <Box sx={{ mb: 2, mt: 2 }}>
        <MeasurementPeriodDropdown
          measurementPeriod={state.measurementPeriod}
          setMeasurementPeriod={(value) => handleFieldChange('measurementPeriod', value)}
        />
      </Box>

      {/* Display error message if any validation fails */}
      {state.error && (
        <Typography variant="body2" color="error" sx={{ mt: 2 }}>
          {state.error}
        </Typography>
      )}

      <Button variant="contained" onClick={handleOnClick}>
        Save Universe
      </Button>
    </Box>
  );
};

export default CreateUniversePage;
