// App.jsx
import React, { Suspense, lazy, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthContext } from './components/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import MainLayout from './components/MainLayout';

// Lazy load pages
const Login = lazy(() => import('./pages/Login'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Vessels = lazy(() => import('./pages/Vessels'));
const Ports = lazy(() => import('./pages/Ports'));
const Trains = lazy(() => import('./pages/Trains'));
const Plants = lazy(() => import('./pages/Plants'));
const Optimization = lazy(() => import('./pages/Optimization'));
const Report = lazy(() => import('./pages/Report'));
const DataManagement = lazy(() => import('./pages/DataManagement'));

const App = () => {
  const { isAuthenticated } = useContext(AuthContext);

  return (
    <Router>
      <Suspense fallback={<div>Loading...</div>}>
        <Routes>
          {/* Public Route */}
          <Route path="/login" element={<Login />} />

          {/* Root redirect */}
          <Route
            path="/"
            element={
              isAuthenticated ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />
            }
          />

          {/* Protected layout with sidebar */}
          <Route
            element={
              <ProtectedRoute>
                <MainLayout />
              </ProtectedRoute>
            }
          >
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/plants" element={<Plants />} />
            <Route path="/trains" element={<Trains />} />
            <Route path="/ports" element={<Ports />} />
            <Route path="/vessels" element={<Vessels />} />
            <Route path="/optimization" element={<Optimization />} />
            <Route path="/data-management" element={<DataManagement />} />
          </Route>

          {/* Catch-all */}
          <Route path="*" element={<div>404 Not Found</div>} />
        </Routes>
      </Suspense>
    </Router>
  );
};

export default App;
