import React, { useEffect, useState } from 'react';

function DataFetchingComponent() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Make HTTP GET request when the component mounts
    fetch('http://localhost:8000/tickers')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => setData(data))
      .catch(error => setError(error));
  }, []);

  useEffect(() => {
    // Make HTTP GET request when the component mounts
    fetch('http://apiserver:8000/tickers')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => setData(data))
      .catch(error => setError(error));
  }, []); // Empty array means this useEffect runs once, on mount

  return (
    <div>
      {error && <p>Error: {error.message}</p>}
      {data ? (
        <div>
          <h3>Data fetched from API:</h3>
          <pre>{JSON.stringify(data, null, 2)}</pre>
        </div>
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
}

export default DataFetchingComponent;