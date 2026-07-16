"""
Three Connect Four agents, all sharing the engine's interface.

Every agent implements:
    choose_move(board, player, rng) -> column (int)

`rng` is a `random.Random` instance passed in by the caller so that all
randomness (including tie-breaking) is reproducible from a seed.
"""

import time
from engine import (
    ROWS, COLS, legal_moves, apply_move, winner, is_terminal, opponent
)


# ---------------------------------------------------------------------------
# Agent 1: Random Agent
# ---------------------------------------------------------------------------
class RandomAgent:
    name = "Random"

    def choose_move(self, board, player, rng):
        moves = legal_moves(board)
        return rng.choice(moves)


# ---------------------------------------------------------------------------
# Agent 2: Rule-Based Agent
# ---------------------------------------------------------------------------
class RuleBasedAgent:
    """
    Priority order (stated exactly, must match the report):
        1. If a move wins immediately, play it.
        2. Else, if the opponent has an immediate winning move, block it.
        3. Else, prefer central columns (score columns by distance to center).
        4. Else, extend own longest line / create threats
           (score each move by how many of the agent's own discs
           would end up adjacent in a line after the move).

    Whenever multiple moves are tied for best under whichever rule fired,
    choose uniformly at random among them (mandatory tie-breaking rule).
    """

    name = "RuleBased"

    CENTER = COLS // 2  # column 3

    def choose_move(self, board, player, rng):
        moves = legal_moves(board)
        opp = opponent(player)

        # Rule 1: winning move
        winning = [m for m in moves if self._wins_immediately(board, m, player)]
        if winning:
            return rng.choice(winning)

        # Rule 2: block opponent's winning move
        blocking = [m for m in moves if self._wins_immediately(board, m, opp)]
        if blocking:
            return rng.choice(blocking)

        # Rule 3 + 4 combined into a single score: center preference +
        # threat-building. We compute a score per move and take the max,
        # tie-breaking uniformly at random among the best.
        scored = [(m, self._move_score(board, m, player)) for m in moves]
        best_score = max(s for _, s in scored)
        best_moves = [m for m, s in scored if s == best_score]
        return rng.choice(best_moves)

    def _wins_immediately(self, board, col, player):
        try:
            result = apply_move(board, col, player)
        except ValueError:
            return False
        return winner(result) == player

    def _move_score(self, board, col, player):
        """
        Score = center-closeness + count of own discs the new disc
        would connect to (a simple 'extend my line / create threats' proxy).
        """
        result = apply_move(board, col, player)
        # Find the row the disc landed in
        row = None
        for r in range(ROWS):
            if board[r][col] == 0 and result[r][col] == player:
                row = r
                break

        center_score = -abs(col - self.CENTER)  # closer to center = higher

        # Count adjacent same-player discs in all 8 directions (1 step)
        # as a cheap proxy for "extends a line / builds a threat"
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1),
                      (0, 1), (1, -1), (1, 0), (1, 1)]
        adjacency_score = 0
        for dr, dc in directions:
            rr, cc = row + dr, col + dc
            if 0 <= rr < ROWS and 0 <= cc < COLS and result[rr][cc] == player:
                adjacency_score += 1

        return center_score + adjacency_score


# ---------------------------------------------------------------------------
# Agent 3: Minimax Agent (with windowed heuristic)
# ---------------------------------------------------------------------------
class MinimaxAgent:
    """
    Minimax with a fixed search depth and a windowed-scoring heuristic
    at the depth cutoff.

    Terminal evaluation (from the perspective of `player`, the agent to move
    at the root):
        win  -> +10_000_000
        loss -> -10_000_000
        draw ->  0

    Heuristic (non-terminal, at depth limit): slide every length-4 window
    across all rows, columns, and diagonals. Score each window:
        4 of agent's discs      -> +100000 (should already be caught as terminal)
        3 of agent's, 1 empty   -> +100
        2 of agent's, 2 empty   -> +10
        opponent windows mirrored with negative weight (blocking is valued
        slightly higher than attacking, a common Connect-4 heuristic choice)
    Plus a small bonus per disc in the center column.
    """

    name = "Minimax"

    def __init__(self, depth=4):
        self.depth = depth

    def choose_move(self, board, player, rng):
        moves = legal_moves(board)
        opp = opponent(player)

        best_score = -float("inf")
        best_moves = []
        for m in moves:
            child = apply_move(board, m, player)
            score = self._minimax(child, self.depth - 1, -float("inf"),
                                   float("inf"), False, player, opp)
            if score > best_score:
                best_score = score
                best_moves = [m]
            elif score == best_score:
                best_moves.append(m)

        return rng.choice(best_moves)

    def _minimax(self, board, depth, alpha, beta, maximizing, player, opp):
        win = winner(board)
        if win == player:
            return 10_000_000 + depth  # prefer faster wins
        if win == opp:
            return -10_000_000 - depth  # prefer slower losses
        if is_terminal(board):
            return 0  # draw (board full, no winner)
        if depth == 0:
            return self._evaluate(board, player, opp)

        moves = legal_moves(board)
        if maximizing:
            value = -float("inf")
            for m in moves:
                child = apply_move(board, m, player)
                value = max(value, self._minimax(child, depth - 1, alpha,
                                                   beta, False, player, opp))
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:
            value = float("inf")
            for m in moves:
                child = apply_move(board, m, opp)
                value = min(value, self._minimax(child, depth - 1, alpha,
                                                   beta, True, player, opp))
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return value

    # ---- heuristic evaluation -------------------------------------------
    def _evaluate(self, board, player, opp):
        score = 0

        # Center column control
        center_col = COLS // 2
        center_count = sum(1 for r in range(ROWS) if board[r][center_col] == player)
        score += center_count * 6

        # All length-4 windows: horizontal, vertical, both diagonals
        for window in self._all_windows(board):
            score += self._score_window(window, player, opp)

        return score

    def _all_windows(self, board):
        windows = []
        # Horizontal
        for r in range(ROWS):
            for c in range(COLS - 3):
                windows.append([board[r][c + i] for i in range(4)])
        # Vertical
        for c in range(COLS):
            for r in range(ROWS - 3):
                windows.append([board[r + i][c] for i in range(4)])
        # Diagonal (up-right)
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                windows.append([board[r + i][c + i] for i in range(4)])
        # Diagonal (down-right)
        for r in range(3, ROWS):
            for c in range(COLS - 3):
                windows.append([board[r - i][c + i] for i in range(4)])
        return windows

    def _score_window(self, window, player, opp):
        own = window.count(player)
        opp_count = window.count(opp)
        empty = window.count(0)

        if own > 0 and opp_count > 0:
            return 0  # blocked window, worthless to either side

        if own == 3 and empty == 1:
            return 100
        if own == 2 and empty == 2:
            return 10
        if own == 1 and empty == 3:
            return 1

        if opp_count == 3 and empty == 1:
            return -120  # weight blocking slightly higher than attacking
        if opp_count == 2 and empty == 2:
            return -12
        if opp_count == 1 and empty == 3:
            return -1

        return 0


def timed_choose_move(agent, board, player, rng):
    """Helper: call an agent's choose_move and return (move, elapsed_seconds)."""
    start = time.perf_counter()
    move = agent.choose_move(board, player, rng)
    elapsed = time.perf_counter() - start
    return move, elapsed
