/**
 * API Client for Vietnamese AI Dubbing FastAPI Backend
 */

import axios, { AxiosInstance, AxiosResponse } from 'axios';

// API Base URL - adjust this to match your backend URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API Response types
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  success: boolean;
}

export interface Job {
  id: number;
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  input_type: string;
  input_filename?: string;
  output_filename?: string;
  created_at: string;
  updated_at: string;
  started_at?: string;
  completed_at?: string;
  processing_time?: number;
  error_message?: string;
}

export interface JobStats {
  total_jobs: number;
  status_counts: Record<string, number>;
  average_processing_time_seconds?: number;
  success_rate: number;
}

export interface VideoProcessingRequest {
  video_file?: File;
  video_url?: string;
  youtube_url?: string;
  options?: Record<string, any>;
}

export interface VideoProcessingResponse {
  job_id: string;
  status: string;
  message: string;
  estimated_time: string;
}

// API Endpoints
export const api = {
  // Health checks
  health: {
    basic: () => apiClient.get('/health'),
    detailed: () => apiClient.get('/health/detailed'),
    ready: () => apiClient.get('/health/ready'),
  },

  // Jobs
  jobs: {
    list: (params?: {
      status?: string;
      user_id?: string;
      limit?: number;
      offset?: number;
    }) => apiClient.get<Job[]>('/jobs', { params }),

    get: (jobId: string) => apiClient.get<Job>(`/jobs/${jobId}`),

    delete: (jobId: string) => apiClient.delete(`/jobs/${jobId}`),

    stats: () => apiClient.get<JobStats>('/jobs/stats/summary'),
  },

  // Video Processing
  video: {
    process: (data: FormData) =>
      apiClient.post<VideoProcessingResponse>('/video/process', data, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }),

    status: (jobId: string) => apiClient.get(`/video/status/${jobId}`),

    download: (jobId: string) => apiClient.get(`/video/download/${jobId}`),

    cancel: (jobId: string) => apiClient.post(`/video/cancel/${jobId}`),

    supportedFormats: () => apiClient.get('/video/supported-formats'),
  },

  // Users
  users: {
    list: (params?: { skip?: number; limit?: number }) =>
      apiClient.get('/users', { params }),

    get: (userId: number) => apiClient.get(`/users/${userId}`),

    getByEmail: (email: string) => apiClient.get(`/users/by-email/${email}`),

    stats: () => apiClient.get('/users/stats/summary'),
  },
};

export default apiClient;