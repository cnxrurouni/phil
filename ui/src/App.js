import { Box } from '@mui/material';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import MenuSidebar from './MenuSidebar';
import UniversePage from './UniversePage'; // Import your page components
import BacktestResultsPage from './BacktestResultsPage'; // Import your page components

const drawerWidth = 240;

const style={
  flexGrow: 1,
  p: 3,
  width: { sm: `calc(100% - ${drawerWidth}px)` }, // Aligns with MenuSidebar
};


function App() {
  return (
    <Router>
      <Box sx={{ display: 'flex' }}>
        <MenuSidebar style={style} />
        <Routes>
          <Route path="/universes" element={<UniversePage style={style} />} />
          <Route path="/backtest-results" element={<BacktestResultsPage style={style} />} />
          {/* Define other routes as needed */}
        </Routes>
      </Box>
    </Router>
  );
}
export default App;
