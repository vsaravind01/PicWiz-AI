
import { User } from 'lucide-react';
import React from 'react';
import { Link } from 'react-router-dom';

const Person = ({ id, name, avatar, photoCount }) => {
  return (
    <Link to={`/people/${id}`} className="block">
      <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
        <div className="p-4 flex items-center">
          {avatar ? (
            <img src={avatar} alt={name} className="w-16 h-16 rounded-full object-cover" />
          ) : (
            <div className="w-16 h-16 rounded-full bg-gray-200 flex items-center justify-center">
              <User className="h-8 w-8 text-gray-400" />
            </div>
          )}
          <div className="ml-4">
            <h3 className="text-lg font-semibold text-gray-900">{name}</h3>
            <p className="text-sm text-gray-500">{photoCount} photos</p>
          </div>
        </div>
      </div>
    </Link>
  );
};

export default Person;