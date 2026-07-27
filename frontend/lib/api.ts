import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout for image processing
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  timestamp: string;
  version: string;
}

export interface PredictResponse {
  /** Inspection verdict: 'OK' or 'NG' */
  status: string;
  confidence: number;
  processing_time_ms: number;
  timestamp: string;
  model_version: string;
}

export interface ModelInfoResponse {
  model_name: string;
  architecture: string;
  training_data: string;
  classes: string[];
  input_size: string;
  framework: string;
  model_loaded: boolean;
  status: string;
}

/**
 * Pings the backend server to check its operational status.
 * Used by the UI to display the connection status indicator.
 * 
 * @returns {Promise<HealthResponse>} The health status of the backend.
 * @throws {Error} If the backend is unreachable or returns an error.
 */
export const healthCheck = async (): Promise<HealthResponse> => {
  try {
    const response = await api.get<HealthResponse>('/health');
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

/**
 * Sends a base64 encoded image to the backend for AI analysis.
 * 
 * @param {string} imageData - The base64 encoded image string.
 * @returns {Promise<PredictResponse>} The classification result and confidence score.
 * @throws {Error} If the prediction fails or the backend rejects the payload.
 */
export const predictImage = async (imageData: string): Promise<PredictResponse> => {
  try {
    const response = await api.post<PredictResponse>('/predict', {
      image: imageData
    });
    return response.data;
  } catch (error) {
    console.error('Prediction failed:', error);
    throw error;
  }
};

/**
 * Retrieves metadata about the currently loaded Machine Learning model.
 * 
 * @returns {Promise<ModelInfoResponse>} Model architecture, version, and threshold details.
 * @throws {Error} If the backend is unreachable.
 */
export const getModelInfo = async (): Promise<ModelInfoResponse> => {
  try {
    const response = await api.get<ModelInfoResponse>('/info');
    return response.data;
  } catch (error) {
    console.error('Failed to get model info:', error);
    throw error;
  }
};

export default api;
