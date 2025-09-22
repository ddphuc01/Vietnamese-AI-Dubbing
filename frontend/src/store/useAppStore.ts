/**
 * Global App Store using Zustand
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { Job, JobStats } from '../api/client';

interface AppState {
  // UI State
  isLoading: boolean;
  error: string | null;
  success: string | null;

  // Job Management
  jobs: Job[];
  currentJob: Job | null;
  jobStats: JobStats | null;

  // Video Processing
  isProcessing: boolean;
  processingProgress: number;
  processingStatus: string;

  // User
  user: any | null;
  isAuthenticated: boolean;

  // Actions
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setSuccess: (success: string | null) => void;

  // Job Actions
  setJobs: (jobs: Job[]) => void;
  addJob: (job: Job) => void;
  updateJob: (jobId: string, updates: Partial<Job>) => void;
  removeJob: (jobId: string) => void;
  setCurrentJob: (job: Job | null) => void;
  setJobStats: (stats: JobStats | null) => void;

  // Processing Actions
  setProcessing: (processing: boolean) => void;
  setProcessingProgress: (progress: number) => void;
  setProcessingStatus: (status: string) => void;

  // User Actions
  setUser: (user: any | null) => void;
  setAuthenticated: (authenticated: boolean) => void;

  // Utility Actions
  reset: () => void;
  resetProcessing: () => void;
}

const initialState = {
  // UI State
  isLoading: false,
  error: null,
  success: null,

  // Job Management
  jobs: [],
  currentJob: null,
  jobStats: null,

  // Video Processing
  isProcessing: false,
  processingProgress: 0,
  processingStatus: '',

  // User
  user: null,
  isAuthenticated: false,
};

export const useAppStore = create<AppState>()(
  devtools(
    (set, get) => ({
      ...initialState,

      // UI Actions
      setLoading: (isLoading: boolean) => set({ isLoading }),

      setError: (error: string | null) => set({ error }),

      setSuccess: (success: string | null) => set({ success }),

      // Job Actions
      setJobs: (jobs: Job[]) => set({ jobs }),

      addJob: (job: Job) => set((state) => ({
        jobs: [job, ...state.jobs]
      })),

      updateJob: (jobId: string, updates: Partial<Job>) => set((state) => ({
        jobs: state.jobs.map(job =>
          job.job_id === jobId ? { ...job, ...updates } : job
        ),
        currentJob: state.currentJob?.job_id === jobId
          ? { ...state.currentJob, ...updates }
          : state.currentJob
      })),

      removeJob: (jobId: string) => set((state) => ({
        jobs: state.jobs.filter(job => job.job_id !== jobId),
        currentJob: state.currentJob?.job_id === jobId ? null : state.currentJob
      })),

      setCurrentJob: (currentJob: Job | null) => set({ currentJob }),

      setJobStats: (jobStats: JobStats | null) => set({ jobStats }),

      // Processing Actions
      setProcessing: (isProcessing: boolean) => set({ isProcessing }),

      setProcessingProgress: (processingProgress: number) => set({ processingProgress }),

      setProcessingStatus: (processingStatus: string) => set({ processingStatus }),

      // User Actions
      setUser: (user: any | null) => set({ user }),

      setAuthenticated: (isAuthenticated: boolean) => set({ isAuthenticated }),

      // Utility Actions
      reset: () => set(initialState),

      resetProcessing: () => set({
        isProcessing: false,
        processingProgress: 0,
        processingStatus: '',
        currentJob: null
      }),
    }),
    {
      name: 'vietnamese-ai-dubbing-store',
    }
  )
);

// Selectors for commonly used state
export const useJobs = () => useAppStore((state) => state.jobs);
export const useCurrentJob = () => useAppStore((state) => state.currentJob);
export const useJobStats = () => useAppStore((state) => state.jobStats);
export const useProcessing = () => useAppStore((state) => ({
  isProcessing: state.isProcessing,
  progress: state.processingProgress,
  status: state.processingStatus
}));
export const useAuth = () => useAppStore((state) => ({
  user: state.user,
  isAuthenticated: state.isAuthenticated
}));
export const useUI = () => useAppStore((state) => ({
  isLoading: state.isLoading,
  error: state.error,
  success: state.success
}));