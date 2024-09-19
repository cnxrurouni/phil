import React, { useState, useEffect } from 'react';
import { Typography, Box, Toolbar, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';
import { Link } from 'react-router-dom';  // Import Link from react-router-dom


export default function UniverseListPage({ style }) {
  const [universes, setUniverses] = useState([]);
  const [error, setError] = useState(null);

  const SX = {
    borderBottom: '1px solid #ddd',
    borderRight: '1px solid #ddd',
  };

  const SX2 = {
    fontWeight: 'bold', 
    borderBottom: '2px solid #ddd',
    borderRight: '1px solid #ddd',
  };

  // Fetch universe data when the component mounts
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`${process.env.REACT_APP_API_SERVER_URL}/get_universes`);
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        console.log('Fetched data:', data);
        setUniverses(data.universes || []); // Ensure default empty array if no universes
      } catch (error) {
        setError(error);
      }
    };

    fetchData();
  }, []);

  if (error) {
    return <Typography color="error">Error: {error.message}</Typography>;
  }

  return (
    <Box component="main" sx={style}>
      <Toolbar /> {/* This aligns the content below the AppBar */}
      <Typography variant="h6">Universe List:</Typography>
      <TableContainer component={Paper} sx={{ marginTop: 2, maxHeight: 600 }}>
        <Table stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell sx={SX2}>Id</TableCell>
              <TableCell sx={SX2}>Name</TableCell>
              <TableCell sx={SX2}>Date Range</TableCell>
              <TableCell sx={SX2}>Tickers</TableCell>
              <TableCell sx={SX2}>Measurement Period</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {universes.length > 0 ? (
              universes.map((universe) => (
                <TableRow key={universe.id} sx={{ '&:nth-of-type(odd)': { backgroundColor: '#f9f9f9' } }}>
                  <TableCell sx={SX}>
                    <Link to={`/universe/${universe.id}`} state={{ universe: universe }} underline="hover">
                      {universe.id}
                    </Link>
                  </TableCell>
                  <TableCell sx={SX}>
                    <Link to={`/universe/${universe.name}`} state={{ universe: universe }} underline="hover">
                      {universe.name}
                    </Link>
                  </TableCell>
                  <TableCell sx={SX}>
                    {universe.date_range ? `${universe.date_range.lower} - ${universe.date_range.upper}` : 'N/A'}
                  </TableCell>
                  <TableCell sx={SX}>{universe.tickers.join(', ')}</TableCell>
                  <TableCell sx={SX}>{universe.measurement_period}</TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={4} sx={{ textAlign: 'center' }}>No universes available</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}