/**
 * Main App Component with React Router and FastAPI Integration
 */

import React, { useEffect } from 'react';
import { RouterProvider } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { Notifications } from '@mantine/notifications';
import { router } from './router';
import { useAppStore } from './store/useAppStore';
import { api } from './api/client';
import './App.css';

const App: React.FC = () => {
  const { setLoading, setError, setSuccess } = useAppStore();

  useEffect(() => {
    // Initialize app
    const initializeApp = async () => {
      try {
        setLoading(true);

        // Test API connection
        const response = await api.health.basic();
        console.log('API Connection:', response.data);

        setSuccess('Kết nối API thành công');
      } catch (error) {
        console.error('API Connection failed:', error);
        setError('Không thể kết nối với API backend');
      } finally {
        setLoading(false);
      }
    };

    initializeApp();
  }, [setLoading, setError, setSuccess]);

  return (
    <MantineProvider
      theme={{
        colorScheme: 'dark',
        primaryColor: 'orange',
        colors: {
          orange: [
            '#fff4e6',
            '#ffe8cc',
            '#ffd8a8',
            '#ffc078',
            '#ffac4d',
            '#ff9d2e',
            '#ff9419',
            '#e8850e',
            '#d4790a',
            '#c06b08',
          ],
        },
      }}
      withGlobalStyles
      withNormalizeCSS
    >
      <Notifications position="top-right" />
      <RouterProvider router={router} />
    </MantineProvider>
  );
};

export default App;