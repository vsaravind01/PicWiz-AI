import { ImageList } from "@mui/material";
import React, { useEffect, useState } from "react";
import Photo from "../components/Photo";
import { getPhotos } from "../services/api";

function Photos() {
    const [photos, setPhotos] = useState([]);

    useEffect(() => {
        const fetchPhotos = async () => {
            try {
                const response = await getPhotos();
                setPhotos(response.data);
            } catch (error) {
                console.error("Error fetching photos:", error);
            }
        };
        fetchPhotos();
    }, []);

    return (
        <ImageList variant="masonry" cols={3} gap={8}>
            {photos.map((photo, index) => (
                <Photo key={index} photo={photo} />
            ))}
        </ImageList>
    );
}

export default Photos;
