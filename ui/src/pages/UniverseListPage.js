import React, { useState, useEffect } from 'react';
import { Typography, Box, Toolbar, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';

const apiServerUrl = process.env.REACT_APP_API_SERVER_URL;

export default function UniverseListPage({ style }) {
  const [universes, setUniverses] = useState([]);
  const [error, setError] = useState(null);

  // Fetch universe data when the component mounts
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`${apiServerUrl}/get_universes`);
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
              <TableCell sx={{ fontWeight: 'bold', borderBottom: '2px solid #ddd', borderRight: '1px solid #ddd' }}>Id</TableCell>
              <TableCell sx={{ fontWeight: 'bold', borderBottom: '2px solid #ddd', borderRight: '1px solid #ddd' }}>Name</TableCell>
              <TableCell sx={{ fontWeight: 'bold', borderBottom: '2px solid #ddd', borderRight: '1px solid #ddd' }}>Date Range</TableCell>
              <TableCell sx={{ fontWeight: 'bold', borderBottom: '2px solid #ddd' }}>Tickers</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {universes.length > 0 ? (
              universes.map((universe) => (
                <TableRow key={universe.id} sx={{ '&:nth-of-type(odd)': { backgroundColor: '#f9f9f9' } }}>
                  <TableCell sx={{ borderBottom: '1px solid #ddd', borderRight: '1px solid #ddd' }}>{universe.id || 'N/A'}</TableCell>
                  <TableCell sx={{ borderBottom: '1px solid #ddd', borderRight: '1px solid #ddd' }}>{universe.name || 'N/A'}</TableCell>
                  <TableCell sx={{ borderBottom: '1px solid #ddd', borderRight: '1px solid #ddd' }}>
                    {universe.date_range ? `${universe.date_range.lower} - ${universe.date_range.upper}` : 'N/A'}
                  </TableCell>
                  <TableCell sx={{ borderBottom: '1px solid #ddd' }}>{universe.tickers.join(', ')}</TableCell>
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
