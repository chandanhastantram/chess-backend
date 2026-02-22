import { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import { Header } from './components/Header';
import { MatchPage } from './pages/MatchPage';
import { LoginPage } from './pages/LoginPage';
import { PlayPage } from './pages/PlayPage';
import { Leaderboard } from './pages/Leaderboard';
import { ProfilePage } from './pages/ProfilePage';
import { Crown, Zap, Puzzle, BookOpen, Trophy, Monitor } from 'lucide-react';

// Landing Page
const Landing = () => (
  <div className="min-h-[calc(100vh-48px)] bg-surface-100">
    {/* Hero */}
    <div className="bg-surface-200 border-b border-surface-100">
      <div className="max-w-6xl mx-auto px-6 py-20 flex flex-col lg:flex-row items-center gap-12">
        <div className="flex-1 space-y-6">
          <h1 className="text-5xl lg:text-6xl font-bold leading-tight">
            Play Chess <span className="text-accent-green">Online</span>
          </h1>
          <p className="text-xl text-text-muted max-w-md">
            Join millions of players worldwide. Play, learn, and improve your game.
          </p>
          <div className="flex gap-3">
            <Link to="/play" className="btn-primary text-lg !py-4 !px-8 flex items-center gap-2">
              <Crown size={22} /> Play Now
            </Link>
            <Link to="/register" className="btn-secondary text-lg !py-4 !px-8">
              Sign Up Free
            </Link>
          </div>
          <div className="flex gap-6 text-sm text-text-dim pt-2">
            <span>✓ 100% Free</span>
            <span>✓ No Download</span>
            <span>✓ Play Instantly</span>
          </div>
        </div>

        {/* Mini Board Preview */}
        <div className="w-80 h-80 rounded-lg overflow-hidden shadow-2xl grid grid-cols-8 grid-rows-8 flex-shrink-0">
          {Array.from({ length: 64 }, (_, i) => {
            const row = Math.floor(i / 8);
            const col = i % 8;
            const isLight = (row + col) % 2 === 0;
            return (
              <div
                key={i}
                className={isLight ? 'bg-board-light' : 'bg-board-dark'}
              />
            );
          })}
        </div>
      </div>
    </div>

    {/* Features Grid */}
    <div className="max-w-6xl mx-auto px-6 py-16">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {[
          { icon: Zap, title: 'Play Online', desc: 'Instant matchmaking with players at your level', color: 'text-accent-orange' },
          { icon: Puzzle, title: 'Puzzles', desc: 'Sharpen your tactics with thousands of puzzles', color: 'text-accent-green' },
          { icon: BookOpen, title: 'Lessons', desc: 'Learn from beginner to master level courses', color: 'text-accent-green' },
          { icon: Trophy, title: 'Tournaments', desc: 'Compete in daily and weekly tournaments', color: 'text-accent-orange' },
          { icon: Monitor, title: 'Game Analysis', desc: 'AI-powered analysis to review your games', color: 'text-accent-green' },
          { icon: Crown, title: 'Play vs AI', desc: '6 difficulty levels from beginner to master', color: 'text-accent-orange' },
        ].map((f) => {
          const Icon = f.icon;
          return (
            <div key={f.title} className="card p-6 hover:bg-surface-400 transition-colors cursor-pointer group">
              <div className={`w-12 h-12 rounded-lg bg-surface-200 flex items-center justify-center mb-4 ${f.color}`}>
                <Icon size={24} />
              </div>
              <h3 className="text-lg font-bold mb-2 group-hover:text-accent-green transition-colors">{f.title}</h3>
              <p className="text-sm text-text-muted">{f.desc}</p>
            </div>
          );
        })}
      </div>
    </div>

    {/* Stats Bar */}
    <div className="bg-surface-300 border-t border-surface-100">
      <div className="max-w-6xl mx-auto px-6 py-8 flex flex-wrap justify-center gap-12 text-center">
        {[
          { num: '50M+', label: 'Games Played' },
          { num: '10M+', label: 'Members' },
          { num: '100K+', label: 'Puzzles' },
          { num: '50K+', label: 'Online Now' },
        ].map((s) => (
          <div key={s.label}>
            <div className="text-3xl font-bold text-accent-green">{s.num}</div>
            <div className="text-sm text-text-muted mt-1">{s.label}</div>
          </div>
        ))}
      </div>
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
