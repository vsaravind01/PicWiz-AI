import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import Person from '../components/Person';
import Image from '../components/Image';
import ImageDetails from '../components/ImageDetails';
import apiService from '../services/apiService';

const PersonPage = () => {
  const [people, setPeople] = useState([]);
  const [selectedPerson, setSelectedPerson] = useState(null);
  const [selectedImage, setSelectedImage] = useState(null);
  const { id } = useParams();

  useEffect(() => {
    const fetchPeople = async () => {
      try {
        const response = await apiService.listPersons();
        setPeople(response.data);
      } catch (error) {
        console.error('Error fetching people:', error);
      }
    };

    fetchPeople();
  }, []);

  useEffect(() => {
    if (id) {
      const fetchPersonDetails = async () => {
        try {
          const personResponse = await apiService.getPerson(id);
          const photosResponse = await apiService.listPhotos(); // We'll filter photos on the client side for now
          const personPhotos = photosResponse.data.filter(photo => photo.persons.includes(parseInt(id)));
          setSelectedPerson({
            ...personResponse.data,
            photos: personPhotos
          });
        } catch (error) {
          console.error('Error fetching person details:', error);
        }
      };

      fetchPersonDetails();
    }
  }, [id]);

  return (
    <div className="container mx-auto px-4">
      {!id ? (
        <>
          <h1 className="text-3xl font-bold mb-6">People</h1>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {people.map((person) => (
              <Person key={person.id} {...person} />
            ))}
          </div>
        </>
      ) : selectedPerson ? (
        <>
          <h1 className="text-3xl font-bold mb-6">{selectedPerson.name}</h1>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {selectedPerson.photos.map((photo) => (
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
        <p>Loading person...</p>
      )}
      {selectedImage && (
        <ImageDetails image={selectedImage} onClose={() => setSelectedImage(null)} />
      )}
    </div>
  );
};

export default PersonPage;