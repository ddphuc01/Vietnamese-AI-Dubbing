/**
 * Constants for Vietnamese AI Dubbing
 */

export const DEFAULT_VOICE_ID = 'vi-VN-NamMinhNeural';
export const DEFAULT_OLLAMA_URL = 'http://localhost:11434';

// API endpoints
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Supported file formats
export const SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.webm'];
export const SUPPORTED_AUDIO_FORMATS = ['.mp3', '.wav', '.flac', '.aac', '.ogg'];

// Maximum file sizes
export const MAX_VIDEO_SIZE = 500 * 1024 * 1024; // 500MB
export const MAX_AUDIO_SIZE = 100 * 1024 * 1024; // 100MB

// Processing options
export const VOICE_OPTIONS = [
  { value: 'vi-VN-NamMinhNeural', label: 'Nam Minh (Nam)' },
  { value: 'vi-VN-HoaiMyNeural', label: 'Hoài My (Nữ)' },
  { value: 'vi-VN-NgocLamNeural', label: 'Ngọc Lam (Nữ)' },
  { value: 'vi-VN-ThanhTungNeural', label: 'Thanh Tùng (Nam)' },
];

export const QUALITY_OPTIONS = [
  { value: '144p', label: '144p' },
  { value: '240p', label: '240p' },
  { value: '360p', label: '360p' },
  { value: '480p', label: '480p' },
  { value: '720p', label: '720p (HD)' },
  { value: '1080p', label: '1080p (Full HD)' },
  { value: '4k', label: '4K (Ultra HD)' },
];

export const RESOLUTION_OPTIONS = [
  { value: '720p', label: '720p (HD)' },
  { value: '1080p', label: '1080p (Full HD)' },
  { value: '4k', label: '4K (Ultra HD)' },
];

export const TRANSLATION_METHODS = [
  { value: 'gtx_free', label: 'Google Translate (Miễn phí)' },
  { value: 'openrouter', label: 'OpenRouter AI' },
  { value: 'ollama', label: 'Ollama (Local)' },
];

// Model options
export const ASR_MODELS = [
  { value: 'WhisperX', label: 'WhisperX' },
  { value: 'FunASR', label: 'FunASR' },
  { value: 'Wav2Vec2', label: 'Wav2Vec2' },
];

export const MODEL_SIZES = [
  { value: 'tiny', label: 'Tiny (Fast)' },
  { value: 'base', label: 'Base' },
  { value: 'small', label: 'Small' },
  { value: 'medium', label: 'Medium' },
  { value: 'large', label: 'Large (Accurate)' },
  { value: 'large-v2', label: 'Large v2' },
];

export const COMPUTE_DEVICES = [
  { value: 'auto', label: 'Tự động' },
  { value: 'cpu', label: 'CPU' },
  { value: 'cuda', label: 'CUDA (GPU)' },
];

// Default settings
export const DEFAULT_SETTINGS = {
  voiceId: DEFAULT_VOICE_ID,
  isMultiSpeaker: false,
  speakerVoices: [DEFAULT_VOICE_ID],
  separationModel: 'htdemucs_ft',
  removeOriginalVocals: true,
  removeInstruments: false,
  asrModel: 'WhisperX',
  modelSize: 'large',
  computeDevice: 'auto',
  batchSize: 32,
  minSpeakers: null,
  maxSpeakers: null,
  translationMethod: 'gtx_free' as const,
  openRouterApiKey: '',
  openRouterModel: 'microsoft/wizardlm-2-8x22b',
  ollamaUrl: DEFAULT_OLLAMA_URL,
  ollamaModel: '',
  addSubs: true,
  speedFactor: 1.0,
  frameRate: 30,
  backgroundMusicFile: null,
  bgMusicVolume: 0.5,
  videoVolume: 1.0,
  resolution: '720p',
};

// UI Constants
export const ITEMS_PER_PAGE = 10;
export const MAX_RECENT_JOBS = 5;
export const TOAST_DURATION = 5000;

// Error messages
export const ERROR_MESSAGES = {
  FILE_TOO_LARGE: 'File quá lớn. Kích thước tối đa là 500MB.',
  UNSUPPORTED_FORMAT: 'Định dạng file không được hỗ trợ.',
  UPLOAD_FAILED: 'Tải lên thất bại. Vui lòng thử lại.',
  PROCESSING_FAILED: 'Xử lý thất bại. Vui lòng thử lại.',
  NETWORK_ERROR: 'Lỗi kết nối mạng. Vui lòng kiểm tra kết nối internet.',
  API_ERROR: 'Lỗi API. Vui lòng thử lại sau.',
};

// Success messages
export const SUCCESS_MESSAGES = {
  FILE_UPLOADED: 'File đã được tải lên thành công.',
  PROCESSING_STARTED: 'Đã bắt đầu xử lý video.',
  PROCESSING_COMPLETED: 'Xử lý video thành công!',
  SETTINGS_SAVED: 'Cài đặt đã được lưu.',
  JOB_DELETED: 'Job đã được xóa.',
};

// Loading messages
export const LOADING_MESSAGES = {
  UPLOADING: 'Đang tải lên...',
  PROCESSING: 'Đang xử lý...',
  DOWNLOADING: 'Đang tải xuống...',
  ANALYZING: 'Đang phân tích...',
  TRANSCRIBING: 'Đang chuyển văn bản...',
  TRANSLATING: 'Đang dịch...',
  GENERATING_AUDIO: 'Đang tạo audio...',
  MERGING: 'Đang hợp nhất...',
};