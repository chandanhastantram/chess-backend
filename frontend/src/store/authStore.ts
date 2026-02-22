import { create } from 'zustand';
import api from '../services/api';

interface User {
  id: string;
  username: string;
  avatar_url?: string;
  country?: string;
  bio?: string;
  level?: number;
  xp?: number;
  is_online?: boolean;
  preferred_board_theme?: string;
  preferred_piece_set?: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
  checkAuth: () => Promise<void>;
  updateUser: (data: Partial<User>) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),
  loading: true,

  login: (token, user) => {
    localStorage.setItem('token', token);
    set({ token, user, isAuthenticated: true, loading: false });
  },

  logout: () => {
    localStorage.removeItem('token');
    set({ token: null, user: null, isAuthenticated: false, loading: false });
  },

  checkAuth: async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      set({ loading: false });
      return;
    }

    try {
      const response = await api.get('/users/me');
      set({ user: response.data, isAuthenticated: true, loading: false });
    } catch (error) {
      localStorage.removeItem('token');
      set({ token: null, user: null, isAuthenticated: false, loading: false });
    }
  },

  updateUser: (data) => {
    set((state) => ({
      user: state.user ? { ...state.user, ...data } : null,
    }));
  },
}));
