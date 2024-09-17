import { Box } from '@mui/material';
import MenuSidebar from './modules/MenuSidebar';
import CreateUniversePage from './pages/CreateUniversePage';
import ExamplePage from './pages/ExamplePage'; 
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs'
import UniverseListPage from './pages/UniverseListPage';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';


const drawerWidth = 240;

const style={
  flexGrow: 1,
  p: 3,
  width: { sm: `calc(100% - ${drawerWidth}px)` }, // Aligns with MenuSidebar
};


function App({ children }) {
  return (
    <><LocalizationProvider dateAdapter={AdapterDayjs}>
      {children}
    </LocalizationProvider><Router>
        <Box sx={{ display: 'flex' }}>
          <MenuSidebar style={style} />
          <Routes>
            <Route path="/" element={<Navigate to="/universes" />} /> {/* Redirect to UniverseListPage */}
            <Route path="/create_universe" element={<CreateUniversePage style={style} />} />
            <Route path="/backtest_results" element={<ExamplePage style={style} />} />
            <Route path="/universes" element={<UniverseListPage style={style} />} />
            {/* Define other routes as needed */}
          </Routes>
        </Box>
      </Router></>
  );
}
export default App;
