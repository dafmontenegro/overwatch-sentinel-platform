export interface Stream {
  id: string;
  name: string;
  url: string;
  cameraId: string;
  status: 'online' | 'offline' | 'error';
}

export interface Recording {
  id: string;
  cameraId: string;
  timestamp: string; // ISO date string
  duration: number; // in seconds
  url: string;
  thumbnail?: string;
  detectedObjects?: string[];
  zoneId?: string;
}