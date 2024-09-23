import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import React from 'react';
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import Header from './components/Header';
import Login from './components/Login';
import ProtectedRoute from './components/ProtectedRoute';
import Signup from './components/Signup';
import { AuthProvider } from './contexts/AuthContext';
import Albums from './pages/Albums';
import Home from './pages/Home';
import People from './pages/People';
import Photos from './pages/Photos';
import Search from './pages/Search';

const theme = createTheme();

function App() {
  return (
    <AuthProvider>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Header />
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/" element={<ProtectedRoute><Home /></ProtectedRoute>} />
            <Route path="/photos" element={<ProtectedRoute><Photos /></ProtectedRoute>} />
            <Route path="/people" element={<ProtectedRoute><People /></ProtectedRoute>} />
            <Route path="/albums" element={<ProtectedRoute><Albums /></ProtectedRoute>} />
            <Route path="/search" element={<ProtectedRoute><Search /></ProtectedRoute>} />
          </Routes>
        </Router>
      </ThemeProvider>
    </AuthProvider>
  );
}

export default App;