import { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import { Header } from './components/Header';
import { MatchPage } from './pages/MatchPage';
import { LoginPage } from './pages/LoginPage';
import { PlayPage } from './pages/PlayPage';
import { Leaderboard } from './pages/Leaderboard';
import { ProfilePage } from './pages/ProfilePage';
import { Crown, Zap, Puzzle, BookOpen, Trophy, Monitor } from 'lucide-react';
import { motion } from 'framer-motion';

// Piece positions for the animated board preview
const INITIAL_PIECES: Record<number, string> = {
  0: '♜', 1: '♞', 2: '♝', 3: '♛', 4: '♚', 5: '♝', 6: '♞', 7: '♜',
  8: '♟', 9: '♟', 10: '♟', 11: '♟', 12: '♟', 13: '♟', 14: '♟', 15: '♟',
  48: '♙', 49: '♙', 50: '♙', 51: '♙', 52: '♙', 53: '♙', 54: '♙', 55: '♙',
  56: '♖', 57: '♘', 58: '♗', 59: '♕', 60: '♔', 61: '♗', 62: '♘', 63: '♖',
};

const stagger = {
  hidden: {},
  show: { transition: { staggerChildren: 0.08 } }
};

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0, 0, 0.2, 1] as const } }
};

const scaleUp = {
  hidden: { opacity: 0, scale: 0.8 },
  show: { opacity: 1, scale: 1, transition: { duration: 0.4, ease: [0, 0, 0.2, 1] as const } }
};

// Animated counter component
const AnimatedNumber = ({ target, suffix = '' }: { target: string; suffix?: string }) => {
  const [display, setDisplay] = useState('0');
  useEffect(() => {
    const num = parseInt(target.replace(/[^0-9]/g, ''));
    const duration = 1500;
    const steps = 40;
    const increment = num / steps;
    let current = 0;
    let step = 0;
    const timer = setInterval(() => {
      step++;
      current = Math.min(Math.round(increment * step), num);
      if (current >= 1000) {
        setDisplay(Math.floor(current / 1000) + 'K+');
      } else if (current >= 1000000) {
        setDisplay(Math.floor(current / 1000000) + 'M+');
      } else {
        setDisplay(target.includes('M') ? Math.floor(current / (num / parseInt(target))) + 'M+' :
                   target.includes('K') ? Math.floor(current / (num / parseInt(target))) + 'K+' :
                   String(current));
      }
      if (step >= steps) {
        setDisplay(target);
        clearInterval(timer);
      }
    }, duration / steps);
    return () => clearInterval(timer);
  }, [target]);
  return <>{display}{suffix}</>;
};

// Landing Page
const Landing = () => (
  <div className="min-h-[calc(100vh-48px)] bg-surface-100">
    {/* Hero */}
    <div className="bg-surface-200 border-b border-surface-100 overflow-hidden">
      <motion.div
        className="max-w-6xl mx-auto px-6 py-20 flex flex-col lg:flex-row items-center gap-12"
        initial="hidden"
        animate="show"
        variants={stagger}
      >
        <div className="flex-1 space-y-6">
          <motion.h1 variants={fadeUp} className="text-5xl lg:text-6xl font-bold leading-tight">
            Play Chess <span className="text-accent-green">Online</span>
          </motion.h1>
          <motion.p variants={fadeUp} className="text-xl text-text-muted max-w-md">
            Join millions of players worldwide. Play, learn, and improve your game.
          </motion.p>
          <motion.div variants={fadeUp} className="flex gap-3">
            <Link to="/play" className="btn-primary text-lg !py-4 !px-8 flex items-center gap-2 animate-glow-pulse">
              <Crown size={22} /> Play Now
            </Link>
            <Link to="/register" className="btn-secondary text-lg !py-4 !px-8">
              Sign Up Free
            </Link>
          </motion.div>
          <motion.div variants={fadeUp} className="flex gap-6 text-sm text-text-dim pt-2">
            <span>✓ 100% Free</span>
            <span>✓ No Download</span>
            <span>✓ Play Instantly</span>
          </motion.div>
        </div>

        {/* Animated Mini Board Preview with pieces */}
        <motion.div
          variants={scaleUp}
          className="w-80 h-80 rounded-lg overflow-hidden shadow-2xl grid grid-cols-8 grid-rows-8 flex-shrink-0 animate-float"
        >
          {Array.from({ length: 64 }, (_, i) => {
            const row = Math.floor(i / 8);
            const col = i % 8;
            const isLight = (row + col) % 2 === 0;
            const piece = INITIAL_PIECES[i];
            const isBlack = i < 16;
            return (
              <div
                key={i}
                className={`flex items-center justify-center ${isLight ? 'bg-board-light' : 'bg-board-dark'}`}
              >
                {piece && (
                  <motion.span
                    initial={{ scale: 0, rotate: -180 }}
                    animate={{ scale: 1, rotate: 0 }}
                    transition={{ delay: 0.5 + i * 0.02, duration: 0.3, type: 'spring', stiffness: 200 }}
                    className="text-xl select-none"
                    style={{
                      color: isBlack ? '#000' : '#fff',
                      textShadow: isBlack ? '0 0 2px rgba(255,255,255,0.1)' : '0 0 3px rgba(0,0,0,0.4)',
                    }}
                  >
                    {piece}
                  </motion.span>
                )}
              </div>
            );
          })}
        </motion.div>
      </motion.div>
    </div>

    {/* Features Grid */}
    <div className="max-w-6xl mx-auto px-6 py-16">
      <motion.div
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6"
        initial="hidden"
        whileInView="show"
        viewport={{ once: true, margin: '-50px' }}
        variants={stagger}
      >
        {[
          { icon: Zap, title: 'Play Online', desc: 'Instant matchmaking with players at your level' },
          { icon: Puzzle, title: 'Puzzles', desc: 'Sharpen your tactics with thousands of puzzles' },
          { icon: BookOpen, title: 'Lessons', desc: 'Learn from beginner to master level courses' },
          { icon: Trophy, title: 'Tournaments', desc: 'Compete in daily and weekly tournaments' },
          { icon: Monitor, title: 'Game Analysis', desc: 'AI-powered analysis to review your games' },
          { icon: Crown, title: 'Play vs AI', desc: '6 difficulty levels from beginner to master' },
        ].map((f) => {
          const Icon = f.icon;
          return (
            <motion.div
              key={f.title}
              variants={fadeUp}
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
              className="card p-6 hover:bg-surface-400 cursor-pointer group"
            >
              <div className="w-12 h-12 rounded-lg bg-surface-200 flex items-center justify-center mb-4 text-accent-green group-hover:scale-110 transition-transform">
                <Icon size={24} />
              </div>
              <h3 className="text-lg font-bold mb-2 group-hover:text-accent-greenHover transition-colors">{f.title}</h3>
              <p className="text-sm text-text-muted">{f.desc}</p>
            </motion.div>
          );
        })}
      </motion.div>
    </div>

    {/* Stats Bar */}
    <div className="bg-surface-300 border-t border-surface-100">
      <motion.div
        className="max-w-6xl mx-auto px-6 py-8 flex flex-wrap justify-center gap-12 text-center"
        initial="hidden"
        whileInView="show"
        viewport={{ once: true }}
        variants={stagger}
      >
        {[
          { num: '50M+', label: 'Games Played' },
          { num: '10M+', label: 'Members' },
          { num: '100K+', label: 'Puzzles' },
          { num: '50K+', label: 'Online Now' },
        ].map((s) => (
          <motion.div key={s.label} variants={fadeUp}>
            <div className="text-3xl font-bold text-accent-green">
              <AnimatedNumber target={s.num} />
            </div>
            <div className="text-sm text-text-muted mt-1">{s.label}</div>
          </motion.div>
        ))}
      </motion.div>
    </div>
  </div>
);

function App() {
  const { checkAuth, loading } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  if (loading) {
    return (
      <div className="min-h-screen bg-surface-100 flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-surface-400 border-t-accent-green rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <Router>
      <Header />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/play" element={<PlayPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<LoginPage />} />
        <Route path="/leaderboard" element={<Leaderboard />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/game/:gameId" element={<MatchPage />} />
        {/* Aliases for nav */}
        <Route path="/watch" element={<Leaderboard />} />
        <Route path="/puzzles" element={<PlayPage />} />
        <Route path="/learn" element={<PlayPage />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

export default App;
