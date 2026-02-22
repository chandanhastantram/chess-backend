"""Board theme routes — 4 chess board theme presets"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


# Theme data
BOARD_THEMES = {
    "classic": {
        "id": "classic",
        "name": "Classic",
        "description": "Traditional green and white chess board",
        "light_square": "#F0D9B5",
        "dark_square": "#B58863",
        "highlight": "#FFFF00",
        "move_indicator": "#82B1FF",
        "check_highlight": "#FF5252",
        "last_move_light": "#CDD16A",
        "last_move_dark": "#AAA23A",
    },
    "wood": {
        "id": "wood",
        "name": "Wood",
        "description": "Warm wooden board with walnut and maple tones",
        "light_square": "#E8C98E",
        "dark_square": "#A67C52",
        "highlight": "#FFD54F",
        "move_indicator": "#90CAF9",
        "check_highlight": "#E57373",
        "last_move_light": "#D4C46B",
        "last_move_dark": "#A09030",
    },
    "tournament": {
        "id": "tournament",
        "name": "Tournament",
        "description": "Official FIDE tournament green and cream board",
        "light_square": "#EEEED2",
        "dark_square": "#769656",
        "highlight": "#FFFF33",
        "move_indicator": "#5C93D1",
        "check_highlight": "#E06666",
        "last_move_light": "#F6F669",
        "last_move_dark": "#BACA44",
    },
    "dark": {
        "id": "dark",
        "name": "Dark",
        "description": "Sleek dark mode board for night play",
        "light_square": "#4B4B4B",
        "dark_square": "#2C2C2C",
        "highlight": "#8B8000",
        "move_indicator": "#5C6BC0",
        "check_highlight": "#C62828",
        "last_move_light": "#6B6B3B",
        "last_move_dark": "#4A4A20",
    },
}


class BoardThemeResponse(BaseModel):
    id: str
    name: str
    description: str
    light_square: str
    dark_square: str
    highlight: str
    move_indicator: str
    check_highlight: str
    last_move_light: str
    last_move_dark: str


@router.get("", response_model=list[BoardThemeResponse])
async def list_board_themes():
    """List all available board themes"""
    return list(BOARD_THEMES.values())


@router.get("/{theme_id}", response_model=BoardThemeResponse)
async def get_board_theme(theme_id: str):
    """Get a specific board theme by ID"""
    from fastapi import HTTPException, status

    theme = BOARD_THEMES.get(theme_id)
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Theme '{theme_id}' not found. Available: {list(BOARD_THEMES.keys())}"
        )
    return theme
