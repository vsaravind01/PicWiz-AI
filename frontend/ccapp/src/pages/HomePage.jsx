import React, { useEffect, useState } from 'react';
import Image from '../components/Image';
import ImageDetails from '../components/ImageDetails';
import apiService from '../services/apiService';

const HomePage = () => {
  const [recentPhotos, setRecentPhotos] = useState([]);
  const [selectedImage, setSelectedImage] = useState(null);

  useEffect(() => {
    fetchRecentPhotos();
  }, []);

  const fetchRecentPhotos = async () => {
    try {
      const response = await apiService.listPhotos();
      setRecentPhotos(response.data);
    } catch (error) {
      console.error('Error fetching recent photos:', error);
    }
  };

  const handleImageUpdate = (updatedImage) => {
    setRecentPhotos(prevPhotos =>
      prevPhotos.map(photo => photo.id === updatedImage.id ? updatedImage : photo)
    );
    setSelectedImage(updatedImage);
  };

  const handleImageDelete = (deletedImageId) => {
    setRecentPhotos(prevPhotos => prevPhotos.filter(photo => photo.id !== deletedImageId));
    setSelectedImage(null);
  };

  return (
    <div className="container mx-auto px-4">
      <h1 className="text-3xl font-bold mb-6">Recent Photos</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {recentPhotos.map((photo) => (
          <Image
            key={photo.id}
            src={photo.url}
            alt={photo.title}
            onClick={() => setSelectedImage(photo)}
          />
        ))}
      </div>
      {selectedImage && (
        <ImageDetails
          image={selectedImage}
          onClose={() => setSelectedImage(null)}
          onUpdate={handleImageUpdate}
          onDelete={handleImageDelete}
        />
      )}
    </div>
  );
};

export default HomePage;