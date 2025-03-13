import * as React from 'react';
import { AppBar, Toolbar, IconButton, Drawer, List, ListItem, ListItemText, Typography, CssBaseline, Divider } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import { Box } from '@mui/system';
import { useNavigate } from 'react-router-dom'; // Import useNavigate hook
import '../css/MenuSidebar.css';

const drawerWidth = 240;

export default function MenuSidebar({style}) {
  const [mobileOpen, setMobileOpen] = React.useState(false);
  const navigate = useNavigate(); // Initialize navigate

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleNavigation = (index) => {
    switch (index) {
      case 0:
        navigate("/universes");
        break;
      case 1:
        navigate("/create_universe");
        break;
      case 2:
        navigate("/backtest_results");
        break;
      case 3:
        navigate("/stock_analysis");
        break;
      default:
        break;
    }
  };
  
  const menuList = [
    'Universes',
    'Create Universe',
    'Backtest Results',
    'Stock Analysis'
  ];

  const drawer = (
    <div>
      <Toolbar />
      <Divider />
      <List>
        {menuList.map((text, index) => (
          <ListItem button key={text} onClick={() => handleNavigation(index)}>
            <ListItemText primary={text} />
          </ListItem>
        ))}
      </List>
    </div>
  );

  return (
    /* First box is the blue top header */
    <Box sx={{ display: 'flex', align: 'center'}}>
      <CssBaseline />
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar sx={{ display: 'flex', justifyContent: 'space-between' }}>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ align: 'center', mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap sx={{ flexGrow: 1, textAlign: 'center' }}>
            Backtest Tool
          </Typography>
        </Toolbar>
      </AppBar>
      <Box
        component="navigation"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
        aria-label="mailbox folders"
      >
        {/* The implementation can be swapped with js to avoid SEO duplication of links. */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile.
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={style}
      >
        <Toolbar />
        <Typography>
        </Typography>
      </Box>
    </Box>
  );
}
