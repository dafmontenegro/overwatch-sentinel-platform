import { useState, useEffect } from 'react';
import { getVideoStreamUrl } from '../services/videoService';

export const useVideoStream = (cameraId: string) => {
  const [streamUrl, setStreamUrl] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStreamUrl = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        // Obtener la URL del stream desde el servicio
        const url = await getVideoStreamUrl(cameraId);
        setStreamUrl(url);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error al cargar el stream de video');
        console.error('Error fetching video stream:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchStreamUrl();

    // Cleanup function
    return () => {
      // Si hay alguna limpieza necesaria, como cancelar solicitudes pendientes
    };
  }, [cameraId]);

  return { streamUrl, isLoading, error };
};