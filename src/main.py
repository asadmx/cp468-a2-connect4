"""
Interactive / demo entry point.

Modes:
    python main.py human    -- you (player 1) vs Minimax agent (player 2)
    python main.py demo     -- watch two agents play each other, printing the board
    python main.py          -- defaults to demo: RuleBased vs Minimax

Use this file for your demonstration video: run a couple of AI-vs-AI
matches and narrate what's happening, then show one full game.
"""

import random
import sys
import time

from engine import new_board, apply_move, is_terminal, winner, legal_moves, print_board
from agents import RandomAgent, RuleBasedAgent, MinimaxAgent, timed_choose_move


def demo_match(agent1, agent2, seed=1, delay=0.0):
    rng = random.Random(seed)
    board = new_board()
    agents = {1: agent1, 2: agent2}
    current = 1
    move_num = 0

    print(f"=== {agent1.name} (X) vs {agent2.name} (O) | seed={seed} ===\n")
    print(print_board(board))
    print()

    while not is_terminal(board):
        agent = agents[current]
        move, elapsed = timed_choose_move(agent, board, current, rng)
        board = apply_move(board, move, current)
        move_num += 1
        print(f"Move {move_num}: {agent.name} (player {current}) plays column {move} "
              f"(decided in {elapsed*1000:.2f} ms)")
        print(print_board(board))
        print()
        current = 2 if current == 1 else 1
        if delay:
            time.sleep(delay)

    w = winner(board)
    if w == 0:
        print("Result: DRAW")
    else:
        winner_agent = agents[w]
        print(f"Result: {winner_agent.name} (player {w}) WINS")


def human_vs_agent(agent, human_player=1, seed=1):
    rng = random.Random(seed)
    board = new_board()
    ai_player = 2 if human_player == 1 else 1
    current = 1

    print(f"You are player {human_player}. {agent.name} is player {ai_player}.")
    print(print_board(board))
    print()

    while not is_terminal(board):
        if current == human_player:
            valid = legal_moves(board)
            move = None
            while move not in valid:
                try:
                    move = int(input(f"Your move, choose column {valid}: "))
                except ValueError:
                    continue
        else:
            move, elapsed = timed_choose_move(agent, board, current, rng)
            print(f"{agent.name} plays column {move} ({elapsed*1000:.2f} ms)")

        board = apply_move(board, move, current)
        print(print_board(board))
        print()
        current = 2 if current == 1 else 1

    w = winner(board)
    if w == 0:
        print("Result: DRAW")
    elif w == human_player:
        print("Result: YOU WIN")
    else:
        print("Result: AI WINS")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "demo"

    if mode == "human":
        human_vs_agent(MinimaxAgent(depth=4), human_player=1, seed=int(time.time()))
    elif mode == "demo":
        demo_match(RuleBasedAgent(), MinimaxAgent(depth=4), seed=7)
    else:
        print("Usage: python main.py [human|demo]")
