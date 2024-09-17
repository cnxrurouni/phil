// UniversePage.js
import React from 'react';
import { Typography, Box, Toolbar } from '@mui/material';


const BackTestResultPage = ({ style }) => {
    return (
      <Box
        component="main"
        sx={style}
      >
        <Toolbar /> {/* This aligns the content below the AppBar */}
        <Typography variant="h4">
          I am the back test result page
        </Typography>
        <Typography>
          Add more content related to the back test result page here.
        </Typography>
      </Box>
    );
  };
  
export default BackTestResultPage;