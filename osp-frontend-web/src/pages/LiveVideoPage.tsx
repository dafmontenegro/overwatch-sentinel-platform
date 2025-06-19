import React, { useState, useEffect } from 'react';
import DashboardLayout from '../layouts/DashboardLayout';
import LiveStream from '../components/video/LiveStream';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { fetchAvailableCameras } from '../services/videoService';
import type { Stream } from '../types/video.types';

const LiveVideoPage: React.FC = () => {
  const [selectedCamera, setSelectedCamera] = useState<string | null>(null);
  const [cameras, setCameras] = useState<Stream[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadCameras = async () => {
      try {
        setLoading(true);
        const availableCameras = await fetchAvailableCameras();
        setCameras(availableCameras);
        
        // Seleccionar automáticamente la primera cámara si hay disponibles
        if (availableCameras.length > 0) {
          setSelectedCamera(availableCameras[0].id);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error al cargar las cámaras');
        console.error('Error loading cameras:', err);
      } finally {
        setLoading(false);
      }
    };

    loadCameras();
  }, []);

  return (
    <DashboardLayout>
      <div className="p-6">
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <LoadingSpinner />
          </div>
        ) : error ? (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            Error al cargar las transmisiones: {error}
          </div>
        ) : (
          <>
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Seleccionar Cámara
              </label>
              <select 
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 rounded-md"
                value={selectedCamera || ''}
                onChange={(e) => setSelectedCamera(e.target.value)}
              >
                <option value="">Selecciona una cámara</option>
                {cameras.map(camera => (
                  <option key={camera.id} value={camera.id}>
                    {camera.name} ({camera.status === 'online' ? 'En línea' : 'Desconectada'})
                  </option>
                ))}
              </select>
            </div>
            
            {selectedCamera ? (
              <LiveStream cameraId={selectedCamera} id={''} name={''} url={''} status={'error'} />
            ) : (
              <div className="flex-1 flex justify-center items-center">
                <div className="w-full max-w-screen-xl flex items-center justify-center bg-black aspect-video">
                  <p className="text-gray-400 text-center px-4">
                    Selecciona una cámara para ver la transmisión en vivo
                  </p>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </DashboardLayout>
  );
};

export default LiveVideoPage;