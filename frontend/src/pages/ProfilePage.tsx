import { useAuthStore } from '../store/authStore';
import { Trophy, Target, Flame, Zap, Clock, Timer, TrendingUp, Star, Award } from 'lucide-react';
import { motion } from 'framer-motion';

const stagger = { hidden: {}, show: { transition: { staggerChildren: 0.08 } } };
const fadeUp = {
  hidden: { opacity: 0, y: 15 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0, 0, 0.2, 1] as const } }
};
const scaleIn = {
  hidden: { opacity: 0, scale: 0.8 },
  show: { opacity: 1, scale: 1, transition: { type: 'spring' as const, stiffness: 300, damping: 20 } }
};

export const ProfilePage = () => {
  const { user } = useAuthStore();

  const stats = [
    { label: 'Bullet', rating: 1450, icon: Zap, games: 342, winRate: 54 },
    { label: 'Blitz', rating: 1520, icon: Clock, games: 567, winRate: 58 },
    { label: 'Rapid', rating: 1680, icon: Timer, games: 189, winRate: 62 },
  ];

  const recentGames = [
    { opponent: 'ChessKing', result: 'win', rating: '+8', time: '5+0', date: '2h ago' },
    { opponent: 'PawnStar', result: 'loss', rating: '-6', time: '3+2', date: '3h ago' },
    { opponent: 'KnightRider', result: 'draw', rating: '+1', time: '10+0', date: '5h ago' },
    { opponent: 'Gambit99', result: 'win', rating: '+10', time: '1+0', date: '6h ago' },
    { opponent: 'RookMaster', result: 'win', rating: '+7', time: '3+0', date: '8h ago' },
  ];

  const xp = user?.xp || 45;

  return (
    <div className="min-h-[calc(100vh-48px)] bg-surface-100 p-6 max-w-5xl mx-auto">
      {/* Profile Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card p-6 flex flex-col sm:flex-row items-start gap-6 mb-6"
      >
        <motion.div
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ type: 'spring', stiffness: 200, damping: 15, delay: 0.2 }}
          className="w-24 h-24 rounded-lg bg-accent-green flex items-center justify-center text-white text-4xl font-bold"
        >
          {user?.username?.charAt(0).toUpperCase() || 'U'}
        </motion.div>
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-1">
            <h1 className="text-2xl font-bold">{user?.username || 'Player'}</h1>
            <motion.span
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.4, type: 'spring', stiffness: 300 }}
              className="px-2 py-0.5 bg-accent-green/20 text-accent-green text-xs font-bold rounded"
            >
              Level {user?.level || 1}
            </motion.span>
          </div>
          <p className="text-text-muted text-sm mb-3">Member since January 2024</p>

          {/* Animated XP Bar */}
          <div className="mb-3">
            <div className="flex justify-between text-xs text-text-dim mb-1">
              <span>XP: {xp} / 100</span>
              <span>Level {(user?.level || 1) + 1}</span>
            </div>
            <div className="h-2 bg-surface-200 rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-accent-green rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${xp}%` }}
                transition={{ duration: 1, delay: 0.5, ease: [0.34, 1.56, 0.64, 1] as const }}
              />
            </div>
          </div>

          {/* Quick stats with count-up */}
          <motion.div
            className="flex gap-6 text-sm"
            initial="hidden" animate="show" variants={stagger}
          >
            <motion.div variants={fadeUp} className="flex items-center gap-1.5">
              <Trophy size={14} className="text-accent-orange" />
              <span className="font-bold">1,098</span>
              <span className="text-text-dim">games</span>
            </motion.div>
            <motion.div variants={fadeUp} className="flex items-center gap-1.5">
              <Target size={14} className="text-accent-green" />
              <span className="font-bold">57%</span>
              <span className="text-text-dim">win rate</span>
            </motion.div>
            <motion.div variants={fadeUp} className="flex items-center gap-1.5">
              <Flame size={14} className="text-accent-red" />
              <span className="font-bold">5</span>
              <span className="text-text-dim">streak</span>
            </motion.div>
          </motion.div>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Rating Cards */}
        <div className="lg:col-span-2 space-y-4">
          <motion.h2
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            className="text-lg font-bold flex items-center gap-2"
          >
            <TrendingUp size={20} className="text-accent-green" /> Ratings
          </motion.h2>
          <motion.div
            className="grid grid-cols-3 gap-4"
            initial="hidden" animate="show" variants={stagger}
          >
            {stats.map((s) => {
              const Icon = s.icon;
              return (
                <motion.div
                  key={s.label}
                  variants={scaleIn}
                  whileHover={{ y: -4, transition: { duration: 0.2 } }}
                  className="card p-4 cursor-pointer"
                >
                  <div className="flex items-center gap-2 mb-3">
                    <Icon size={16} className="text-text-muted" />
                    <span className="text-sm font-bold text-text-muted">{s.label}</span>
                  </div>
                  <div className="text-3xl font-bold mb-1">{s.rating}</div>
                  <div className="flex justify-between text-xs text-text-dim">
                    <span>{s.games} games</span>
                    <span>{s.winRate}% wins</span>
                  </div>
                  {/* Mini progress bar */}
                  <div className="mt-2 h-1 bg-surface-200 rounded-full overflow-hidden">
                    <motion.div
                      className="h-full bg-accent-green rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: `${s.winRate}%` }}
                      transition={{ duration: 1, delay: 0.6 }}
                    />
                  </div>
                </motion.div>
              );
            })}
          </motion.div>

          {/* Recent Games */}
          <motion.h2
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="text-lg font-bold flex items-center gap-2 mt-6"
          >
            <Clock size={20} className="text-text-muted" /> Recent Games
          </motion.h2>
          <motion.div
            className="card overflow-hidden"
            initial="hidden" animate="show" variants={stagger}
          >
            {recentGames.map((game, i) => (
              <motion.div
                key={i}
                variants={fadeUp}
                whileHover={{ x: 4, transition: { duration: 0.15 } }}
                className={`flex items-center justify-between px-4 py-3 ${
                  i % 2 === 0 ? 'bg-surface-300' : 'bg-surface-200'
                } hover:bg-surface-400 transition-colors cursor-pointer`}
              >
                <div className="flex items-center gap-3">
                  <motion.div
                    className={`w-2 h-2 rounded-full ${
                      game.result === 'win' ? 'bg-accent-green' :
                      game.result === 'loss' ? 'bg-accent-red' : 'bg-text-dim'
                    }`}
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: 0.5 + i * 0.1 }}
                  />
                  <div>
                    <span className="font-bold text-sm">vs {game.opponent}</span>
                    <span className="text-text-dim text-xs ml-2">{game.time}</span>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <span className={`font-mono font-bold text-sm ${
                    game.result === 'win' ? 'text-accent-green' :
                    game.result === 'loss' ? 'text-accent-red' : 'text-text-dim'
                  }`}>{game.rating}</span>
                  <span className="text-xs text-text-dim">{game.date}</span>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>

        {/* Achievements Sidebar */}
        <motion.div
          className="space-y-4"
          initial="hidden" animate="show" variants={stagger}
        >
          <motion.h2 variants={fadeUp} className="text-lg font-bold flex items-center gap-2">
            <Award size={20} className="text-accent-orange" /> Achievements
          </motion.h2>
          {[
            { name: 'First Win', desc: 'Win your first game', done: true },
            { name: 'Century', desc: 'Play 100 games', done: true },
            { name: 'Streak Master', desc: '10 win streak', done: false },
            { name: 'Puzzle Pro', desc: 'Solve 500 puzzles', done: false },
            { name: 'Grandmaster', desc: 'Reach 2000 rating', done: false },
          ].map((a) => (
            <motion.div
              key={a.name}
              variants={fadeUp}
              whileHover={a.done ? { scale: 1.02, transition: { duration: 0.15 } } : {}}
              className={`card p-4 flex items-center gap-3 ${!a.done && 'opacity-50'}`}
            >
              <motion.div
                className={`w-10 h-10 rounded-md flex items-center justify-center ${
                  a.done ? 'bg-accent-green/20' : 'bg-surface-200'
                }`}
                whileHover={a.done ? { rotate: 15 } : {}}
              >
                <Star size={18} className={a.done ? 'text-accent-green' : 'text-text-dim'} />
              </motion.div>
              <div>
                <div className="text-sm font-bold">{a.name}</div>
                <div className="text-xs text-text-dim">{a.desc}</div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </div>
  );
};
