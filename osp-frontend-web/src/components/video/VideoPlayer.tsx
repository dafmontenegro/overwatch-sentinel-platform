import React, { useRef, useState, useEffect } from 'react';

interface VideoPlayerProps {
  streamUrl: string;
  isPlaying: boolean;
  isMuted: boolean;
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({ streamUrl, isPlaying }) => {
  const imgRef = useRef<HTMLImageElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [lastFrameUrl, setLastFrameUrl] = useState<string | null>(null);
  
  useEffect(() => {
    // Configurar una nueva imagen para capturar el frame
    if (isPlaying) {
      const captureImg = new Image();
      captureImg.crossOrigin = "anonymous";
      
      captureImg.onload = () => {
        try {
          const canvas = document.createElement('canvas');
          canvas.width = captureImg.naturalWidth || 640;
          canvas.height = captureImg.naturalHeight || 480;
          const ctx = canvas.getContext('2d');
          ctx?.drawImage(captureImg, 0, 0);
          setLastFrameUrl(canvas.toDataURL('image/jpeg'));
        } catch (e) {
          console.error('Error al capturar frame:', e);
        }
      };
      
      // Asignar la URL después de configurar crossOrigin
      captureImg.src = streamUrl;
    }
  }, [isPlaying, streamUrl]);

  return (
    <div ref={containerRef} className="w-full h-full object-contain">
      {/* Imagen del stream en vivo */}
      {isPlaying && (
        <img 
          ref={imgRef}
          src={streamUrl}
          alt="Video en vivo"
          crossOrigin="anonymous"
          className="w-full h-auto"
        />
      )}
      
      {/* Imagen congelada cuando está pausado */}
      {!isPlaying && lastFrameUrl && (
        <img 
          src={lastFrameUrl}
          alt="Video pausado"
          className="w-full h-auto"
        />
      )}
      
      {/* Fallback cuando no hay imagen disponible */}
      {!isPlaying && !lastFrameUrl && (
        <div className="w-full h-64 flex items-center justify-center">
          <p className="text-white">No se pudo capturar la imagen</p>
        </div>
      )}
      
      {/* Icono de play cuando está pausado */}
      {!isPlaying && (
        <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-30">
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            className="h-16 w-16 text-white" 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" 
            />
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" 
            />
          </svg>
        </div>
      )}
    </div>
  );
};

export default VideoPlayer;