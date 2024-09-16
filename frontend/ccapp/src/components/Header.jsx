import React, { useState } from 'react';
import { Link, useHistory } from 'react-router-dom';

const Header = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const history = useHistory();

  const handleSearch = (e) => {
    e.preventDefault();
    history.push(`/search?q=${searchQuery}`);
  };

  return (
    <header className="bg-blue-500 text-white p-4">
      <div className="container mx-auto flex justify-between items-center">
        <nav>
          <ul className="flex space-x-4">
            <li><Link to="/">Home</Link></li>
            <li><Link to="/albums">Albums</Link></li>
            <li><Link to="/people">People</Link></li>
          </ul>
        </nav>
        <form onSubmit={handleSearch} className="flex">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search photos..."
            className="px-2 py-1 text-black"
          />
          <button type="submit" className="bg-white text-blue-500 px-4 py-1 ml-2">Search</button>
        </form>
      </div>
    </header>
  );
};

export default Header;