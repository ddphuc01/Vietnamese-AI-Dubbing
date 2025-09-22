/**
 * React Router Configuration
 */

import { createBrowserRouter, Navigate } from 'react-router-dom';
import App from '../App';
import HomePage from '../pages/HomePage';
import VideoProcessingPage from '../pages/VideoProcessingPage';
import JobsPage from '../pages/JobsPage';
import SettingsPage from '../pages/SettingsPage';
import AboutPage from '../pages/AboutPage';

// Lazy load components for better performance
const HomePage = lazy(() => import('../pages/HomePage'));
const VideoProcessingPage = lazy(() => import('../pages/VideoProcessingPage'));
const JobsPage = lazy(() => import('../pages/JobsPage'));
const SettingsPage = lazy(() => import('../pages/SettingsPage'));
const AboutPage = lazy(() => import('../pages/AboutPage'));

export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      {
        index: true,
        element: <Navigate to="/home" replace />,
      },
      {
        path: 'home',
        element: <HomePage />,
      },
      {
        path: 'video-processing',
        element: <VideoProcessingPage />,
      },
      {
        path: 'jobs',
        element: <JobsPage />,
      },
      {
        path: 'settings',
        element: <SettingsPage />,
      },
      {
        path: 'about',
        element: <AboutPage />,
      },
      {
        path: '*',
        element: <Navigate to="/home" replace />,
      },
    ],
  },
]);

export default router;