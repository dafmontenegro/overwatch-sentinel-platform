import React, { useEffect, useState } from 'react';
import DashboardLayout from '../layouts/DashboardLayout';
import Loader from '../components/common/Loader';
import RecordingList from '../components/video/RecordingList';
import CalendarPicker from '../components/video/CalendarPicker';
import { fetchRecordingEvents } from '../services/videoService';

interface RecordingEvent {
  date: string;
  hours: { time: string; videos: any[] }[];
}

const RecordingsPage: React.FC = () => {
  const [events, setEvents] = useState<RecordingEvent[]>([]);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadEvents = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchRecordingEvents();
        setEvents(data.events || []);
      } catch (err) {
        setError('Error al cargar las grabaciones');
      } finally {
        setLoading(false);
      }
    };
    loadEvents();
  }, []);

  const availableDates = events.map(e => e.date);

  return (
    <DashboardLayout>
      <div className="p-6">
        <h2 className="text-2xl font-bold mb-4 text-asphalt">Grabaciones</h2>
        {loading ? (
          <Loader />
        ) : error ? (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">{error}</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <CalendarPicker 
                availableDates={availableDates} 
                selectedDate={selectedDate} 
                onSelectDate={setSelectedDate} 
              />
            </div>
            <div className="md:col-span-2">
              <RecordingList 
                date={selectedDate} 
              />
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default RecordingsPage; 