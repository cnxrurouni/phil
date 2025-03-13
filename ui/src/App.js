import { Box } from '@mui/material';
import MenuSidebar from './modules/MenuSidebar';
import ExamplePage from './pages/ExamplePage'; 
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import UniverseListPage from './pages/UniverseListPage';
import UniverseDetailPage from './pages/UniverseDetailPage';
import CreateUniversePage from './pages/CreateUniversePage';
import EditUniversePage from './pages/EditUniversePage';
import StockAnalysisPage from './pages/StockAnalysisPage';


const drawerWidth = 100;

const style={
  flexGrow: 1,
  p: 3,
  width: { sm: `calc(100% - ${drawerWidth}px)` }, // Aligns with MenuSidebar
};


function App({ children }) {
  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      {children}
      <Router>
        <Box sx={{ display: 'flex' }}>
          <MenuSidebar style={style} />
          <Routes>
            <Route path="/" element={<Navigate to="/universes" />} /> {/* Redirect to UniverseListPage */}
            <Route path="/create_universe" element={<CreateUniversePage style={style} />} />
            <Route path="/backtest_results" element={<ExamplePage style={style} />} />
            <Route path="/universes" element={<UniverseListPage style={style} />} />
            <Route path="/universe/:name" element={<UniverseDetailPage />} />
            <Route path="/edit_universe/:name" element={<EditUniversePage />} />
            <Route path="/stock_analysis" element={<StockAnalysisPage style={style} />} />
            {/* Define other routes as needed */}
          </Routes>
        </Box>
      </Router>
    </LocalizationProvider>
  );
}
export default App;
