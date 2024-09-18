import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Box, Typography, Button, Toolbar } from '@mui/material';

const UniverseDetailPage = () => {
  const location = useLocation();
  const navigate = useNavigate(); // Initialize navigate

  // Destructure the state passed from the previous page
  const { universe } = location.state || {}; // Safely destructure the passed state

  console.log("state:", universe);

  // Handler for navigating to the CreateEditUniversePage
  const handleEditClick = () => {
    navigate(`/edit_universe/${universe.name}`, { state: { universe: universe } }); // Pass the current universe data
  };

  return (
    <Box component="main">
      <Toolbar /> {/* Align content below the AppBar */}
      <Typography variant="h6" sx={{ mb: 2, mt: 2 }}>
        Universe Details
      </Typography>

      <Typography variant="h6" sx={{ mb: 1 }}>
        name: {universe?.name || 'N/A'}
      </Typography>
      <Typography variant="body1" sx={{ mb: 2 }}>
        id: {universe?.id || 'N/A'}
      </Typography>
      <Typography variant="body1" sx={{ mb: 2 }}>
        Date range: {universe?.date_range ? `${universe.date_range.lower} - ${universe.date_range.upper}` : 'N/A'}
      </Typography>
      <Typography variant="body1" sx={{ mb: 2 }}>
        tickers: {universe?.tickers?.join(', ') || 'N/A'}
      </Typography>

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
