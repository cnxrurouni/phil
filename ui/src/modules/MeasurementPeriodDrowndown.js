import React, { useEffect, useState } from 'react';
import { Autocomplete, Box, TextField } from '@mui/material';
import axios from 'axios';

const MeasurementPeriodDropdown = ({measurementPeriod, setMeasurementPeriod}) => {
  const [periods, setPeriods] = useState([]);

  useEffect(() => {
    // Fetch the allowed measurement periods from the backend
    axios.get(`${process.env.REACT_APP_API_SERVER_URL}/measurement_periods`)
      .then((response) => {
        const periodsData = response.data;
        setPeriods(periodsData);
        // Set the first option as the default value if the list is not empty
        if (periodsData.length > 0) {
            setMeasurementPeriod(measurementPeriod);
        }
      })
      .catch((error) => {
        console.error("Error fetching measurement periods", error);
      });
  }, []);

  return (
    <Box sx={{ width: 400 }}>
      <Autocomplete
        options={periods}
        value={measurementPeriod} // Set the value to selectedPeriod
        onChange={(_, newValue) => {
            setMeasurementPeriod(newValue); // Update the selected period when user selects a new value
        }}
        sx={{
          width: '100%',
          mb: 2, // Adjust margin for spacing
        }}
        renderInput={(params) => <TextField {...params} label="Measurement Period" />}
        getOptionLabel={(option) => option.toString()}
      />
    </Box>
  );
};

export default MeasurementPeriodDropdown;