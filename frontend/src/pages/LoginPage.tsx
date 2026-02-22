import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import api from '../services/api';
import { Eye, EyeOff, Crown } from 'lucide-react';

export const LoginPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPass, setShowPass] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);
        const res = await api.post('/auth/login', formData, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        login(res.data.access_token, res.data.user);
      } else {
        const res = await api.post('/auth/register', { username, email, password });
        login(res.data.access_token, res.data.user);
      }
      navigate('/play');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-surface-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="flex items-center justify-center gap-2 mb-8">
          <div className="w-12 h-12 bg-accent-green rounded-lg flex items-center justify-center">
            <Crown size={28} className="text-white" />
          </div>
          <span className="font-bold text-3xl">chess<span className="text-accent-green">.club</span></span>
        </div>

        {/* Toggle */}
        <div className="flex mb-6 bg-surface-300 rounded-lg p-1">
          <button
            onClick={() => setIsLogin(true)}
            className={`flex-1 py-2.5 rounded-md text-sm font-bold transition-colors ${
              isLogin ? 'bg-accent-green text-white' : 'text-text-muted hover:text-text'
            }`}
          >
            Log In
          </button>
          <button
            onClick={() => setIsLogin(false)}
            className={`flex-1 py-2.5 rounded-md text-sm font-bold transition-colors ${
              !isLogin ? 'bg-accent-green text-white' : 'text-text-muted hover:text-text'
            }`}
          >
            Sign Up
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="card p-6 space-y-4">
          <div>
            <label className="block text-sm font-bold text-text-muted mb-1">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-surface-200 border border-surface-400 rounded-md px-4 py-2.5 text-text placeholder:text-text-dim focus:outline-none focus:border-accent-green transition-colors"
              placeholder="Enter username"
              required
            />
          </div>

          {!isLogin && (
            <div>
              <label className="block text-sm font-bold text-text-muted mb-1">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-surface-200 border border-surface-400 rounded-md px-4 py-2.5 text-text placeholder:text-text-dim focus:outline-none focus:border-accent-green transition-colors"
                placeholder="Enter email"
                required
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-bold text-text-muted mb-1">Password</label>
            <div className="relative">
              <input
                type={showPass ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-surface-200 border border-surface-400 rounded-md px-4 py-2.5 pr-10 text-text placeholder:text-text-dim focus:outline-none focus:border-accent-green transition-colors"
                placeholder="Enter password"
                required
              />
              <button
                type="button"
                onClick={() => setShowPass(!showPass)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-text-dim hover:text-text"
              >
                {showPass ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          {error && (
            <div className="bg-accent-red/10 border border-accent-red/30 text-accent-red rounded-md px-4 py-2 text-sm">
              {error}
            </div>
          )}

          <button type="submit" disabled={loading} className="btn-primary w-full !py-3">
            {loading ? 'Loading...' : isLogin ? 'Log In' : 'Sign Up'}
          </button>
        </form>

        <p className="text-center text-text-dim text-sm mt-6">
          By continuing, you agree to our Terms of Service
        </p>
      </div>
    </div>
  );
};
