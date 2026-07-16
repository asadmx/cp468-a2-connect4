"""
Connect Four game engine.

Board representation:
    - 7 columns (0-6), 6 rows (0-5)
    - board[row][col], row 0 = bottom row, row 5 = top row
    - 0 = empty, 1 = player 1's disc, 2 = player 2's disc

This module has NO knowledge of any agent. Agents only interact with the
engine through the public functions below:

    new_board()
    legal_moves(board)
    apply_move(board, col, player)   -> new board (does not mutate input)
    is_terminal(board)
    winner(board)
    print_board(board)
"""

ROWS = 6
COLS = 7


def new_board():
    """Return a fresh empty board."""
    return [[0 for _ in range(COLS)] for _ in range(ROWS)]


def clone_board(board):
    return [row[:] for row in board]


def legal_moves(board):
    """Return list of column indices that are not full."""
    return [c for c in range(COLS) if board[ROWS - 1][c] == 0]


def apply_move(board, col, player):
    """
    Drop `player`'s disc into column `col`.
    Returns a NEW board (input is not mutated).
    Raises ValueError if the column is full or invalid.
    """
    if col < 0 or col >= COLS:
        raise ValueError(f"Invalid column: {col}")
    new = clone_board(board)
    for row in range(ROWS):
        if new[row][col] == 0:
            new[row][col] = player
            return new
    raise ValueError(f"Column {col} is full")


def _check_line(board, r, c, dr, dc, player):
    """Check for 4-in-a-row starting at (r,c) going in direction (dr,dc)."""
    for i in range(4):
        rr = r + dr * i
        cc = c + dc * i
        if rr < 0 or rr >= ROWS or cc < 0 or cc >= COLS:
            return False
        if board[rr][cc] != player:
            return False
    return True


def winner(board):
    """
    Return 1 or 2 if that player has won, else 0 (no winner yet / draw).
    """
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for r in range(ROWS):
        for c in range(COLS):
            player = board[r][c]
            if player == 0:
                continue
            for dr, dc in directions:
                if _check_line(board, r, c, dr, dc, player):
                    return player
    return 0


def is_full(board):
    return len(legal_moves(board)) == 0


def is_terminal(board):
    """Game over if someone has won or the board is full."""
    return winner(board) != 0 or is_full(board)


def print_board(board):
    """Text rendering, row 5 (top) printed first."""
    symbols = {0: ".", 1: "X", 2: "O"}
    lines = []
    for r in range(ROWS - 1, -1, -1):
        lines.append(" ".join(symbols[board[r][c]] for c in range(COLS)))
    lines.append(" ".join(str(c) for c in range(COLS)))
    return "\n".join(lines)


def opponent(player):
    return 2 if player == 1 else 1
