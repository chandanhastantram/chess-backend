import { Link, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { Crown, Puzzle, BookOpen, Trophy, User, LogOut, ChevronDown } from 'lucide-react';

export const Header = () => {
  const { user, logout, isAuthenticated } = useAuthStore();
  const location = useLocation();

  const navItems = [
    { label: 'Play', path: '/play', icon: Crown },
    { label: 'Puzzles', path: '/puzzles', icon: Puzzle },
    { label: 'Learn', path: '/learn', icon: BookOpen },
    { label: 'Watch', path: '/watch', icon: Trophy },
  ];

  return (
    <header className="h-12 bg-surface-300 border-b border-surface-100 flex items-center px-4 sticky top-0 z-50">
      {/* Logo */}
      <Link to="/" className="flex items-center gap-2 mr-6">
        <div className="w-8 h-8 bg-accent-green rounded flex items-center justify-center">
          <Crown size={18} className="text-white" />
        </div>
        <span className="font-bold text-lg text-text hidden sm:block">chess<span className="text-accent-green">.club</span></span>
      </Link>

      {/* Nav */}
      <nav className="flex items-center gap-1 flex-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-sm font-bold transition-all hover:scale-105 active:scale-95 ${
                isActive
                  ? 'bg-surface-400 text-text shadow-sm'
                  : 'text-text-muted hover:text-text hover:bg-surface-400'
              }`}
            >
              <Icon size={16} className={isActive ? 'text-accent-green' : ''} />
              <span className="hidden md:inline">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* User */}
      <div className="flex items-center gap-2">
        {isAuthenticated ? (
          <div className="relative group">
            <button className="flex items-center gap-2 px-3 py-1.5 rounded hover:bg-surface-400 transition-colors">
              <div className="w-7 h-7 rounded bg-accent-green flex items-center justify-center text-white text-xs font-bold">
                {user?.username?.charAt(0).toUpperCase() || 'U'}
              </div>
              <span className="text-sm font-bold hidden sm:block">{user?.username}</span>
              <ChevronDown size={14} className="text-text-muted" />
            </button>

            <div className="absolute top-full right-0 mt-1 w-48 card py-1 shadow-xl opacity-0 group-hover:opacity-100 pointer-events-none group-hover:pointer-events-auto transition-all">
              <Link to="/profile" className="flex items-center gap-2 px-4 py-2 hover:bg-surface-400 text-sm">
                <User size={14} /> Profile
              </Link>
              <button
                onClick={logout}
                className="flex items-center gap-2 px-4 py-2 hover:bg-surface-400 text-sm text-accent-red w-full text-left"
              >
                <LogOut size={14} /> Log Out
              </button>
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <Link to="/login" className="text-sm font-bold text-text-muted hover:text-text px-3 py-1.5 transition-colors">
              Log In
            </Link>
            <Link to="/register" className="btn-primary text-sm !py-1.5 !px-4">
              Sign Up
            </Link>
          </div>
        )}
      </div>
    </header>
  );
};
