import React, { useEffect, useRef } from 'react';

interface ScoreSheetProps {
  moves: string[];
}

export const ScoreSheet: React.FC<ScoreSheetProps> = ({ moves }) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [moves]);

  // Group moves into pairs (White, Black)
  const groupedMoves = [];
  for (let i = 0; i < moves.length; i += 2) {
    groupedMoves.push({
      number: Math.floor(i / 2) + 1,
      white: moves[i],
      black: moves[i + 1] || null
    });
  }

  return (
    <div className="flex flex-col h-full bg-parchment/95 text-mahogany-dark rounded-sm shadow-inner overflow-hidden border border-mahogany/20">
      <div className="px-4 py-2 bg-mahogany/10 border-b border-mahogany/20 flex justify-between items-center">
        <span className="font-serif font-bold italic">Score Sheet</span>
        <span className="text-xs font-mono uppercase opacity-60">FIDE Standard</span>
      </div>
      
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 font-mono text-sm space-y-1 scroll-smooth"
      >
        {groupedMoves.map((m, idx) => (
          <div key={idx} className="grid grid-cols-[30px_1fr_1fr] gap-4 py-1 border-b border-mahogany/5 last:border-0 hover:bg-mahogany/5 transition-colors">
            <span className="text-mahogany/40 font-bold">{m.number}.</span>
            <span className="font-bold">{m.white}</span>
            <span className="font-bold opacity-80">{m.black || '...'}</span>
          </div>
        ))}
        {moves.length === 0 && (
          <div className="h-full flex items-center justify-center italic text-mahogany/40">
            No moves recorded
          </div>
        )}
      </div>
      
      <div className="p-2 bg-mahogany text-parchment text-[10px] uppercase tracking-tighter text-center font-bold">
        Chessmaster Study Edition
      </div>
    </div>
  );
};
