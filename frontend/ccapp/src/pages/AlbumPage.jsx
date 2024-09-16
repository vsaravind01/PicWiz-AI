import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import Album from '../components/Album';
import Image from '../components/Image';
import ImageDetails from '../components/ImageDetails';
import apiService from '../services/apiService';

const AlbumPage = () => {
  const [albums, setAlbums] = useState([]);
  const [selectedAlbum, setSelectedAlbum] = useState(null);
  const [selectedImage, setSelectedImage] = useState(null);
  const { id } = useParams();

  useEffect(() => {
    const fetchAlbums = async () => {
      try {
        const response = await apiService.listPersons(); // We'll use persons as albums for now
        setAlbums(response.data);
      } catch (error) {
        console.error('Error fetching albums:', error);
      }
    };

    fetchAlbums();
  }, []);

  useEffect(() => {
    if (id) {
      const fetchAlbumDetails = async () => {
        try {
          const personResponse = await apiService.getPerson(id);
          const photosResponse = await apiService.listPhotos(); // We'll filter photos on the client side for now
          const albumPhotos = photosResponse.data.filter(photo => photo.persons.includes(parseInt(id)));
          setSelectedAlbum({
            ...personResponse.data,
            photos: albumPhotos
          });
        } catch (error) {
          console.error('Error fetching album details:', error);
        }
      };

      fetchAlbumDetails();
    }
  }, [id]);

  return (
    <div className="container mx-auto px-4">
      {!id ? (
        <>
          <h1 className="text-3xl font-bold mb-6">Albums</h1>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {albums.map((album) => (
              <Album key={album.id} {...album} />
            ))}
          </div>
        </>
      ) : selectedAlbum ? (
        <>
          <h1 className="text-3xl font-bold mb-6">{selectedAlbum.name}</h1>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {selectedAlbum.photos.map((photo) => (
              <Image
                key={photo.id}
                src={photo.url}
                alt={photo.title}
                onClick={() => setSelectedImage(photo)}
              />
            ))}
          </div>
        </>
      ) : (
        <p>Loading album...</p>
      )}
      {selectedImage && (
        <ImageDetails image={selectedImage} onClose={() => setSelectedImage(null)} />
      )}
    </div>
  );
};

export default AlbumPage;