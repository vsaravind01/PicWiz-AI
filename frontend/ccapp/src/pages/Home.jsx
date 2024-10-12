import { Button, Grid, Paper, Typography } from '@mui/material';
import React from 'react';
import { Link } from 'react-router-dom';

function Home() {
  return (
    <div style={{ padding: '20px' }}>
      <Typography variant="h3" gutterBottom>
        Your Photo Library
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper elevation={3} style={{ padding: '20px', textAlign: 'center' }}>
            <Typography variant="h5" gutterBottom>
              Photos
            </Typography>
            <Button component={Link} to="/photos" variant="contained" color="primary">
              View Photos
            </Button>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper elevation={3} style={{ padding: '20px', textAlign: 'center' }}>
            <Typography variant="h5" gutterBottom>
              Albums
            </Typography>
            <Button component={Link} to="/albums" variant="contained" color="primary">
              View Albums
            </Button>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper elevation={3} style={{ padding: '20px', textAlign: 'center' }}>
            <Typography variant="h5" gutterBottom>
              People
            </Typography>
            <Button component={Link} to="/people" variant="contained" color="primary">
              View People
            </Button>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper elevation={3} style={{ padding: '20px', textAlign: 'center' }}>
            <Typography variant="h5" gutterBottom>
              Search
            </Typography>
            <Button component={Link} to="/search" variant="contained" color="primary">
              Search Photos
            </Button>
          </Paper>
        </Grid>
      </Grid>
    </div>
  );
}

export default Home;