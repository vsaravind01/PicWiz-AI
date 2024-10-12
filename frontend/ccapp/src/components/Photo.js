import { ImageListItem } from "@mui/material";
import React, { useEffect, useState } from 'react';
import { getPhoto } from '../services/api';

function Photo({ photo }) {
    const [image, setImage] = useState(null);

    useEffect(() => {
        const fetchImage = async () => {
            try {
                const response = await getPhoto(photo.id);
                setImage(response.data);
            } catch (error) {
                console.error("Error fetching image:", error);
            }
        };
        fetchImage();
    }, [photo.id]);

    return (
        <ImageListItem>
            <img
                src={`data:image/jpeg;base64,${image}`}
                alt={photo.title}
                loading="lazy"
                width="80%"
            />
        </ImageListItem>
    );
}

export default Photo;
