import type { Stream, Recording } from '../types/video.types';

const API_URL = import.meta.env.VITE_BACK_API_URL;

// Función para obtener la URL del stream de video
export const getVideoStreamUrl = async (_cameraId: string): Promise<string> => {
  // En este caso, simplemente devolvemos la URL del endpoint de video_feed
  return `${API_URL}/video`;
};

// Función para obtener la lista de cámaras disponibles
export const fetchAvailableCameras = async (): Promise<Stream[]> => {
  try {
    //const token = localStorage.getItem('token');
    
    return [
      {
        id: 'cam-1',
        name: 'Cámara Principal',
        url: `${API_URL}/video`,
        cameraId: 'cam-1',
        status: 'online'
      }
    ];
  } catch (error) {
    console.error('Error fetching cameras:', error);
    throw error;
  }
};

// Otras funciones relacionadas con video...
export const fetchRecordingsByDate = async (date: Date): Promise<Recording[]> => {
  try {
    //const token = localStorage.getItem('token');
    //const formattedDate = date.toISOString().split('T')[0]; // YYYY-MM-DD
    date.toISOString().split('T')[0]; // YYYY-MM-DD
    
    return [
      {
        id: 'rec-1',
        cameraId: 'cam-1',
        timestamp: new Date().toISOString(),
        duration: 120, // 2 minutos
        url: `${API_URL}/recordings/rec-1.mp4`,
        thumbnail: `${API_URL}/thumbnails/rec-1.jpg`,
        detectedObjects: ['Persona', 'Automóvil']
      }
    ];
  } catch (error) {
    console.error('Error fetching recordings:', error);
    throw error;
  }
};