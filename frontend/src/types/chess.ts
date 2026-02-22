export type Color = 'w' | 'b';
export type PieceType = 'p' | 'n' | 'b' | 'r' | 'q' | 'k';

export interface Piece {
  type: PieceType;
  color: Color;
}

export interface Square {
  square: string;
  piece: Piece | null;
  isHighlighted?: boolean;
  isValidMove?: boolean;
  isLastMove?: boolean;
}

export interface GameInfo {
  game_id: string;
  white_player: string;
  black_player: string;
  time_control: string;
  status: string;
}
