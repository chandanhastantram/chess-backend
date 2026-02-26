import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import api from '../services/api';
import { Eye, EyeOff, Crown } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

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
        const res = await api.post('/auth/login', { email, password });
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
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        {/* Logo */}
        <motion.div
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ type: 'spring', stiffness: 200, damping: 15 }}
          className="flex items-center justify-center gap-2 mb-8"
        >
          <div className="w-12 h-12 bg-accent-green rounded-lg flex items-center justify-center animate-glow-pulse">
            <Crown size={28} className="text-white" />
          </div>
          <span className="font-bold text-3xl">chess<span className="text-accent-green">.club</span></span>
        </motion.div>

        {/* Toggle */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="flex mb-6 bg-surface-300 rounded-lg p-1"
        >
          <button
            onClick={() => setIsLogin(true)}
            className={`flex-1 py-2.5 rounded-md text-sm font-bold transition-all ${
              isLogin ? 'bg-accent-green text-white shadow-md' : 'text-text-muted hover:text-text'
            }`}
          >
            Log In
          </button>
          <button
            onClick={() => setIsLogin(false)}
            className={`flex-1 py-2.5 rounded-md text-sm font-bold transition-all ${
              !isLogin ? 'bg-accent-green text-white shadow-md' : 'text-text-muted hover:text-text'
            }`}
          >
            Sign Up
          </button>
        </motion.div>

        {/* Form */}
        <motion.form
          onSubmit={handleSubmit}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="card p-6 space-y-4"
        >
          {/* Username - always shown for sign up, shown as login identifier for login */}
          <AnimatePresence mode="wait">
            {!isLogin && (
              <motion.div
                key="username"
                initial={{ opacity: 0, height: 0, marginTop: 0 }}
                animate={{ opacity: 1, height: 'auto', marginTop: 0 }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.2 }}
              >
                <label className="block text-sm font-bold text-text-muted mb-1">Username</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full bg-surface-200 border border-surface-400 rounded-md px-4 py-2.5 text-text placeholder:text-text-dim focus:outline-none focus:border-accent-green focus:shadow-[0_0_0_1px_rgba(129,182,76,0.3)] transition-all"
                  placeholder="Choose a username"
                  required={!isLogin}
                />
              </motion.div>
            )}
          </AnimatePresence>

          <div>
            <label className="block text-sm font-bold text-text-muted mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-surface-200 border border-surface-400 rounded-md px-4 py-2.5 text-text placeholder:text-text-dim focus:outline-none focus:border-accent-green focus:shadow-[0_0_0_1px_rgba(129,182,76,0.3)] transition-all"
              placeholder="Enter email"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-bold text-text-muted mb-1">Password</label>
            <div className="relative">
              <input
                type={showPass ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-surface-200 border border-surface-400 rounded-md px-4 py-2.5 pr-10 text-text placeholder:text-text-dim focus:outline-none focus:border-accent-green focus:shadow-[0_0_0_1px_rgba(129,182,76,0.3)] transition-all"
                placeholder="Enter password"
                required
              />
              <button
                type="button"
                onClick={() => setShowPass(!showPass)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-text-dim hover:text-text transition-colors"
              >
                {showPass ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10, height: 0 }}
                animate={{ opacity: 1, y: 0, height: 'auto' }}
                exit={{ opacity: 0, y: -10, height: 0 }}
                className="bg-accent-red/10 border border-accent-red/30 text-accent-red rounded-md px-4 py-2 text-sm"
              >
                {error}
              </motion.div>
            )}
          </AnimatePresence>

          <motion.button
            type="submit"
            disabled={loading}
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.98 }}
            className="btn-primary w-full !py-3"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <motion.span
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                  className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full"
                />
                Loading...
              </span>
            ) : isLogin ? 'Log In' : 'Sign Up'}
          </motion.button>
        </motion.form>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-center text-text-dim text-sm mt-6"
        >
          By continuing, you agree to our Terms of Service
        </motion.p>
      </motion.div>
    </div>
  );
};
