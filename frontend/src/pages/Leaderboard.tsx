import { useState, useEffect } from 'react';
import api from '../services/api';
import { Trophy, Medal, Crown, ChevronUp, ChevronDown } from 'lucide-react';

export const Leaderboard = () => {
  const [leaders, setLeaders] = useState<any[]>([]);
  const [tab, setTab] = useState<'daily' | 'bullet' | 'blitz' | 'rapid'>('blitz');

  useEffect(() => {
    const fetchLeaders = async () => {
      try {
        const res = await api.get(`/leaderboard?category=${tab}`);
        setLeaders(res.data);
      } catch {
        setLeaders([
          { rank: 1,  username: 'DrNykterstein', rating: 3300, change: +5, country: '🇳🇴', games: 1245, winRate: 78 },
          { rank: 2,  username: 'Hikaru',        rating: 3280, change: +12, country: '🇺🇸', games: 2341, winRate: 75 },
          { rank: 3,  username: 'GothamChess',   rating: 3150, change: -3, country: '🇺🇸', games: 890, winRate: 72 },
          { rank: 4,  username: 'Firouzja',      rating: 3120, change: +8, country: '🇫🇷', games: 556, winRate: 74 },
          { rank: 5,  username: 'MagnusCarlsen', rating: 3100, change: 0, country: '🇳🇴', games: 1100, winRate: 76 },
          { rank: 6,  username: 'DanielNaroditsky', rating: 3050, change: +2, country: '🇺🇸', games: 1890, winRate: 71 },
          { rank: 7,  username: 'Levy',          rating: 2980, change: -5, country: '🇺🇸', games: 3200, winRate: 68 },
          { rank: 8,  username: 'ChessKing',     rating: 2950, change: +15, country: '🇮🇳', games: 780, winRate: 70 },
          { rank: 9,  username: 'QueenSlayer',   rating: 2920, change: +3, country: '🇬🇧', games: 440, winRate: 69 },
          { rank: 10, username: 'BishopMaster',  rating: 2900, change: -1, country: '🇩🇪', games: 620, winRate: 67 },
        ]);
      }
    };
    fetchLeaders();
  }, [tab]);

  const tabs = [
    { id: 'daily', label: 'Daily' },
    { id: 'bullet', label: 'Bullet' },
    { id: 'blitz', label: 'Blitz' },
    { id: 'rapid', label: 'Rapid' },
  ] as const;

  return (
    <div className="min-h-[calc(100vh-48px)] bg-surface-100 p-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <Trophy size={28} className="text-accent-orange" />
        <h1 className="text-2xl font-bold">Leaderboard</h1>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-surface-300 p-1 rounded-md mb-6 w-fit">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-5 py-2 rounded text-sm font-bold transition-colors ${
              tab === t.id
                ? 'bg-accent-green text-white'
                : 'text-text-muted hover:text-text'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Top 3 */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        {leaders.slice(0, 3).map((p, i) => (
          <div key={p.username} className={`card p-5 text-center ${i === 0 ? 'border border-accent-orange/30' : ''}`}>
            <div className="flex justify-center mb-3">
              {i === 0 ? <Crown size={32} className="text-accent-orange" /> :
               i === 1 ? <Medal size={28} className="text-text-muted" /> :
               <Medal size={28} className="text-amber-700" />}
            </div>
            <div className="text-xl font-bold mb-1">{p.username}</div>
            <div className="text-sm text-text-muted mb-2">{p.country}</div>
            <div className="text-3xl font-bold text-accent-green">{p.rating}</div>
            <div className={`text-sm font-bold mt-1 flex items-center justify-center gap-0.5 ${
              p.change > 0 ? 'text-accent-green' : p.change < 0 ? 'text-accent-red' : 'text-text-dim'
            }`}>
              {p.change > 0 ? <ChevronUp size={14} /> : p.change < 0 ? <ChevronDown size={14} /> : null}
              {p.change > 0 ? '+' : ''}{p.change}
            </div>
          </div>
        ))}
      </div>

      {/* Full Table */}
      <div className="card overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="bg-surface-400 text-xs font-bold text-text-dim uppercase tracking-wider">
              <th className="px-4 py-3 text-left w-16">#</th>
              <th className="px-4 py-3 text-left">Player</th>
              <th className="px-4 py-3 text-center">Rating</th>
              <th className="px-4 py-3 text-center">Change</th>
              <th className="px-4 py-3 text-center hidden sm:table-cell">Games</th>
              <th className="px-4 py-3 text-center hidden sm:table-cell">Win %</th>
            </tr>
          </thead>
          <tbody>
            {leaders.map((p) => (
              <tr key={p.username} className="border-t border-surface-200 hover:bg-surface-400/50 transition-colors">
                <td className="px-4 py-3 font-bold text-text-dim">{p.rank}</td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded bg-surface-400 flex items-center justify-center text-sm font-bold">
                      {p.username.charAt(0)}
                    </div>
                    <div>
                      <div className="font-bold">{p.username}</div>
                      <div className="text-xs text-text-dim">{p.country}</div>
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3 text-center font-mono font-bold text-lg">{p.rating}</td>
                <td className="px-4 py-3 text-center">
                  <span className={`flex items-center justify-center gap-0.5 font-bold text-sm ${
                    p.change > 0 ? 'text-accent-green' : p.change < 0 ? 'text-accent-red' : 'text-text-dim'
                  }`}>
                    {p.change > 0 ? <ChevronUp size={12} /> : p.change < 0 ? <ChevronDown size={12} /> : null}
                    {Math.abs(p.change)}
                  </span>
                </td>
                <td className="px-4 py-3 text-center text-text-muted hidden sm:table-cell">{p.games}</td>
                <td className="px-4 py-3 text-center text-text-muted hidden sm:table-cell">{p.winRate}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
