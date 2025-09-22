/**
 * Type definitions for Vietnamese AI Dubbing
 */

export enum DubbingStage {
  IDLE = 'idle',
  DOWNLOADING = 'downloading',
  TRANSCRIBING = 'transcribing',
  TRANSLATING = 'translating',
  GENERATING_AUDIO = 'generating_audio',
  MERGING = 'merging',
  DONE = 'done',
}

export type TranslationMethod = 'gtx_free' | 'openrouter' | 'ollama';

export type OllamaStatus = 'idle' | 'checking' | 'online' | 'offline';

export interface ModelOption {
  name: string;
  id: string;
}

export interface ProcessingOptions {
  voiceId?: string;
  isMultiSpeaker?: boolean;
  speakerVoices?: string[];
  separationModel?: string;
  removeOriginalVocals?: boolean;
  removeInstruments?: boolean;
  asrModel?: string;
  modelSize?: string;
  computeDevice?: string;
  batchSize?: number;
  minSpeakers?: number | null;
  maxSpeakers?: number | null;
  translationMethod?: TranslationMethod;
  openRouterApiKey?: string;
  openRouterModel?: string;
  ollamaUrl?: string;
  ollamaModel?: string;
  addSubs?: boolean;
  speedFactor?: number;
  frameRate?: number;
  backgroundMusicFile?: File | null;
  bgMusicVolume?: number;
  videoVolume?: number;
  resolution?: string;
}

export interface JobStatus {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  message?: string;
  error?: string;
}

export interface VideoInfo {
  duration: number;
  width: number;
  height: number;
  format: string;
  size: number;
}

export interface AudioTrack {
  language: string;
  codec: string;
  channels: number;
  sampleRate: number;
}

export interface SubtitleTrack {
  language: string;
  format: string;
  content: string;
}