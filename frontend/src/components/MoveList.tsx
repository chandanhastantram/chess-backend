import { useEffect, useRef } from 'react';

interface MoveListProps {
  moves: string[];
  currentMoveIndex?: number;
  onMoveClick?: (index: number) => void;
}

export const MoveList = ({ moves, currentMoveIndex, onMoveClick }: MoveListProps) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [moves]);

  // Group into pairs
  const pairs: { num: number; white: string; black: string | null }[] = [];
  for (let i = 0; i < moves.length; i += 2) {
    pairs.push({
      num: Math.floor(i / 2) + 1,
      white: moves[i],
      black: moves[i + 1] || null,
    });
  }

  return (
    <div className="flex flex-col h-full bg-surface-200 rounded overflow-hidden">
      <div className="px-3 py-2 bg-surface-300 border-b border-surface-100 text-sm font-bold text-text-muted">
        Moves
      </div>
      <div ref={scrollRef} className="flex-1 overflow-y-auto">
        {pairs.length === 0 ? (
          <div className="p-6 text-center text-text-dim text-sm">
            Game hasn't started yet
          </div>
        ) : (
          pairs.map((pair, i) => (
            <div key={i} className="move-row">
              <div className="move-num">{pair.num}.</div>
              <div
                className={`move-cell ${currentMoveIndex === i * 2 ? 'bg-surface-400' : ''}`}
                onClick={() => onMoveClick?.(i * 2)}
              >
                {pair.white}
              </div>
              <div
                className={`move-cell ${currentMoveIndex === i * 2 + 1 ? 'bg-surface-400' : ''}`}
                onClick={() => onMoveClick?.(i * 2 + 1)}
              >
                {pair.black || ''}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
