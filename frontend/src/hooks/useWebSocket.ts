import { useEffect, useRef, useCallback } from 'react';
import { useGameStore } from '../store/gameStore';
import { useAuthStore } from '../store/authStore';

export const useWebSocket = (gameId: string | null, isAi: boolean = false) => {
  const socket = useRef<WebSocket | null>(null);
  const { setGame, updateTime, addMove, setSpectatorCount } = useGameStore();
  const { token } = useAuthStore();

  const connect = useCallback(() => {
    if (!gameId || !token) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const baseUrl = import.meta.env.VITE_WS_URL || 'localhost:8000';
    const path = isAi ? `/ws/game/ai/${gameId}` : `/ws/game/${gameId}`;
    
    const url = `${protocol}//${baseUrl}${path}?token=${token}`;
    
    socket.current = new WebSocket(url);

    socket.current.onopen = () => {
      console.log('Connected to game socket');
    };

    socket.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case 'game_state':
          setGame(data);
          break;
        case 'time_update':
          updateTime(data.white_time, data.black_time);
          break;
        case 'move':
          addMove(data.move, data.fen, data.turn);
          break;
        case 'spectator_joined':
        case 'spectator_left':
          setSpectatorCount(data.spectator_count);
          break;
        case 'game_over':
          // Handle game over (update store status, result, termination)
          setGame({ ...data, is_active: false });
          break;
        case 'error':
          console.error('Socket error:', data.message);
          break;
        default:
          console.log('Unknown socket event:', data.type);
      }
    };

    socket.current.onclose = () => {
      console.log('Disconnected from game socket');
      // Potential reconnect logic here
    };

    socket.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }, [gameId, token, isAi, setGame, updateTime, addMove, setSpectatorCount]);

  useEffect(() => {
    connect();
    return () => {
      socket.current?.close();
    };
  }, [connect]);

  const sendMove = (move: string) => {
    if (socket.current?.readyState === WebSocket.OPEN) {
      socket.current.send(JSON.stringify({
        type: 'move',
        move: move
      }));
    }
  };

  const offerDraw = () => {
    socket.current?.send(JSON.stringify({ type: 'offer_draw' }));
  };

  const resign = () => {
    socket.current?.send(JSON.stringify({ type: 'resign' }));
  };

  return {
    sendMove,
    offerDraw,
    resign,
    isConnected: socket.current?.readyState === WebSocket.OPEN
  };
};
