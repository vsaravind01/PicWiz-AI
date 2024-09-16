import axios from "axios";

const API_BASE_URL = "/api/v1";

const apiService = {
    // Person endpoints
    createPerson: (personData) =>
        axios.post(`${API_BASE_URL}/person/`, personData),
    listPersons: () => axios.get(`${API_BASE_URL}/person/`),
    getPerson: (personId) => axios.get(`${API_BASE_URL}/person/${personId}`),
    deletePerson: (personId) =>
        axios.delete(`${API_BASE_URL}/person/${personId}`),
    updatePerson: (personId, personData) =>
        axios.put(`${API_BASE_URL}/person/${personId}`, personData),
    updatePersonName: (personId, name) =>
        axios.put(`${API_BASE_URL}/person/${personId}/name/${name}`),
    searchPersons: (query) =>
        axios.get(`${API_BASE_URL}/person/search`, { params: { q: query } }),

    // Photo endpoints
    uploadPhoto: (photoData) => axios.post(`${API_BASE_URL}/photo/`, photoData),
    listPhotos: () => axios.get(`${API_BASE_URL}/photo/`),
    getPhoto: (photoId) => axios.get(`${API_BASE_URL}/photo/${photoId}`),
    deletePhoto: (photoId) => axios.delete(`${API_BASE_URL}/photo/${photoId}`),
    getFacesInPhoto: (photoId) =>
        axios.get(`${API_BASE_URL}/photo/${photoId}/faces`),

    // Face endpoints
    createFace: (faceData) => axios.post(`${API_BASE_URL}/face/`, faceData),
    getFace: (faceId) => axios.get(`${API_BASE_URL}/face/${faceId}`),
    deleteFace: (faceId) => axios.delete(`${API_BASE_URL}/face/${faceId}`),
    updateFace: (faceId, faceData) =>
        axios.put(`${API_BASE_URL}/face/${faceId}`, faceData),
};

export default apiService;
