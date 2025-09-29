import React from 'react';
import { AppBar, Toolbar, Typography, Box } from '@mui/material';
import { colors } from '../styles/colors';

function Header() {
  return (
    <AppBar
      position="static"
      sx={{
        backgroundColor: colors.primary,
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}
    >
      <Toolbar>
        <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
          <img
            src="/policyengine-logo-white.svg"
            alt="PolicyEngine"
            style={{
              height: '32px',
              marginRight: '16px',
            }}
          />
          <Typography
            variant="h5"
            component="h1"
            sx={{
              fontWeight: 600,
              color: colors.text.white,
              fontFamily: 'Roboto, sans-serif'
            }}
          >
            The Marginal Child
          </Typography>
          <Typography
            variant="body2"
            sx={{
              ml: 2,
              color: colors.text.white,
              opacity: 0.9,
              fontStyle: 'italic'
            }}
          >
            Powered by PolicyEngine
          </Typography>
        </Box>
      </Toolbar>
    </AppBar>
  );
}

export default Header;