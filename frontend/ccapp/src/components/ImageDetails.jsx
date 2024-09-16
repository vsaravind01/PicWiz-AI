import React, { useState, useEffect } from 'react';
import { X, Calendar, MapPin, Users, Folder, Tag, Edit2, Trash2 } from 'lucide-react';
import apiService from '../services/apiService';

const ImageDetails = ({ image, onClose, onUpdate, onDelete }) => {
  const [faces, setFaces] = useState([]);
  const [editMode, setEditMode] = useState(false);
  const [editedImage, setEditedImage] = useState({ ...image });

  useEffect(() => {
    const fetchFaces = async () => {
      try {
        const response = await apiService.getFacesInPhoto(image.id);
        setFaces(response.data);
      } catch (error) {
        console.error('Error fetching faces:', error);
      }
    };

    fetchFaces();
  }, [image.id]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setEditedImage(prev => ({ ...prev, [name]: value }));
  };

  const handleSave = async () => {
    try {
      await apiService.updatePhoto(image.id, editedImage);
      onUpdate(editedImage);
      setEditMode(false);
    } catch (error) {
      console.error('Error updating image:', error);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this image?')) {
      try {
        await apiService.deletePhoto(image.id);
        onDelete(image.id);
        onClose();
      } catch (error) {
        console.error('Error deleting image:', error);
      }
    }
  };

  if (!image) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg overflow-hidden max-w-6xl w-full max-h-[90vh] flex">
        <div className="w-2/3 bg-gray-100 relative">
          <img src={image.url} alt={image.title} className="w-full h-full object-contain" />
          {faces.map((face) => (
            <div
              key={face.id}
              style={{
                position: 'absolute',
                left: `${face.x * 100}%`,
                top: `${face.y * 100}%`,
                width: `${face.width * 100}%`,
                height: `${face.height * 100}%`,
                border: '2px solid red',
              }}
            />
          ))}
        </div>
        <div className="w-1/3 p-6 overflow-y-auto">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">
              {editMode ? (
                <input
                  type="text"
                  name="title"
                  value={editedImage.title}
                  onChange={handleInputChange}
                  className="w-full border-b border-gray-300 focus:border-blue-500 outline-none"
                />
              ) : (
                image.title
              )}
            </h2>
            <div className="flex space-x-2">
              {editMode ? (
                <>
                  <button onClick={handleSave} className="text-green-500 hover:text-green-700">
                    Save
                  </button>
                  <button onClick={() => setEditMode(false)} className="text-gray-500 hover:text-gray-700">
                    Cancel
                  </button>
                </>
              ) : (
                <button onClick={() => setEditMode(true)} className="text-blue-500 hover:text-blue-700">
                  <Edit2 className="h-5 w-5" />
                </button>
              )}
              <button onClick={handleDelete} className="text-red-500 hover:text-red-700">
                <Trash2 className="h-5 w-5" />
              </button>
              <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
                <X className="h-6 w-6" />
              </button>
            </div>
          </div>
          <div className="space-y-4">
            <div className="flex items-center">
              <Calendar className="h-5 w-5 mr-2 text-gray-500" />
              <p><strong>Date:</strong> {editMode ? (
                <input
                  type="date"
                  name="date"
                  value={editedImage.date}
                  onChange={handleInputChange}
                  className="border-b border-gray-300 focus:border-blue-500 outline-none"
                />
              ) : image.date}</p>
            </div>
            <div className="flex items-center">
              <MapPin className="h-5 w-5 mr-2 text-gray-500" />
              <p><strong>Location:</strong> {editMode ? (
                <input
                  type="text"
                  name="location"
                  value={editedImage.location}
                  onChange={handleInputChange}
                  className="border-b border-gray-300 focus:border-blue-500 outline-none"
                />
              ) : image.location}</p>
            </div>
            <div className="flex items-start">
              <Users className="h-5 w-5 mr-2 mt-1 text-gray-500" />
              <div>
                <strong>People:</strong>
                <ul className="list-disc list-inside">
                  {image.persons.map((person, index) => (
                    <li key={index}>{person}</li>
                  ))}
                </ul>
              </div>
            </div>
            <div className="flex items-center">
              <Folder className="h-5 w-5 mr-2 text-gray-500" />
              <p><strong>Album:</strong> {image.album}</p>
            </div>
            <div className="flex items-start">
              <Tag className="h-5 w-5 mr-2 mt-1 text-gray-500" />
              <div>
                <strong>Tags:</strong>
                {editMode ? (
                  <input
                    type="text"
                    name="tags"
                    value={editedImage.tags.join(', ')}
                    onChange={(e) => setEditedImage(prev => ({ ...prev, tags: e.target.value.split(', ') }))}
                    className="w-full border-b border-gray-300 focus:border-blue-500 outline-none"
                  />
                ) : (
                  <ul className="list-disc list-inside">
                    {image.tags.map((tag, index) => (
                      <li key={index}>{tag}</li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          </div>
          <div className="mt-6">
            <h3 className="text-lg font-semibold mb-2">Description</h3>
            {editMode ? (
              <textarea
                name="description"
                value={editedImage.description}
                onChange={handleInputChange}
                className="w-full h-32 border border-gray-300 rounded p-2 focus:border-blue-500 outline-none"
              />
            ) : (
              <p className="text-gray-600">{image.description}</p>
            )}
          </div>
          <div className="mt-6">
            <h3 className="text-lg font-semibold mb-2">Detected Faces</h3>
            <p>Number of faces detected: {faces.length}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ImageDetails;