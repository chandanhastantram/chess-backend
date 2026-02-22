import { useState, useEffect } from 'react';
import { Chess, type Square } from 'chess.js';
import { useGameStore } from '../store/gameStore';
import { useWebSocket } from '../hooks/useWebSocket';

// Chess.com standard piece unicode characters
const PIECE_CHARS: Record<string, string> = {
  'wk': '♔', 'wq': '♕', 'wr': '♖', 'wb': '♗', 'wn': '♘', 'wp': '♙',
  'bk': '♚', 'bq': '♛', 'br': '♜', 'bb': '♝', 'bn': '♞', 'bp': '♟',
};

export const Chessboard = () => {
  const { fen, turn, playerColor, game_id } = useGameStore();
  const { sendMove } = useWebSocket(game_id);
  const [chess] = useState(new Chess(fen));
  const [selectedSquare, setSelectedSquare] = useState<string | null>(null);
  const [validMoves, setValidMoves] = useState<string[]>([]);
  const [lastMove, setLastMove] = useState<{ from: string; to: string } | null>(null);

  useEffect(() => {
    chess.load(fen);
  }, [fen, chess]);

  const onSquareClick = (square: string) => {
    // Spectators can't move
    if (playerColor === 'spectator') return;
    // Not your turn
    if ((turn === 'white' && playerColor !== 'white') || (turn === 'black' && playerColor !== 'black')) return;

    if (selectedSquare === square) {
      setSelectedSquare(null);
      setValidMoves([]);
      return;
    }

    const piece = chess.get(square as Square);

    // Select a piece of your color
    if (piece && piece.color === (playerColor === 'white' ? 'w' : 'b')) {
      setSelectedSquare(square);
      const moves = chess.moves({ square: square as Square, verbose: true });
      setValidMoves(moves.map(m => m.to));
      return;
    }

    // Move to target
    if (selectedSquare) {
      const moves = chess.moves({ square: selectedSquare as Square, verbose: true });
      const move = moves.find(m => m.to === square);

      if (move) {
        setLastMove({ from: selectedSquare, to: square });
        sendMove(move.lan);
        setSelectedSquare(null);
        setValidMoves([]);
      } else {
        setSelectedSquare(null);
        setValidMoves([]);
      }
    }
  };

  const isFlipped = playerColor === 'black';
  const ranks = isFlipped ? [0,1,2,3,4,5,6,7] : [7,6,5,4,3,2,1,0];
  const files = isFlipped ? [7,6,5,4,3,2,1,0] : [0,1,2,3,4,5,6,7];
  const fileLetters = 'abcdefgh';

  return (
    <div className="relative select-none">
      <div className="grid grid-cols-8 grid-rows-8 rounded-board overflow-hidden shadow-lg" style={{ aspectRatio: '1' }}>
        {ranks.map((rank, ri) =>
          files.map((file, fi) => {
            const sq = `${fileLetters[file]}${rank + 1}`;
            const isLight = (rank + file) % 2 === 0;
            const piece = chess.get(sq as Square);
            const isSelected = selectedSquare === sq;
            const isValid = validMoves.includes(sq);
            const isLast = lastMove?.from === sq || lastMove?.to === sq;

            let bgColor = isLight ? 'bg-board-light' : 'bg-board-dark';
            if (isSelected) bgColor = isLight ? 'bg-board-lastLight' : 'bg-board-lastDark';
            if (isLast && !isSelected) bgColor = isLight ? 'bg-board-lastLight' : 'bg-board-lastDark';

            return (
              <div
                key={sq}
                onClick={() => onSquareClick(sq)}
                className={`relative flex items-center justify-center cursor-pointer ${bgColor}`}
              >
                {/* Piece */}
                {piece && (
                  <span
                    className="text-[clamp(1.5rem,5vw,3.5rem)] leading-none select-none"
                    style={{
                      filter: piece.color === 'b' ? 'drop-shadow(0 1px 1px rgba(0,0,0,0.3))' : 'drop-shadow(0 1px 2px rgba(0,0,0,0.2))',
                      color: piece.color === 'w' ? '#fff' : '#000',
                      textShadow: piece.color === 'w' ? '0 0 3px rgba(0,0,0,0.4)' : '0 0 2px rgba(255,255,255,0.1)',
                    }}
                  >
                    {PIECE_CHARS[`${piece.color}${piece.type}`]}
                  </span>
                )}

                {/* Legal move dot */}
                {isValid && !piece && (
                  <div className="w-[25%] h-[25%] rounded-full bg-black/20" />
                )}
                {/* Legal move capture ring */}
                {isValid && piece && (
                  <div className="absolute inset-[6%] rounded-full border-[3px] border-black/20" />
                )}

                {/* Coordinates */}
                {fi === 0 && (
                  <span className={`absolute top-0.5 left-1 text-[10px] font-bold ${isLight ? 'text-board-dark' : 'text-board-light'}`}>
                    {rank + 1}
                  </span>
                )}
                {ri === 7 && (
                  <span className={`absolute bottom-0 right-1 text-[10px] font-bold ${isLight ? 'text-board-dark' : 'text-board-light'}`}>
                    {fileLetters[file]}
                  </span>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
