import type { Stream } from '../types/video.types';

const API_URL = import.meta.env.VITE_API_URL;

// Función para obtener la URL del stream de video
export const getVideoStreamUrl = async (_cameraId: string): Promise<string> => {
  // En este caso, simplemente devolvemos la URL del endpoint de video_feed
  return `${API_URL}/stream`;
};

// Función para obtener la lista de cámaras disponibles
export const fetchAvailableCameras = async (): Promise<Stream[]> => {
  try {
    //const token = localStorage.getItem('token');
    //if (!token) throw new Error('Token no encontrado');

    return [
      {
        id: 'cam-1',
        name: 'Cámara Principal',
        url: `${API_URL}/stream`,
        cameraId: 'cam-1',
        status: 'online'
      }
    ];
  } catch (error) {
    console.error('Error fetching cameras:', error);
    throw error;
  }
};

export const fetchRecordingsByDate = async (date: string): Promise<{ path: string; filename: string; size_mb: number }[]> => {
  try {
    const res = await fetch(`${API_URL}/events`);
    if (!res.ok) throw new Error('Error al obtener grabaciones');
    const data = await res.json();
    const events = data.events || [];
    const event = events.find((e: any) => e.date === date);
    if (!event || !event.hours) return [];
    // Unir todos los videos del día en un solo array plano
    const allVideos = event.hours.flatMap((hour: any) =>
      (hour.videos || []).map((video: any) => ({
        path: video.path,
        filename: video.filename,
        size_mb: video.size_mb || 0,
      }))
    );
    return allVideos;
  } catch (error) {
    console.error('Error fetching recordings by date:', error);
    throw error;
  }
};

export const fetchRecordingEvents = async (): Promise<any> => {
  try {
    const res = await fetch(`${API_URL}/events`);
    if (!res.ok) throw new Error('Error al obtener grabaciones');
    return await res.json();
  } catch (error) {
    console.error('Error fetching recording events:', error);
    throw error;
  }
};