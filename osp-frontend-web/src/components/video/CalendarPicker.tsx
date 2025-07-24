import React from 'react';
import { DayPicker } from 'react-day-picker';
import 'react-day-picker/dist/style.css';

interface CalendarPickerProps {
  availableDates: string[];
  selectedDate: string | null;
  onSelectDate: (date: string) => void;
}

const CalendarPicker: React.FC<CalendarPickerProps> = ({ availableDates, selectedDate, onSelectDate }) => {
  // Convierte los strings de fechas a objetos Date
  const available = availableDates.map(dateStr => {
    // Formato esperado: April27
    const match = dateStr.match(/([A-Za-z]+)(\d+)/);
    if (!match) return null;
    const [_, month, day] = match;
    const year = new Date().getFullYear();
    return new Date(`${month} ${day}, ${year}`);
  }).filter(Boolean) as Date[];

  return (
    <div>
      <DayPicker
        mode="single"
        selected={selectedDate 
          ? (() => {
              const match = selectedDate.match(/([A-Za-z]+)(\d+)/);
              if (!match) return undefined;
              const [_, month, day] = match;
              const year = new Date().getFullYear();
              return new Date(`${month} ${day}, ${year}`);
            })()
          : undefined}
        onSelect={date => {
          if (date) {
            // Convierte la fecha seleccionada a formato "MonthDay" (ej: "July11")
            const month = date.toLocaleString('en-US', { month: 'long' });
            const day = date.getDate();
            onSelectDate(`${month}${day}`);
          }
        }}
        modifiers={{ available }}
        modifiersClassNames={{ available: 'bg-capri text-white' }}
        disabled={date => !available.some(av => av.toDateString() === date.toDateString())}
      />
      <style>{`.rdp-day_available { background: #2ec4f1; color: white; }`}</style>
    </div>
  );
};

export default CalendarPicker; 