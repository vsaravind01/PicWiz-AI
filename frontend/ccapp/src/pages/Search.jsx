import { Button, Grid, TextField } from '@mui/material';
import React, { useState } from 'react';
import { searchPhotos } from '../services/api';

function Search() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  const handleSearch = async (e) => {
    e.preventDefault();
    try {
      const response = await searchPhotos(query);
      setResults(response.data);
    } catch (error) {
      console.error('Error searching photos:', error);
    }
  };

  return (
    <div>
      <form onSubmit={handleSearch}>
        <TextField
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          label="Search photos"
          variant="outlined"
          fullWidth
        />
        <Button type="submit" variant="contained" color="primary">
          Search
        </Button>
      </form>
      <Grid container spacing={2}>
        {/* Display search results similar to the Photos component */}
      </Grid>
    </div>
  );
}

export default Search;