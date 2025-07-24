import React from 'react';
import PlaylistPlayer from './PlaylistPlayer';

interface RecordingListProps {
  date: string | null;
  recordingEvent?: {
    date: string;
    hours: { time: string; videos: any[] }[];
  };
}

const RecordingList: React.FC<RecordingListProps> = ({ date, recordingEvent }) => {
  if (!date) {
    return <div className="text-gray-500">Selecciona un día con grabaciones.</div>;
  }
  if (!recordingEvent || recordingEvent.hours.length === 0) {
    return <div className="text-gray-500">No hay grabaciones para este día.</div>;
  }

  // Unir todos los videos del día en un solo array ordenado
  const allVideos = recordingEvent.hours.flatMap(hour => hour.videos);

  return (
    <div>
      <h3 className="text-lg font-semibold mb-2">Grabaciones de {date}</h3>
      <PlaylistPlayer videos={allVideos} />
    </div>
  );
};

export default RecordingList; 