import React, { useState } from 'react';
import VideoPlayer from './VideoPlayer';
import VideoControls from './VideoControls';
import { useVideoStream } from '../../hooks/useVideoStream';
import LoadingSpinner from '../common/LoadingSpinner';
import type { Stream } from '../../types/video.types';

const LiveStream: React.FC<Stream> = ({ cameraId }) => {
  const { streamUrl, isLoading, error } = useVideoStream(cameraId);
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [isMuted, setIsMuted] = useState<boolean>(false);
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleMute = () => {
    setIsMuted(!isMuted);
  };

  const handleFullscreen = (element: HTMLElement | null) => {
    if (!element) return;

    if (!document.fullscreenElement) {
      element.requestFullscreen().then(() => {
        setIsFullscreen(true);
      }).catch(err => {
        console.error(`Error attempting to enable fullscreen: ${err.message}`);
      });
    } else {
      document.exitFullscreen().then(() => {
        setIsFullscreen(false);
      }).catch(err => {
        console.error(`Error attempting to exit fullscreen: ${err.message}`);
      });
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64 bg-gray-100 rounded-lg">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-64 bg-gray-100 rounded-lg">
        <p className="text-red-500 mb-4">{error}</p>
        <button 
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          onClick={() => window.location.reload()}
        >
          Reintentar
        </button>
      </div>
    );
  }

  return (
    <div className='flex justify-center items-center min-h-[78vh]'>
      <div className="relative bg-black rounded-lg max-w-[105vh] max-h-[79vh] aspect-[4/3] w-full h-full">
        <VideoPlayer 
          streamUrl={streamUrl} 
          isPlaying={isPlaying}
          isMuted={isMuted}
        />
        <VideoControls 
          isPlaying={isPlaying} 
          isMuted={isMuted} 
          isFullscreen={isFullscreen}
          onPlayPause={handlePlayPause}
          onMute={handleMute}
          onFullscreen={handleFullscreen}
        />
      </div>
    </div>
  );
};

export default LiveStream;