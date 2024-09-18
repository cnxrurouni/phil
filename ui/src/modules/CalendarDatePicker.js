import React from 'react';
import { DatePicker, LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import dayjs from 'dayjs';
import TextField from '@mui/material/TextField';


const CalendarDatePicker = ({ date, setDateHandler, label }) => {
  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <DatePicker
        label={label}
        value={date}
        onChange={(newValue) => setDateHandler(dayjs(newValue))}
        TextField={(params) => <TextField {...params} />}
      />
    </LocalizationProvider>
  );
};

export default CalendarDatePicker;