import { ImageListItem, ImageListItemBar } from "@mui/material";
import React, { useEffect, useState } from "react";
import { getPhoto } from "../services/api";
function Person({ person, photos }) {
    const [coverPhoto, setCoverPhoto] = useState(null);
    useEffect(() => {
        const fetchCoverPhoto = async () => {
            if (photos.length > 0) {
                const response = await getPhoto(photos[0].id);
                setCoverPhoto(response.data);
            }
        };
        fetchCoverPhoto();
        // if (firstPhoto) {
        //     getPhoto(firstPhoto.id).then(setCoverPhoto);
        // }
    }, [photos]);
    return (
        <ImageListItem>
            <img
                src={`data:image/jpeg;base64,${coverPhoto}`}
                alt={person.title}
                loading="lazy"
                width="80%"
            />
            <ImageListItemBar title={person.name ? person.name : "Person"} />
        </ImageListItem>
    );
}

export default Person;
