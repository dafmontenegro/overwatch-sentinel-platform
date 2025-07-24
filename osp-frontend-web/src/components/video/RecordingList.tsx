import React from 'react';
import PlaylistPlayer from './PlaylistPlayer';

interface RecordingListProps {
  date: string | null;
}

const RecordingList: React.FC<RecordingListProps> = ({ date }) => {
  if (!date) {
    return <div className="text-gray-500">Selecciona un día con grabaciones.</div>;
  }

  return (
    <div>
      <h3 className="text-lg font-semibold mb-2">Grabaciones de {date}</h3>
      <PlaylistPlayer date={date} />
    </div>
  );
};

export default RecordingList; 