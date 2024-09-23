import { ImageList, Typography } from '@mui/material';
import React, { useEffect, useState } from 'react';
import Person from '../components/Person';
import { getPeople, getPersonPhotos } from '../services/api';
function People() {
  const [people, setPeople] = useState([]);
  const [personPhotos, setPersonPhotos] = useState({});

  useEffect(() => {
    const fetchPeople = async () => {
      try {
        const response = await getPeople();
        setPeople(response.data);
        var _photos = {}
        for (const person of response.data) {
          const photos = await getPersonPhotos(person.id);
          _photos[person.id] = photos.data;
        }
        setPersonPhotos(_photos);
        console.log(_photos);
      } catch (error) {
        console.error('Error fetching people:', error);
      }
    };
    fetchPeople();
  }, []);

  return (
    <div>
      <Typography variant="h4" gutterBottom>
        People in Your Photos
      </Typography>
      <ImageList variant="masonry" cols={3} gap={8}>
        {people.map((person) => (
            <Person key={person.id} person={person} photos={personPhotos[person.id]} />
        ))}
      </ImageList>
    </div>
  );
}

export default People;