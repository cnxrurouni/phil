import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Box, Typography, Button, Toolbar, Paper } from '@mui/material';
import ShortInterestComponent from '../modules/ShortInterestComponent';

const UniverseDetailPage = () => {
  const location = useLocation();
  const navigate = useNavigate();

  // Destructure the state passed from the previous page
  const { universe } = location.state || {}; // Safely destructure the passed state

  // Handler for navigating to the CreateEditUniversePage
  const handleEditClick = () => {
    navigate(`/edit_universe/${universe.name}`, { state: { universe: universe } });
  };

  const startDate = universe?.date_range?.lower;
  const endDate = universe?.date_range?.upper;
  const tickers = universe?.tickers?.join(',') || 'N/A';

  return (
    <Box component="main" sx={{ p: 3 }}>
      <Toolbar /> {/* Align content below the AppBar */}
      <Typography variant="h6" sx={{ mb: 2 }}>
        Universe Details
      </Typography>
      
      {/* Universe Information */}
      <Typography variant="body1" sx={{ mb: 1 }}>
        <strong>Name:</strong> {universe?.name || 'N/A'}
      </Typography>
      <Typography variant="body1" sx={{ mb: 1 }}>
        <strong>ID:</strong> {universe?.id || 'N/A'}
      </Typography>
      <Typography variant="body1" sx={{ mb: 1 }}>
        <strong>Date Range:</strong> {universe?.date_range ? `${startDate} - ${endDate}` : 'N/A'}
      </Typography>
      <Typography variant="body1" sx={{ mb: 1 }}>
        <strong>Tickers:</strong> {tickers}
      </Typography>
      <Typography variant="body1" sx={{ mb: 1 }}>
        <strong>Measurement Period:</strong> {universe?.measurement_period}
      </Typography>

      {/* Short Interest Chart */}
      <ShortInterestComponent 
        tickers={tickers}
        startDate={startDate} 
        endDate={endDate} 
      />

      {/* Edit Button */}
      <Button
        variant="contained"
        color="primary"
        onClick={handleEditClick}
      >
        Edit Universe
      </Button>
    </Box>
  );
};

export default UniverseDetailPage;
