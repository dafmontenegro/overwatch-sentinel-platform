import React, { useRef, useState, useEffect } from 'react';

interface Video {
  path: string;
  filename: string;
  size_mb: number;
}

interface PlaylistPlayerProps {
  videos: Video[];
}

const API_URL = import.meta.env.VITE_API_URL;

const PlaylistPlayer: React.FC<PlaylistPlayerProps> = ({ videos }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);
  const videoRef = useRef<HTMLVideoElement>(null);

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

  if (videos.length === 0) return <div>No hay videos para reproducir.</div>;

  const currentVideo = videos[currentIndex];
  const videoUrl = `${API_URL}/video/${currentVideo.path}`;

  return (
    <div>
      <h4 className="text-lg font-bold mb-2">{currentVideo.filename}</h4>
      <video
        ref={videoRef}
        src={videoUrl}
        controls
        autoPlay
        onEnded={handleEnded}
        className="w-full max-h-96 bg-black"
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
      />
      <div className="flex gap-2 mt-2">
        <button onClick={handlePrev} disabled={currentIndex === 0} className="px-3 py-1 bg-capri text-white rounded disabled:opacity-50">Anterior</button>
        <button onClick={() => setIsPlaying(!isPlaying)} className="px-3 py-1 bg-capri text-white rounded">
          {isPlaying ? 'Pausar' : 'Reproducir'}
        </button>
        <button onClick={handleNext} disabled={currentIndex === videos.length - 1} className="px-3 py-1 bg-capri text-white rounded disabled:opacity-50">Siguiente</button>
      </div>
      <div className="mt-2 text-sm text-gray-500">
        Video {currentIndex + 1} de {videos.length}
      </div>
    </div>
  );
};

export default PlaylistPlayer; 