import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { Swords, Clock, ArrowRight, Zap, Target, BookOpen } from 'lucide-react';

export const Lobby: React.FC = () => {
  const [activeMatches, setActiveMatches] = useState<any[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch active matches from backend
    const fetchMatches = async () => {
      try {
        const response = await api.get('/games/live');
        setActiveMatches(response.data);
      } catch (error) {
        console.error('Failed to fetch matches');
      }
    };
    fetchMatches();
  }, []);

  const matchmakingPools = [
    { id: 'bullet', label: 'Bullet', time: '1+0', icon: Zap, color: 'text-yellow-400' },
    { id: 'blitz', label: 'Blitz', time: '3+2', icon: Clock, color: 'text-blue-400' },
    { id: 'rapid', label: 'Rapid', time: '10+5', icon: Target, color: 'text-green-400' },
    { id: 'classical', label: 'Classical', time: '30+0', icon: BookOpen, color: 'text-parchment' },
  ];

  return (
    <div className="min-h-screen pt-24 px-6 max-w-7xl mx-auto pb-12">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Play Now - Matchmaking Pools */}
        <div className="lg:col-span-2 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-3xl font-bold">Tournament Hall</h2>
            <div className="flex gap-2">
              <span className="px-3 py-1 bg-accent-green/10 text-accent-green text-[10px] font-bold uppercase tracking-widest rounded-full border border-accent-green/20">
                1,248 Players Online
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {matchmakingPools.map((pool) => {
              const Icon = pool.icon;
              return (
                <button
                  key={pool.id}
                  className="card p-6 flex items-center justify-between group hover:bg-surface-400 hover:-translate-y-1 transition-all text-left"
                >
                  <div className="flex items-center gap-4">
                    <div className={`p-3 rounded-xl bg-surface-200 group-hover:scale-110 transition-transform ${pool.color}`}>
                      <Icon size={24} />
                    </div>
                    <div>
                      <h3 className="text-lg font-bold group-hover:text-accent-greenHover transition-colors">{pool.label}</h3>
                      <p className="text-sm text-text-muted">{pool.time} • Rated</p>
                    </div>
                  </div>
                  <ArrowRight className="text-accent-green opacity-0 group-hover:opacity-100 transition-all -translate-x-2 group-hover:translate-x-0" />
                </button>
              );
            })}
          </div>

          {/* Quick Actions */}
          <div className="flex flex-wrap gap-4 pt-4">
            <button className="btn-primary flex-1 min-w-[200px] flex items-center justify-center gap-2 text-lg">
              <Swords size={20} />
              Challenge a Friend
            </button>
            <button className="btn-secondary flex-1 min-w-[200px] flex items-center justify-center gap-2 text-lg">
              Play with AI
            </button>
          </div>
        </div>

        {/* Live Games - Spectator View */}
        <div className="space-y-6">
          <h2 className="text-2xl font-bold">Watch Live</h2>
          <div className="space-y-4">
            {activeMatches.length > 0 ? (
              activeMatches.map((match) => (
                <div 
                  key={match.id}
                  onClick={() => navigate(`/game/${match.id}`)}
                  className="card p-4 space-y-4 cursor-pointer hover:bg-surface-400 hover:-translate-y-1 transition-all"
                >
                  <div className="flex justify-between items-center text-xs text-text-muted uppercase tracking-widest font-bold">
                    <span>{match.time_control}</span>
                    <span className="flex items-center gap-1">
                      <div className="w-1.5 h-1.5 rounded-full bg-accent-green animate-subtle-pulse" />
                      Live
                    </span>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                       <div className="flex items-center gap-2">
                         <div className="w-6 h-6 rounded bg-surface-100 flex items-center justify-center text-text-muted text-xs font-bold border border-surface-400">W</div>
                         <span className="text-sm font-bold truncate group-hover:text-accent-green transition-colors">{match.white_player}</span>
                       </div>
                       <span className="text-xs text-text-dim font-mono">2140</span>
                    </div>
                    <div className="flex items-center justify-between">
                       <div className="flex items-center gap-2">
                         <div className="w-6 h-6 rounded bg-surface-100 flex items-center justify-center text-text-muted text-xs font-bold border border-surface-400">B</div>
                         <span className="text-sm font-bold truncate group-hover:text-accent-green transition-colors">{match.black_player}</span>
                       </div>
                       <span className="text-xs text-text-dim font-mono">2155</span>
                    </div>
                  </div>

                  <div className="pt-2 border-t border-surface-200 flex justify-between items-center text-[10px] text-text-dim">
                    <span>{match.opening_name || 'Chess Variation'}</span>
                    <span>{match.spectators || 0} watching</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="card p-8 text-center space-y-4">
                <p className="text-sm text-text-muted">No matches currently in progress</p>
                <button className="btn-primary w-full text-sm !py-2">Start a Game</button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
