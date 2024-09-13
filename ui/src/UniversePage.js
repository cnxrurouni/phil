// UniversePage.js
import React from 'react';
import { Typography, Box, Toolbar } from '@mui/material';


const UniversePage = ({ style }) => {
    return (
      <Box
        component="main"
        sx={style}
      >
        <Toolbar /> {/* This aligns the content below the AppBar */}
        <Typography variant="h4">
          I am the universe page
        </Typography>
        <Typography>
          Add more content related to the universe page here.
        </Typography>
      </Box>
    );
  };
  
export default UniversePage;