import React, { useState, useEffect } from 'react';
import { Typography, Box, Toolbar } from '@mui/material';
import StockListDropdown from '../modules/StockListDropdown';
import CalendarDatePicker from '../modules/CalendarDatePicker';
import dayjs from 'dayjs';
import EnterNameForm from '../modules/EnterNameForm';
import Button from '@mui/material/Button';

const apiServerUrl = process.env.REACT_APP_API_SERVER_URL;


const CreateUniversePage = ({ style }) => {
    const [name, setName] = useState("");
    const [tickers, setTickers] = useState([]);
    const [beginDate, setBeginDate] = useState(null);
    const [endDate, setEndDate] = useState(null);
    const [error, setError] = useState(null);

    const handleBeginChange = (newValue) => {
      setBeginDate(newValue); // Update the selected tickers array in parent component
      // console.log('begin date: ', newValue);
    };

    const handleEndChange = (newValue) => {
      setEndDate(newValue); // Update the selected tickers array in parent component
      // console.log('end date: ', newValue);
    };

    const handleOnClick = () => {
      // Define the data you want to send in the request body
      const postData = {
        name: name,
        tickers: Array.isArray(tickers) ? tickers : [],
        date_range: `[${beginDate}, ${endDate}]`,
      };

      // Make the POST request
      fetch(`${apiServerUrl}/create_universe`, {
        method: 'POST', // Specify the request method
        headers: {
            'Content-Type': 'application/json' // Specify the content type of the request body
        },
        body: JSON.stringify(postData) // Convert the data to a JSON string
      })
      .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json(); // Parse the JSON from the response
      })
      .then(data => {
        console.log('Success:', data); // Handle the parsed data from the response
      })
      .catch(error => {
        console.error('Error:', error); // Handle any errors that occurred
      });
    };

    // Validation function to check if beginDate < endDate using dayjs
    const validateDates = (begin, end) => {
        if (begin && end && dayjs(begin).isAfter(dayjs(end))) {
            setError("Start date must be earlier than end date.");
        } else {
          setError(null); // Clear the error if dates are valid
        }
    };

    // Effect to validate dates whenever beginDate or endDate changes
    useEffect(() => {
        validateDates(beginDate, endDate);
    }, [beginDate, endDate]);

    return (
      <Box component="main" sx={style}>
        <Toolbar /> {/* This aligns the content below the AppBar */}
        <Typography variant="h8">
          1. Universe Name:
        </Typography>

        <Box sx={{mt: 2, mb: 2}}>
          <EnterNameForm name={name} setName={setName}></EnterNameForm>
        </Box>

        <Typography variant="h8">
          2. Select stocks:
        </Typography>

        <Box sx={{mb: 2, mt:2}}>
        <StockListDropdown tickers={tickers} setTickers={setTickers} />
        </Box>
        
        <Typography variant="h8">
          3. Select date range:
        </Typography>

        <Box sx={{mb: 2, mt:2}}>
          <CalendarDatePicker date={beginDate} setDateHandler={handleBeginChange} label={"Begin Date"}/>
          <CalendarDatePicker date={endDate} setDateHandler={handleEndChange} label={"End Date"}/>
        </Box>
        
        {/* Display error message if dates are invalid */}
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

