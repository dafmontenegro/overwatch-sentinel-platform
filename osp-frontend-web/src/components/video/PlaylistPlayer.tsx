import React, { useRef, useState, useEffect } from 'react';
import { fetchRecordingsByDate } from '../../services/videoService';

interface PlaylistPlayerProps {
  date: string;
}

const API_URL = import.meta.env.VITE_API_URL;

const PlaylistPlayer: React.FC<PlaylistPlayerProps> = ({ date }) => {
  const [videos, setVideos] = useState<{ path: string; filename: string; size_mb: number }[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const loadVideos = async () => {
      setLoading(true);
      setError(null);
      setVideos([]);
      setCurrentIndex(0);
      try {
        const vids = await fetchRecordingsByDate(date);
        setVideos(vids);
      } catch (err) {
        setError('Error al cargar los videos');
      } finally {
        setLoading(false);
      }
    };
    loadVideos();
  }, [date]);

  useEffect(() => {
    if (isPlaying) {
      videoRef.current?.play();
    } else {
      videoRef.current?.pause();
    }
  }, [isPlaying, currentIndex]);

  const handleEnded = () => {
    if (currentIndex < videos.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setIsPlaying(true);
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      setIsPlaying(true);
    }
  };

  const handleNext = () => {
    if (currentIndex < videos.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setIsPlaying(true);
    }
  };

  if (loading) return <div>Cargando videos...</div>;
  if (error) return <div className="text-red-500">{error}</div>;
  if (videos.length === 0) return <div>No hay videos para reproducir.</div>;

  const currentVideo = videos[currentIndex];
  const videoUrl = `${API_URL}/videos/${currentVideo.path}`;
  console.log(videoUrl);

  return (
    <div className="flex flex-col items-center w-full max-w-4xl mx-auto p-2 sm:p-4">
      <h4 className="text-lg font-bold mb-2 text-center break-all">{currentVideo.filename}</h4>
      <div className="w-full flex justify-center">
        <video
          ref={videoRef}
          src={videoUrl}
          controls
          autoPlay
          onEnded={handleEnded}
          className="w-full max-w-3xl h-auto max-h-[60vw] sm:max-h-96 bg-black rounded-lg shadow-md"
          style={{ aspectRatio: '16/9' }}
          onPlay={() => setIsPlaying(true)}
          onPause={() => setIsPlaying(false)}
        />
      </div>
      <div className="flex flex-col sm:flex-row gap-2 mt-4 w-full justify-center items-center">
        <button
          onClick={handlePrev}
          disabled={currentIndex === 0}
          className="px-4 py-2 bg-capri text-white rounded disabled:opacity-50 w-full sm:w-auto"
        >Anterior</button>
        <button
          onClick={() => setIsPlaying(!isPlaying)}
          className="px-4 py-2 bg-capri text-white rounded w-full sm:w-auto"
        >
          {isPlaying ? 'Pausar' : 'Reproducir'}
        </button>
        <button
          onClick={handleNext}
          disabled={currentIndex === videos.length - 1}
          className="px-4 py-2 bg-capri text-white rounded disabled:opacity-50 w-full sm:w-auto"
        >Siguiente</button>
      </div>
      <div className="mt-2 text-sm text-gray-500 text-center">
        Video {currentIndex + 1} de {videos.length}
      </div>
    </div>
  );
};

export default PlaylistPlayer; 