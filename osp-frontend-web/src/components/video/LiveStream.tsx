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

  const handlePlayPause = () => setIsPlaying(!isPlaying);

  const handleMute = () => setIsMuted(!isMuted);

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

  return (
    <div className="flex-1 flex justify-center items-center">
      <div className="relative w-full max-w-screen-xl flex items-center justify-center bg-black aspect-video">
        {isLoading && (
          <div className="absolute inset-0 flex justify-center items-center">
            <LoadingSpinner />
          </div>
        )}

        {error && (
          <div className="absolute inset-0 flex flex-col justify-center items-center text-center p-4">
            <p className="text-red-400 mb-4">{error}</p>
            <button
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              onClick={() => window.location.reload()}
            >
              Reintentar
            </button>
          </div>
        )}

        {!isLoading && !error && (
          <>
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
          </>
        )}
      </div>
    </div>
  );
};

export default LiveStream;