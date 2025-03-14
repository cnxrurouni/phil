import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const update13FData = async (quarter = null, forceUpdate = false) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/update_13F_data`, {
      params: { 
        report_quarter: quarter,
        force_update: forceUpdate
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error updating 13F data:', error);
    throw error;
  }
};

export const getHoldings = async (ticker, quarter = null) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/holdings/${ticker}`, {
      params: { quarter }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching holdings:', error);
    throw error;
  }
};

export const getTickers = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/tickers`);
    return response.data.tickers;
  } catch (error) {
    console.error('Error fetching tickers:', error);
    throw error;
  }
}; 