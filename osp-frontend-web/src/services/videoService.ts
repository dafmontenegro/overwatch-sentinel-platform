import type { Stream, Recording } from '../types/video.types';

// Función para obtener la URL del stream de video
export const getVideoStreamUrl = async (_cameraId: string): Promise<string> => {
  // En este caso, simplemente devolvemos la URL del endpoint de video_feed
  return `/api/video`;
};

// Función para obtener la lista de cámaras disponibles
export const fetchAvailableCameras = async (): Promise<Stream[]> => {
  try {
    const token = localStorage.getItem('token');
    if (!token) throw new Error('Token no encontrado');

    return [
      {
        id: 'cam-1',
        name: 'Cámara Principal',
        url: `/api/video`,
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
        url: `/api/recordings/rec-1.mp4`,
        thumbnail: `/api/thumbnails/rec-1.jpg`,
        detectedObjects: ['Persona', 'Automóvil']
      }
    ];
  } catch (error) {
    console.error('Error fetching recordings:', error);
    throw error;
  }
};