import { Folder } from 'lucide-react';
import React from 'react';
import { Link } from 'react-router-dom';

const Album = ({ id, name, coverImage, photoCount }) => {
  return (
    <Link to={`/albums/${id}`} className="block">
      <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
        <div className="relative aspect-w-16 aspect-h-9">
          {coverImage ? (
            <img src={coverImage} alt={name} className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full bg-gray-200 flex items-center justify-center">
              <Folder className="h-12 w-12 text-gray-400" />
            </div>
          )}
        </div>
        <div className="p-4">
          <h3 className="text-lg font-semibold text-gray-900 truncate">{name}</h3>
          <p className="text-sm text-gray-500">{photoCount} photos</p>
        </div>
      </div>
    </Link>
  );
};

export default Album;