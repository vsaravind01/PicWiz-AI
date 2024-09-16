import { Search } from "lucide-react";
import React, { useState } from "react";
import { Link, Route, BrowserRouter as Router, Routes } from "react-router-dom";

// Placeholder components (to be implemented)
import ImageDetails from "./components/ImageDetails";
import AlbumPage from "./pages/AlbumPage";
import HomePage from "./pages/HomePage";
import PersonPage from "./pages/PersonPage";
import QueryResultsPage from "./pages/QueryResultsPage";

const App = () => {
    const [searchQuery, setSearchQuery] = useState("");
    const [selectedImage, setSelectedImage] = useState(null);

    const handleSearch = (e) => {
        e.preventDefault();
        // Implement search logic here
    };

    return (
        <Router>
            <div className="min-h-screen bg-gray-100">
                <nav className="bg-white shadow-md">
                    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                        <div className="flex justify-between h-16">
                            <div className="flex">
                                <Link
                                    to="/"
                                    className="flex-shrink-0 flex items-center"
                                >
                                    <img
                                        className="h-8 w-auto"
                                        src="/api/placeholder/32/32"
                                        alt="Logo"
                                    />
                                    <span className="ml-2 text-xl font-bold">
                                        Photo App
                                    </span>
                                </Link>
                                <div className="ml-6 flex space-x-8">
                                    <Link
                                        to="/"
                                        className="text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 border-indigo-500 text-sm font-medium"
                                    >
                                        Home
                                    </Link>
                                    <Link
                                        to="/albums"
                                        className="text-gray-500 hover:text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium"
                                    >
                                        Albums
                                    </Link>
                                    <Link
                                        to="/people"
                                        className="text-gray-500 hover:text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium"
                                    >
                                        People
                                    </Link>
                                </div>
                            </div>
                            <div className="flex items-center">
                                <form
                                    onSubmit={handleSearch}
                                    className="w-full max-w-lg lg:max-w-xs"
                                >
                                    <label htmlFor="search" className="sr-only">
                                        Search
                                    </label>
                                    <div className="relative">
                                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                            <Search className="h-5 w-5 text-gray-400" />
                                        </div>
                                        <input
                                            id="search"
                                            name="search"
                                            className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                                            placeholder="Search"
                                            type="search"
                                            value={searchQuery}
                                            onChange={(e) =>
                                                setSearchQuery(e.target.value)
                                            }
                                        />
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                </nav>

                <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                    <Routes>
                        <Route exact path="/" component={HomePage} />
                        <Route path="/albums" component={AlbumPage} />
                        <Route path="/people" component={PersonPage} />
                        <Route path="/search" component={QueryResultsPage} />
                    </Routes>
                </main>

                {selectedImage && (
                    <ImageDetails
                        image={selectedImage}
                        onClose={() => setSelectedImage(null)}
                    />
                )}
            </div>
        </Router>
    );
};

export default App;
