import { AppBar, Button, Toolbar, Typography } from '@mui/material';
import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Header = () => {
  const { user, logout } = useAuth();

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" style={{ flexGrow: 1 }}>
          <Link to="/" style={{ color: 'white', textDecoration: 'none' }}>
            Photo App
          </Link>
        </Typography>
        <Button color="inherit" component={Link} to="/photos">
          Photos
        </Button>
        <Button color="inherit" component={Link} to="/people">
          People
        </Button>
        <Button color="inherit" component={Link} to="/albums">
          Albums
        </Button>
        <Button color="inherit" component={Link} to="/search">
          Search
        </Button>
        {user ? (
          <Button color="inherit" onClick={logout}>
            Logout
          </Button>
        ) : (
          <>
            <Button color="inherit" component={Link} to="/login">
              Login
            </Button>
            <Button color="inherit" component={Link} to="/signup">
              Sign Up
            </Button>
          </>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default Header;