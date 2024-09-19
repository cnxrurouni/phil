import React, { useReducer, useEffect } from 'react';
import { Typography, Box, Toolbar, Button } from '@mui/material';
import StockListDropdown from '../modules/StockListDropdown';
import CalendarDatePicker from '../modules/CalendarDatePicker';
import dayjs from 'dayjs';
import EnterNameForm from '../modules/EnterNameForm';
import { useNavigate, useLocation } from 'react-router-dom';
import MeasurementPeriodDropdown from '../modules/MeasurementPeriodDrowndown';


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

const EditUniversePage = ({ style }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [state, dispatch] = useReducer(formReducer, location.state.universe);

  // Handle field change
  const handleFieldChange = (field, value) => {
    dispatch({ type: 'SET_FIELD', field, value });
  };

    // Validate form
    const validateForm = () => {
      const { name, tickers, date_range, measurement_period } = state;

      const beginDate = dayjs(date_range.lower);
      const endDate = dayjs(date_range.upper);
  
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

  const handleOnClick = () => {
    if (!validateForm()) {
      return;
    }

    const { name, tickers, date_range, measurement_period } = state;

    const putData = {
      name: name,
      tickers: Array.isArray(tickers) ? tickers : [],
      date_range: `[${dayjs(date_range.lower).format('YYYY-MM-DD')}, ${dayjs(date_range.upper).format('YYYY-MM-DD')}]`,
      measurement_period: measurement_period,
    };

    // Make the POST request
    fetch(`${process.env.REACT_APP_API_SERVER_URL}/edit_universe/${state.id}`, {
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
      navigate("/universes");
    })
    .catch(error => {
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
          setDateHandler={(value) => handleFieldChange('beginDate', value)}
          label="Begin Date"
        />
        <CalendarDatePicker
          setDateHandler={(value) => handleFieldChange('endDate', value)}
          label="End Date"
        />
      </Box>

      <Typography variant="h6">4. Select measurement period:</Typography>
      <Box sx={{ mb: 2, mt: 2 }}>
        <MeasurementPeriodDropdown
          measurementPeriod={state.measurement_period}
          setMeasurementPeriod={(value) => handleFieldChange('measurement_period', value)}
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

export default EditUniversePage;
