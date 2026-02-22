import { useNavigate } from 'react-router-dom';
import { Crown, Zap, Clock, Timer, BookOpen, Puzzle, Trophy, Users, Bot, Swords } from 'lucide-react';

export const PlayPage = () => {
  const navigate = useNavigate();

  const timeControls = [
    { label: '1 min', sub: 'Bullet', icon: Zap, time: '1+0', color: 'text-yellow-400' },
    { label: '1 | 1', sub: 'Bullet', icon: Zap, time: '1+1', color: 'text-yellow-400' },
    { label: '2 | 1', sub: 'Bullet', icon: Zap, time: '2+1', color: 'text-yellow-400' },
    { label: '3 min', sub: 'Blitz', icon: Clock, time: '3+0', color: 'text-accent-orange' },
    { label: '3 | 2', sub: 'Blitz', icon: Clock, time: '3+2', color: 'text-accent-orange' },
    { label: '5 min', sub: 'Blitz', icon: Clock, time: '5+0', color: 'text-accent-orange' },
    { label: '10 min', sub: 'Rapid', icon: Timer, time: '10+0', color: 'text-accent-green' },
    { label: '15 | 10', sub: 'Rapid', icon: Timer, time: '15+10', color: 'text-accent-green' },
    { label: '30 min', sub: 'Classical', icon: BookOpen, time: '30+0', color: 'text-text-muted' },
  ];

  return (
    <div className="min-h-[calc(100vh-48px)] bg-surface-100 flex">
      {/* Left: Quick Links */}
      <div className="hidden lg:flex flex-col w-64 bg-surface-200 border-r border-surface-100 p-4 gap-2">
        <h3 className="text-xs font-bold text-text-dim uppercase tracking-wider mb-2 px-3">Quick Play</h3>
        {[
          { icon: Crown, label: 'New Game', active: true },
          { icon: Bot, label: 'Play Computer' },
          { icon: Swords, label: 'Challenge Friend' },
          { icon: Trophy, label: 'Tournaments' },
        ].map((item) => {
          const Icon = item.icon;
          return (
            <button
              key={item.label}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-bold w-full text-left transition-colors ${
                item.active
                  ? 'bg-surface-400 text-accent-green'
                  : 'text-text-muted hover:bg-surface-300 hover:text-text'
              }`}
            >
              <Icon size={18} />
              {item.label}
            </button>
          );
        })}

        <div className="border-t border-surface-400 my-3" />

        <h3 className="text-xs font-bold text-text-dim uppercase tracking-wider mb-2 px-3">More</h3>
        {[
          { icon: Puzzle, label: 'Puzzles' },
          { icon: BookOpen, label: 'Lessons' },
          { icon: Users, label: 'Community' },
        ].map((item) => {
          const Icon = item.icon;
          return (
            <button
              key={item.label}
              className="flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-bold text-text-muted hover:bg-surface-300 hover:text-text w-full text-left transition-colors"
            >
              <Icon size={18} />
              {item.label}
            </button>
          );
        })}
      </div>

      {/* Center: Time Controls */}
      <div className="flex-1 p-6 max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">Play Chess</h1>

        {/* Main Play Button */}
        <div className="card p-6 mb-6">
          <button className="btn-primary w-full text-xl !py-4 flex items-center justify-center gap-3">
            <Crown size={24} />
            Play
          </button>
          <p className="text-center text-text-dim text-sm mt-3">
            Play a rated game against a player of your skill level
          </p>
        </div>

        {/* Time Controls Grid */}
        <div className="card p-4">
          <h2 className="text-sm font-bold text-text-muted mb-4 px-2">Time Control</h2>
          <div className="grid grid-cols-3 gap-2">
            {timeControls.map((tc) => {
              const Icon = tc.icon;
              return (
                <button
                  key={tc.time}
                  className="flex flex-col items-center gap-1 p-4 rounded-md bg-surface-200 hover:bg-surface-400 transition-colors group"
                >
                  <Icon size={20} className={tc.color} />
                  <span className="text-lg font-bold group-hover:text-accent-green transition-colors">{tc.label}</span>
                  <span className="text-xs text-text-dim">{tc.sub}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Quick Challenge */}
        <div className="grid grid-cols-2 gap-4 mt-4">
          <button
            onClick={() => navigate('/play/computer')}
            className="card p-4 flex items-center gap-3 hover:bg-surface-400 transition-colors"
          >
            <div className="w-10 h-10 rounded-md bg-surface-200 flex items-center justify-center">
              <Bot size={20} className="text-accent-green" />
            </div>
            <div className="text-left">
              <div className="text-sm font-bold">Play Computer</div>
              <div className="text-xs text-text-dim">Choose your difficulty</div>
            </div>
          </button>
          <button className="card p-4 flex items-center gap-3 hover:bg-surface-400 transition-colors">
            <div className="w-10 h-10 rounded-md bg-surface-200 flex items-center justify-center">
              <Swords size={20} className="text-accent-orange" />
            </div>
            <div className="text-left">
              <div className="text-sm font-bold">Challenge Friend</div>
              <div className="text-xs text-text-dim">Send a game invite</div>
            </div>
          </button>
        </div>
      </div>

      {/* Right: Online Players */}
      <div className="hidden xl:flex flex-col w-72 bg-surface-200 border-l border-surface-100 p-4">
        <h3 className="text-xs font-bold text-text-dim uppercase tracking-wider mb-3 px-2">Players Online</h3>
        <div className="flex items-center gap-2 mb-4 px-2">
          <div className="w-2 h-2 rounded-full bg-accent-green" />
          <span className="text-sm text-text-muted">1,248 players online</span>
        </div>

        <h3 className="text-xs font-bold text-text-dim uppercase tracking-wider mb-3 px-2 mt-4">Live Games</h3>
        {[
          { w: 'Magnus', b: 'Hikaru', time: '3+0', moves: 24 },
          { w: 'GothamChess', b: 'BotezLive', time: '5+0', moves: 18 },
          { w: 'DrDrunkenstein', b: 'ChessKing', time: '1+0', moves: 31 },
        ].map((game, i) => (
          <button
            key={i}
            className="w-full px-3 py-2 rounded-md hover:bg-surface-300 transition-colors text-left mb-1"
          >
            <div className="flex justify-between items-center">
              <span className="text-sm font-bold">{game.w}</span>
              <span className="text-xs text-text-dim">{game.time}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-text-muted">{game.b}</span>
              <span className="text-xs text-text-dim">Move {game.moves}</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};
