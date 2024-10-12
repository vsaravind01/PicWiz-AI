import React, { useState, useEffect } from 'react';
import { Grid, Card, CardMedia, CardContent, Typography, Button } from '@mui/material';
import { getAlbums } from '../services/api';

function Albums() {
  const [albums, setAlbums] = useState([]);

  useEffect(() => {
    const fetchAlbums = async () => {
      try {
        const response = await getAlbums();
        setAlbums(response.data);
      } catch (error) {
        console.error('Error fetching albums:', error);
      }
    };
    fetchAlbums();
  }, []);

  return (
    <div>
      <Typography variant="h4" gutterBottom>
        Albums
      </Typography>
      <Button variant="contained" color="primary" style={{ marginBottom: '20px' }}>
        Create New Album
      </Button>
      <Grid container spacing={2}>
        {albums.map((album) => (
          <Grid item xs={12} sm={6} md={4} key={album.id}>
            <Card>
              <CardMedia
                component="img"
                height="200"
                image={album.cover_photo_url || 'https://via.placeholder.com/200'}
                alt={album.name}
              />
              <CardContent>
                <Typography variant="h6">{album.name}</Typography>
                <Typography variant="body2" color="textSecondary">
                  {album.photo_count} photos
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </div>
  );
}

export default Albums;