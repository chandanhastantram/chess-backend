import { create } from 'zustand';

interface GameState {
  game_id: string | null;
  fen: string;
  turn: 'white' | 'black';
  white_time: number;
  black_time: number;
  moves: string[];
  status: 'pending' | 'active' | 'completed';
  result: string | null;
  termination: string | null;
  playerColor: 'white' | 'black' | 'spectator';
  isSpectator: boolean;
  spectatorCount: number;
  lastMoveTime: string | null;
  
  // Actions
  setGame: (data: any) => void;
  updateTime: (whiteTime: number, blackTime: number) => void;
  addMove: (move: string, fen: string, turn: 'white' | 'black') => void;
  setSpectatorCount: (count: number) => void;
  resetGame: () => void;
}

export const useGameStore = create<GameState>((set) => ({
  game_id: null,
  fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
  turn: 'white',
  white_time: 0,
  black_time: 0,
  moves: [],
  status: 'pending',
  result: null,
  termination: null,
  playerColor: 'spectator',
  isSpectator: true,
  spectatorCount: 0,
  lastMoveTime: null,

  setGame: (data) => set({
    game_id: data.game_id,
    fen: data.fen || 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
    turn: data.turn || 'white',
    white_time: data.white_time,
    black_time: data.black_time,
    moves: data.moves || [],
    status: data.is_active ? 'active' : 'completed',
    result: data.result,
    termination: data.termination,
    playerColor: data.playerColor || 'spectator',
    isSpectator: data.playerColor === 'spectator',
  }),

  updateTime: (white_time, black_time) => set({ white_time, black_time }),

  addMove: (move, fen, turn) => set((state) => ({
    moves: [...state.moves, move],
    fen,
    turn,
    lastMoveTime: new Date().toISOString()
  })),

  setSpectatorCount: (spectatorCount) => set({ spectatorCount }),

  resetGame: () => set({
    game_id: null,
    fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
    turn: 'white',
    white_time: 0,
    black_time: 0,
    moves: [],
    status: 'pending',
    result: null,
    termination: null,
    playerColor: 'spectator',
    isSpectator: true,
    spectatorCount: 0,
    lastMoveTime: null,
  }),
}));
