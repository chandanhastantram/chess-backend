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
    <div className="min-h-screen study-vibe pt-24 px-6 max-w-7xl mx-auto pb-12">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Play Now - Matchmaking Pools */}
        <div className="lg:col-span-2 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-3xl italic">Tournament Hall</h2>
            <div className="flex gap-2">
              <span className="px-3 py-1 bg-chess-success/10 text-chess-success text-[10px] font-bold uppercase tracking-widest rounded-full border border-chess-success/20">
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
                  className="glass-card p-6 flex items-center justify-between group hover:border-gold/30 hover:bg-obsidian-hover transition-all text-left"
                >
                  <div className="flex items-center gap-4">
                    <div className={`p-3 rounded-xl bg-obsidian border border-white/5 ${pool.color}`}>
                      <Icon size={24} />
                    </div>
                    <div>
                      <h3 className="text-lg font-bold">{pool.label}</h3>
                      <p className="text-sm text-parchment/40">{pool.time} • Rated</p>
                    </div>
                  </div>
                  <ArrowRight className="text-gold opacity-0 group-hover:opacity-100 transition-all -translate-x-2 group-hover:translate-x-0" />
                </button>
              );
            })}
          </div>

          {/* Quick Actions */}
          <div className="flex flex-wrap gap-4 pt-4">
            <button className="premium-button flex-1 min-w-[200px] flex items-center justify-center gap-2">
              <Swords size={20} />
              Challenge a Friend
            </button>
            <button className="flex-1 min-w-[200px] flex items-center justify-center gap-2 glass-card p-3 hover:bg-white/5 transition-all font-bold uppercase text-xs tracking-widest">
              Play with AI
            </button>
          </div>
        </div>

        {/* Live Games - Spectator View */}
        <div className="space-y-6">
          <h2 className="text-2xl italic">Watch Live</h2>
          <div className="space-y-4">
            {activeMatches.length > 0 ? (
              activeMatches.map((match) => (
                <div 
                  key={match.id}
                  onClick={() => navigate(`/game/${match.id}`)}
                  className="glass-card p-4 space-y-4 cursor-pointer hover:border-gold/20 hover:bg-obsidian-hover transition-all"
                >
                  <div className="flex justify-between items-center text-xs text-parchment/40 uppercase tracking-widest font-bold">
                    <span>{match.time_control}</span>
                    <span className="flex items-center gap-1">
                      <div className="w-1.5 h-1.5 rounded-full bg-chess-success" />
                      Live
                    </span>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                       <div className="flex items-center gap-2">
                         <div className="w-6 h-6 rounded bg-white" />
                         <span className="text-sm font-bold truncate">{match.white_player}</span>
                       </div>
                       <span className="text-xs opacity-40 italic">2140</span>
                    </div>
                    <div className="flex items-center justify-between">
                       <div className="flex items-center gap-2">
                         <div className="w-6 h-6 rounded bg-neutral-800 border border-white/10" />
                         <span className="text-sm font-bold truncate">{match.black_player}</span>
                       </div>
                       <span className="text-xs opacity-40 italic">2155</span>
                    </div>
                  </div>

                  <div className="pt-2 border-t border-white/5 flex justify-between items-center text-[10px] text-parchment/40">
                    <span>{match.opening_name || 'Chess Variation'}</span>
                    <span>{match.spectators || 0} watching</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="glass-card p-8 text-center space-y-4">
                <p className="text-sm text-parchment/40 italic">No matches currently in progress</p>
                <button className="premium-button text-xs py-2">Start a Game</button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
