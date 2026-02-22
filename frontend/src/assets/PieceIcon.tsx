import React from 'react';

export const PieceIcon: React.FC<{ type: string; color: string; className?: string }> = ({ type, color, className }) => {
  const isWhite = color === 'w';
  
  // High-fidelity SVG paths for Staunton-style pieces
  const piecePaths: Record<string, React.ReactNode> = {
    p: (
      <g fill={isWhite ? "#fff" : "#000"} stroke={isWhite ? "#000" : "#fff"} strokeWidth="1.5">
        <path d="M12 9c1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3 1.34 3 3 3zM15 15c0-2-1.34-3.5-3-3.5s-3 1.5-3 3.5c0 1.5 1 2.5 1.5 3h3c.5-.5 1.5-1.5 1.5-3zM9 21h6v-2H9v2z" />
      </g>
    ),
    n: (
      <g fill={isWhite ? "#fff" : "#000"} stroke={isWhite ? "#000" : "#fff"} strokeWidth="1.5">
        <path d="M16 19s-1.5-3-1.5-5c0-1.5 1-2.5 1-4.5 0-3-2.5-5.5-5.5-5.5-2 0-3.5 1-4.5 2.5-.5.5-1 1.5-1 2.5 0 2 1.5 3 1 5-.5 2.5-2.5 5-2.5 5h13z" />
        <path d="M8 9a1 1 0 1 0 0-2 1 1 0 0 0 0 2z" />
      </g>
    ),
    b: (
      <g fill={isWhite ? "#fff" : "#000"} stroke={isWhite ? "#000" : "#fff"} strokeWidth="1.5">
        <path d="M12 3c-1.5 0-3 1.5-3 3.5 0 1 .5 2 1.5 3 .5.5 1.5 1.5 1.5 2.5v1h-4v2h8v-2h-4v-1c0-1 1-2 1.5-2.5 1-1 1.5-2 1.5-3 0-2-1.5-3.5-3-3.5z" />
        <path d="M9 21h6v-2H9v2zM12 6v3" />
      </g>
    ),
    r: (
      <g fill={isWhite ? "#fff" : "#000"} stroke={isWhite ? "#000" : "#fff"} strokeWidth="1.5">
        <path d="M8 4h1v2h2V4h2v2h2V4h1v5H8V4zM8 9h8v3H8V9zM9 12l-1 7h8l-1-7H9zM8 21h8v-2H8v2z" />
      </g>
    ),
    q: (
      <g fill={isWhite ? "#fff" : "#000"} stroke={isWhite ? "#000" : "#fff"} strokeWidth="1.5">
        <path d="M12 4c1 0 1.5 1 1.5 2s-.5 2-1.5 2-1.5-1-1.5-2 .5-2 1.5-2zM8 8s-1.5 2-1.5 5c0 1.5 1 2.5 1.5 3.5h8c.5-1 1.5-2 1.5-3.5 0-3-1.5-5-1.5-5L12 11 8 8z" />
        <path d="M8 21h8v-2H8v2z" />
      </g>
    ),
    k: (
      <g fill={isWhite ? "#fff" : "#000"} stroke={isWhite ? "#000" : "#fff"} strokeWidth="1.5">
        <path d="M12 2v3M10.5 3.5h3M12 5c-1.5 0-3 1.5-3 3.5 0 2 1.5 3 2.5 4-1 1.5-2.5 3.5-2.5 5.5h6c0-2-1.5-4-2.5-5.5 1-1 2.5-2 2.5-4 0-2-1.5-3.5-3-3.5z" />
        <path d="M8 21h8v-2H8v2z" />
      </g>
    )
  };

  return (
    <svg viewBox="0 0 24 24" className={className} xmlns="http://www.w3.org/2000/svg">
      {piecePaths[type.toLowerCase()]}
    </svg>
  );
};
