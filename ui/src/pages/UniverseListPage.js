import React, { useState, useEffect } from 'react';
import { Typography, Box, Toolbar, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Checkbox, Button, TableSortLabel } from '@mui/material';
import { Link } from 'react-router-dom';

export default function UniverseListPage({ style }) {
  const [universes, setUniverses] = useState([]);
  const [selectedUniverses, setSelectedUniverses] = useState([]);
  const [sortOrder, setSortOrder] = useState('asc'); // State to track sorting order
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
        setUniverses(data.universes || []);
      } catch (error) {
        setError(error);
      }
    };

    fetchData();
  }, []);

  // Handle checkbox toggle for selecting universes
  const handleSelect = (universeId) => {
    setSelectedUniverses((prevSelected) =>
      prevSelected.includes(universeId)
        ? prevSelected.filter((id) => id !== universeId)
        : [...prevSelected, universeId]
    );
  };

  // Handle sorting by id
  const handleSort = () => {
    const newOrder = sortOrder === 'asc' ? 'desc' : 'asc';
    const sortedUniverses = [...universes].sort((a, b) => {
      if (newOrder === 'asc') {
        return a.id - b.id;
      } else {
        return b.id - a.id;
      }
    });

    setSortOrder(newOrder);
    setUniverses(sortedUniverses);
  };

  // Handle deletion of selected universes
  const handleDelete = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_SERVER_URL}/delete_universes`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ universe_ids: selectedUniverses }), // Send selected universe IDs in the body
      });

      if (!response.ok) {
        throw new Error('Failed to delete universes');
      }

      // Remove the deleted universes from the list
      setUniverses((prevUniverses) =>
        prevUniverses.filter((universe) => !selectedUniverses.includes(universe.id))
      );
      setSelectedUniverses([]); // Clear the selection after deletion
    } catch (error) {
      setError(error);
    }
  };

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
              <TableCell sx={SX2}>Select</TableCell>
              <TableCell sx={SX2}>
                <TableSortLabel
                  active={true} // Always show sort icon for "Id"
                  direction={sortOrder}
                  onClick={handleSort}
                >
                  Id
                </TableSortLabel>
              </TableCell>
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
                    <Checkbox
                      checked={selectedUniverses.includes(universe.id)}
                      onChange={() => handleSelect(universe.id)}
                    />
                  </TableCell>
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
                <TableCell colSpan={6} sx={{ textAlign: 'center' }}>
                  No universes available
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Delete button */}
      <Button
        variant="contained"
        color="error"
        sx={{ marginTop: 2 }}
        onClick={handleDelete}
        disabled={selectedUniverses.length === 0} // Disable button if no universes selected
      >
        Delete Selected
      </Button>
    </Box>
  );
}