import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Paper, Typography } from '@mui/material';

const ShortInterestComponent = ({ tickers, startDate, endDate }) => {
  const [data, setData] = useState([]);
  const [error, setError] = useState(null);
  console.log("Tickers: ", tickers);
  console.log("Start Date: ", startDate);
  console.log("End Date: ", endDate);

  useEffect(() => {
    const url = `http://localhost:8000/get_short_interest?tickers=${tickers}&start_date=${startDate}&end_date=${endDate}`;
    
    fetch(url)
      .then(response => {
        if (!response.ok) {
          throw new Error('Unable to get short interest');
        }
        return response.json();
      })
      .then(data => {
        console.log("API Response Data:", data);  // Log the API response for debugging
        const transformedData = [];

        // Check if 'short_interest' exists in the data and is an object
        if (data.short_interest && typeof data.short_interest === 'object') {
          // Iterate over the tickers in the short interest data
          Object.entries(data.short_interest).forEach(([ticker, shortInterestData]) => {
            // Ensure shortInterestData is an array
            if (Array.isArray(shortInterestData)) {
              shortInterestData.forEach(entry => {
                transformedData.push({
                  ...entry,
                  ticker: ticker,  // Add the ticker to each entry for identification
                });
              });
            } else {
              console.warn(`Expected an array for ticker ${ticker}, but got:`, shortInterestData);
            }
          });
        } else {
          console.error("Invalid data format:", data);
        }

        // Group data by date to create a common structure for the chart
        const groupedData = transformedData.reduce((acc, entry) => {
          const { date, short_interest, ticker } = entry;
          if (!acc[date]) {
            acc[date] = { date };  // Initialize date entry
          }
          acc[date][ticker] = short_interest;  // Set the short interest for this ticker
          return acc;
        }, {});

        setData(Object.values(groupedData));  // Convert the object to an array for charting
      })
      .catch(error => setError(error.message));
  }, [tickers, startDate, endDate]); 

  if (error) {
    return <Typography color="error">Error: {error}</Typography>;
  }

  // Extract unique tickers for rendering lines
  const uniqueTickers = Array.from(new Set(data.flatMap(item => Object.keys(item).slice(1))));

  // Function to generate a random hex color
  const getRandomColor = () => {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
      color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom sx={{ textAlign: 'center', mb: 2 }}>
        Short Interest
      </Typography>
      <ResponsiveContainer width={600} height={400}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          {/* Create a Line for each ticker */}
          {uniqueTickers.map((ticker) => (
            <Line 
              key={ticker} 
              type="monotone" 
              dataKey={ticker}  // Use ticker as the dataKey
              stroke={getRandomColor()}  // Generate a random color for each ticker
              activeDot={{ r: 8 }} 
              name={ticker}  // Set the name for the legend
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </Paper>
  );
};

export default ShortInterestComponent;
