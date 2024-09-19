import * as React from 'react';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';

export default function StateTextFields({name, setName}) {

  return (
    <Box sx={{ width: 400}}
      component="form"
      noValidate
      autoComplete="off"
    >
      <TextField
        id="Name TextField"
        label="Universe Name"
        value={name}
        sx={{
          width: '100%',
        }}
        onChange={(event) => {
          setName(event.target.value);
        }}
      />
    </Box>
  );
}
