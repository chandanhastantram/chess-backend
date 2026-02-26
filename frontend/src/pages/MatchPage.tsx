import { useParams } from 'react-router-dom';
import { Chessboard } from '../components/Chessboard';
import { Clock } from '../components/Clock';
import { MoveList } from '../components/MoveList';
import { useGameStore } from '../store/gameStore';
import { useWebSocket } from '../hooks/useWebSocket';
import { useAuthStore } from '../store/authStore';
import { Flag, Handshake, SkipBack, ChevronLeft, ChevronRight, SkipForward, RotateCcw, Eye } from 'lucide-react';

export const MatchPage = () => {
  const { gameId } = useParams<{ gameId: string }>();
  const {
    white_time, black_time, turn, moves,
    isSpectator, spectatorCount,
    status, result, termination
  } = useGameStore();

  const { resign, offerDraw } = useWebSocket(gameId || null);
  const { user } = useAuthStore();

  return (
    <div className="min-h-[calc(100vh-48px)] bg-surface-100 flex items-start justify-center p-4 pt-6 gap-4">
      {/* Board + Clocks */}
      <div className="flex flex-col gap-2 w-full max-w-[560px]">
        {/* Opponent clock (top) */}
        <Clock
          timeMs={black_time}
          isActive={status === 'active' && turn === 'black'}
          playerName="Opponent"
          rating={1500}
          isWhite={false}
        />

        {/* Board */}
        <Chessboard />

        {/* Your clock (bottom) */}
        <Clock
          timeMs={white_time}
          isActive={status === 'active' && turn === 'white'}
          playerName={user?.username || 'You'}
          rating={1200}
          isWhite={true}
        />
      </div>

      {/* Right Panel */}
      <div className="w-80 flex flex-col gap-2 h-[560px]">
        {/* Move List */}
        <div className="flex-1 min-h-0">
          <MoveList moves={moves} />
        </div>

        {/* Move Navigation */}
        <div className="flex gap-1">
          <button className="btn-icon flex-1"><SkipBack size={16} /></button>
          <button className="btn-icon flex-1"><ChevronLeft size={16} /></button>
          <button className="btn-icon flex-1"><ChevronRight size={16} /></button>
          <button className="btn-icon flex-1"><SkipForward size={16} /></button>
        </div>

        {/* Game Actions */}
        {!isSpectator && status === 'active' && (
          <div className="flex gap-2 mt-4">
            <button
              onClick={offerDraw}
              className="btn-secondary flex-1 flex items-center justify-center gap-2 !py-2 text-sm"
            >
              <Handshake size={16} /> Draw
            </button>
            <button
              onClick={resign}
              className="flex-1 flex items-center justify-center gap-2 bg-accent-red/10 hover:bg-accent-red/20 text-accent-red rounded-md py-2 text-sm font-bold transition-all hover:-translate-y-1 active:scale-95 shadow-[0_4px_0_0_rgba(224,40,40,0.2)] hover:shadow-[0_4px_0_0_rgba(224,40,40,0.3)] active:shadow-none active:translate-y-1"
            >
              <Flag size={16} /> Resign
            </button>
          </div>
        )}

        {/* Spectator bar */}
        {isSpectator && (
          <div className="flex items-center gap-2 px-3 py-2 bg-surface-300 rounded-md text-sm text-text-muted mt-4">
            <Eye size={14} />
            <span>Spectating • {spectatorCount} viewers</span>
          </div>
        )}

        {/* Game Over Banner */}
        {status === 'completed' && (
          <div className="card p-4 border border-accent-green/30 text-center space-y-3 mt-4 animate-slide-up">
            <div className="text-lg font-bold">
              {result === '1-0' ? 'White wins!' : result === '0-1' ? 'Black wins!' : 'Draw!'}
            </div>
            <div className="text-sm text-text-muted">by {termination}</div>
            <div className="flex gap-2">
              <button className="btn-primary flex-1 !py-2 text-sm flex items-center justify-center gap-2">
                <RotateCcw size={14} /> Rematch
              </button>
              <button className="btn-secondary flex-1 !py-2 text-sm">New Game</button>
            </div>
          </div>
        )}

        {/* Game info footer */}
        <div className="text-xs text-text-dim text-center">
          Game #{gameId?.slice(0, 8)} • {spectatorCount} watching
        </div>
      </div>
    </div>
  );
};
