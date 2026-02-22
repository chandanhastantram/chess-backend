import { } from 'react';

interface ClockProps {
  timeMs: number;
  isActive: boolean;
  playerName: string;
  rating?: number;
  isWhite: boolean;
}

export const Clock = ({ timeMs, isActive, playerName, rating, isWhite }: ClockProps) => {
  const formatTime = (ms: number) => {
    const totalSeconds = Math.max(0, Math.floor(ms / 1000));
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;

    if (totalSeconds < 10) {
      const tenths = Math.floor((ms % 1000) / 100);
      return `0:0${seconds}.${tenths}`;
    }
    if (totalSeconds < 60) {
      return `0:${seconds.toString().padStart(2, '0')}`;
    }
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const isLow = timeMs < 30000;
  const isCritical = timeMs < 10000;

  return (
    <div className={`flex items-center justify-between px-3 py-2 rounded transition-colors ${
      isActive ? 'bg-surface-400' : 'bg-surface-300'
    }`}>
      <div className="flex items-center gap-2">
        <div className={`w-8 h-8 rounded flex items-center justify-center text-sm font-bold ${
          isWhite ? 'bg-white text-surface-100' : 'bg-surface-100 text-white'
        }`}>
          {playerName.charAt(0).toUpperCase()}
        </div>
        <div>
          <div className="text-sm font-bold leading-tight">{playerName}</div>
          {rating && <div className="text-xs text-text-muted">({rating})</div>}
        </div>
      </div>

      <div className={`font-mono text-2xl font-bold px-3 py-1 rounded ${
        isCritical
          ? 'bg-accent-red text-white'
          : isLow
            ? 'bg-accent-orange text-white'
            : isActive
              ? 'bg-white text-surface-100'
              : 'bg-surface-500 text-text'
      }`}>
        {formatTime(timeMs)}
      </div>
    </div>
  );
};
