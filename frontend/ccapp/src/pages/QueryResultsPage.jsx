import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import Image from '../components/Image';
import ImageDetails from '../components/ImageDetails';
import apiService from '../services/apiService';

const QueryResultsPage = () => {
  const [searchResults, setSearchResults] = useState([]);
  const [selectedImage, setSelectedImage] = useState(null);
  const location = useLocation();

  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    const query = searchParams.get('q');

    const fetchSearchResults = async () => {
      try {
        const personsResponse = await apiService.searchPersons(query);
        const photosResponse = await apiService.listPhotos(); // We'll filter photos on the client side for now
        const matchingPhotos = photosResponse.data.filter(photo => 
          photo.title.toLowerCase().includes(query.toLowerCase()) ||
          photo.persons.some(personId => 
            personsResponse.data.some(person => person.id === personId)
          )
        );
        setSearchResults(matchingPhotos);
      } catch (error) {
        console.error('Error fetching search results:', error);
      }
    };

    if (query) {
      fetchSearchResults();
    }
  }, [location.search]);

  return (
    <div className="container mx-auto px-4">
      <h1 className="text-3xl font-bold mb-6">Search Results</h1>
      {searchResults.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {searchResults.map((result) => (
            <Image
              key={result.id}
              src={result.url}
              alt={result.title}
              onClick={() => setSelectedImage(result)}
            />
          ))}
        </div>
      ) : (
        <p>No results found.</p>
      )}
      {selectedImage && (
        <ImageDetails image={selectedImage} onClose={() => setSelectedImage(null)} />
      )}
    </div>
  );
};

export default QueryResultsPage;