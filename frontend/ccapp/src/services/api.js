import axios from 'axios';

const API_URL = 'http://localhost:8080/api/v1';

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const login = (credentials) => api.post('/auth/login', credentials);
export const getPhotos = () => api.get('/photos');
export const getPhoto = (photoId) => api.get(`/photos/${photoId}/download`);
export const getPeople = () => api.get('/persons');
export const getPersonPhotos = (personId) => api.get(`/persons/${personId}/photos`);
export const getAlbums = () => api.get('/albums');
export const searchPhotos = (query) => api.get(`/search?q=${query}`);

export const createAlbum = (albumData) => api.post('/albums', albumData);
export const getPersonDetails = (personId) => api.get(`/persons/${personId}`);

export default api;