import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Crown, Zap, Clock, Timer, BookOpen, Puzzle, Trophy, Users, Bot, Swords, Loader2, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const stagger = { hidden: {}, show: { transition: { staggerChildren: 0.05 } } };
const fadeUp = {
  hidden: { opacity: 0, y: 15 },
  show: { opacity: 1, y: 0, transition: { duration: 0.35, ease: [0, 0, 0.2, 1] as const } }
};

export const PlayPage = () => {
  const navigate = useNavigate();
  const [searching, setSearching] = useState(false);
  const [selectedTime, setSelectedTime] = useState('');

  const timeControls = [
    { label: '1 min', sub: 'Bullet', icon: Zap, time: '1+0' },
    { label: '1 | 1', sub: 'Bullet', icon: Zap, time: '1+1' },
    { label: '2 | 1', sub: 'Bullet', icon: Zap, time: '2+1' },
    { label: '3 min', sub: 'Blitz', icon: Clock, time: '3+0' },
    { label: '3 | 2', sub: 'Blitz', icon: Clock, time: '3+2' },
    { label: '5 min', sub: 'Blitz', icon: Clock, time: '5+0' },
    { label: '10 min', sub: 'Rapid', icon: Timer, time: '10+0' },
    { label: '15 | 10', sub: 'Rapid', icon: Timer, time: '15+10' },
    { label: '30 min', sub: 'Classical', icon: BookOpen, time: '30+0' },
  ];

  const handlePlay = (time: string) => {
    setSelectedTime(time);
    setSearching(true);
    // TODO: Connect to matchmaking WebSocket
  };

  return (
    <div className="min-h-[calc(100vh-48px)] bg-surface-100 flex relative">
      {/* Searching Overlay */}
      <AnimatePresence>
        {searching && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center"
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              transition={{ type: 'spring', stiffness: 300, damping: 25 }}
              className="card p-8 text-center space-y-6 max-w-sm w-full mx-4"
            >
              <div className="w-20 h-20 rounded-full bg-surface-200 flex items-center justify-center mx-auto animate-glow-pulse">
                <Loader2 size={36} className="text-accent-green animate-spin" />
              </div>
              <div>
                <h3 className="text-xl font-bold mb-1">Finding Opponent...</h3>
                <p className="text-text-muted text-sm">{selectedTime} rated game</p>
              </div>
              <div className="flex gap-1 justify-center">
                {[0,1,2].map(i => (
                  <motion.div
                    key={i}
                    className="w-2 h-2 rounded-full bg-accent-green"
                    animate={{ scale: [1, 1.5, 1], opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
                  />
                ))}
              </div>
              <button
                onClick={() => setSearching(false)}
                className="btn-secondary !py-2 flex items-center justify-center gap-2 w-full"
              >
                <X size={16} /> Cancel
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Left: Quick Links */}
      <motion.div
        className="hidden lg:flex flex-col w-64 bg-surface-200 border-r border-surface-100 p-4 gap-2"
        initial="hidden" animate="show" variants={stagger}
      >
        <h3 className="text-xs font-bold text-text-dim uppercase tracking-wider mb-2 px-3">Quick Play</h3>
        {[
          { icon: Crown, label: 'New Game', active: true },
          { icon: Bot, label: 'Play Computer' },
          { icon: Swords, label: 'Challenge Friend' },
          { icon: Trophy, label: 'Tournaments' },
        ].map((item) => {
          const Icon = item.icon;
          return (
            <motion.button
              key={item.label}
              variants={fadeUp}
              whileHover={{ x: 4 }}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-bold w-full text-left transition-colors ${
                item.active
                  ? 'bg-surface-400 text-accent-green'
                  : 'text-text-muted hover:bg-surface-300 hover:text-text'
              }`}
            >
              <Icon size={18} />
              {item.label}
            </motion.button>
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
            <motion.button
              key={item.label}
              variants={fadeUp}
              whileHover={{ x: 4 }}
              className="flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-bold text-text-muted hover:bg-surface-300 hover:text-text w-full text-left transition-colors"
            >
              <Icon size={18} />
              {item.label}
            </motion.button>
          );
        })}
      </motion.div>

      {/* Center: Time Controls */}
      <div className="flex-1 p-6 max-w-3xl mx-auto">
        <motion.h1
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-2xl font-bold mb-6"
        >Play Chess</motion.h1>

        {/* Main Play Button */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="card p-6 mb-6"
        >
          <button
            onClick={() => handlePlay('5+0')}
            className="btn-primary w-full text-xl !py-4 flex items-center justify-center gap-3 animate-glow-pulse"
          >
            <Crown size={24} />
            Play
          </button>
          <p className="text-center text-text-dim text-sm mt-3">
            Play a rated game against a player of your skill level
          </p>
        </motion.div>

        {/* Time Controls Grid */}
        <motion.div
          className="card p-4"
          initial="hidden" animate="show" variants={stagger}
        >
          <h2 className="text-sm font-bold text-text-muted mb-4 px-2">Time Control</h2>
          <div className="grid grid-cols-3 gap-2">
            {timeControls.map((tc) => {
              const Icon = tc.icon;
              return (
                <motion.button
                  key={tc.time}
                  variants={fadeUp}
                  whileHover={{ y: -3, transition: { duration: 0.15 } }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => handlePlay(tc.time)}
                  className="flex flex-col items-center gap-1 p-4 rounded-md bg-surface-200 hover:bg-surface-400 transition-colors group"
                >
                  <Icon size={20} className="text-accent-green group-hover:scale-110 transition-transform" />
                  <span className="text-lg font-bold group-hover:text-accent-greenHover transition-colors">{tc.label}</span>
                  <span className="text-xs text-text-dim">{tc.sub}</span>
                </motion.button>
              );
            })}
          </div>
        </motion.div>

        {/* Quick Challenge */}
        <motion.div
          className="grid grid-cols-2 gap-4 mt-4"
          initial="hidden" animate="show" variants={stagger}
        >
          <motion.button
            variants={fadeUp}
            whileHover={{ y: -3 }}
            onClick={() => navigate('/play/computer')}
            className="card p-4 flex items-center gap-3 hover:bg-surface-400 transition-all group"
          >
            <div className="w-10 h-10 rounded-md bg-surface-200 flex items-center justify-center group-hover:scale-110 transition-transform">
              <Bot size={20} className="text-accent-green" />
            </div>
            <div className="text-left">
              <div className="text-sm font-bold group-hover:text-accent-greenHover transition-colors">Play Computer</div>
              <div className="text-xs text-text-dim">Choose your difficulty</div>
            </div>
          </motion.button>
          <motion.button
            variants={fadeUp}
            whileHover={{ y: -3 }}
            className="card p-4 flex items-center gap-3 hover:bg-surface-400 transition-all group"
          >
            <div className="w-10 h-10 rounded-md bg-surface-200 flex items-center justify-center group-hover:scale-110 transition-transform">
              <Swords size={20} className="text-accent-green" />
            </div>
            <div className="text-left">
              <div className="text-sm font-bold group-hover:text-accent-greenHover transition-colors">Challenge Friend</div>
              <div className="text-xs text-text-dim">Send a game invite</div>
            </div>
          </motion.button>
        </motion.div>
      </div>

      {/* Right: Online Players */}
      <motion.div
        className="hidden xl:flex flex-col w-72 bg-surface-200 border-l border-surface-100 p-4"
        initial="hidden" animate="show" variants={stagger}
      >
        <h3 className="text-xs font-bold text-text-dim uppercase tracking-wider mb-3 px-2">Players Online</h3>
        <div className="flex items-center gap-2 mb-4 px-2">
          <div className="w-2 h-2 rounded-full bg-accent-green animate-subtle-pulse" />
          <span className="text-sm text-text-muted">1,248 players online</span>
        </div>

        <h3 className="text-xs font-bold text-text-dim uppercase tracking-wider mb-3 px-2 mt-4">Live Games</h3>
        {[
          { w: 'Magnus', b: 'Hikaru', time: '3+0', moves: 24 },
          { w: 'GothamChess', b: 'BotezLive', time: '5+0', moves: 18 },
          { w: 'DrDrunkenstein', b: 'ChessKing', time: '1+0', moves: 31 },
        ].map((game, i) => (
          <motion.button
            key={i}
            variants={fadeUp}
            whileHover={{ x: 4 }}
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
          </motion.button>
        ))}
      </motion.div>
    </div>
  );
};
