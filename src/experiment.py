"""
Experiment harness.

Plays a configurable number of games between two agents, alternating who
moves first, and records win/draw rates plus average decision time per move.

Usage:
    python experiment.py

Produces:
    results.json   -- raw per-game data
    results.csv    -- summary table (one row per pairing)
    Console output -- human-readable summary
"""

import csv
import json
import random
import sys

from engine import new_board, apply_move, is_terminal, winner, legal_moves
from agents import RandomAgent, RuleBasedAgent, MinimaxAgent, timed_choose_move

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
GAMES_PER_PAIRING = 30
MASTER_SEED = 42  # top-level seed; every game gets its own derived seed
MINIMAX_DEPTH = 4


def play_game(agent1, agent2, seed):
    """
    Play one game. agent1 is player 1 (moves first), agent2 is player 2.
    Returns a dict with the result and timing info.
    """
    rng = random.Random(seed)
    board = new_board()
    current_player = 1
    agents = {1: agent1, 2: agent2}
    times = {1: [], 2: []}
    move_count = 0

    while not is_terminal(board):
        agent = agents[current_player]
        move, elapsed = timed_choose_move(agent, board, current_player, rng)
        times[current_player].append(elapsed)
        board = apply_move(board, move, current_player)
        move_count += 1
        current_player = 2 if current_player == 1 else 1

    w = winner(board)
    return {
        "winner": w,  # 0 = draw, 1 = agent1, 2 = agent2
        "moves": move_count,
        "avg_time_p1": sum(times[1]) / len(times[1]) if times[1] else 0.0,
        "avg_time_p2": sum(times[2]) / len(times[2]) if times[2] else 0.0,
        "seed": seed,
    }


def run_pairing(name_a, agent_a_factory, name_b, agent_b_factory,
                 games=GAMES_PER_PAIRING, master_seed=MASTER_SEED):
    """
    Run `games` games between two agents, alternating who moves first
    (~half each way). Returns a summary dict and the list of per-game logs.
    """
    logs = []
    half = games // 2

    for i in range(games):
        # Fresh agent instances per game keeps things safe even if an
        # agent were to hold state (none of ours do, but this is good practice).
        agent_a = agent_a_factory()
        agent_b = agent_b_factory()
        seed = master_seed * 1000 + i

        if i < half:
            # A moves first
            result = play_game(agent_a, agent_b, seed)
            result["p1_name"], result["p2_name"] = name_a, name_b
        else:
            # B moves first
            result = play_game(agent_b, agent_a, seed)
            result["p1_name"], result["p2_name"] = name_b, name_a

        logs.append(result)

    # Aggregate
    a_wins = b_wins = draws = 0
    a_times, b_times = [], []

    for r in logs:
        if r["winner"] == 0:
            draws += 1
        else:
            winner_name = r["p1_name"] if r["winner"] == 1 else r["p2_name"]
            if winner_name == name_a:
                a_wins += 1
            else:
                b_wins += 1

        # attribute decision times back to the correct named agent
        if r["p1_name"] == name_a:
            a_times.append(r["avg_time_p1"])
            b_times.append(r["avg_time_p2"])
        else:
            b_times.append(r["avg_time_p1"])
            a_times.append(r["avg_time_p2"])

    summary = {
        "pairing": f"{name_a} vs {name_b}",
        "games": games,
        f"{name_a}_wins": a_wins,
        f"{name_b}_wins": b_wins,
        "draws": draws,
        f"{name_a}_win_rate": round(a_wins / games, 3),
        f"{name_b}_win_rate": round(b_wins / games, 3),
        "draw_rate": round(draws / games, 3),
        f"{name_a}_avg_decision_time_sec": round(sum(a_times) / len(a_times), 6),
        f"{name_b}_avg_decision_time_sec": round(sum(b_times) / len(b_times), 6),
        "seeds": f"{master_seed}000-{master_seed}000+{games - 1}",
    }
    return summary, logs


def main():
    pairings = [
        ("Random", RandomAgent, "RuleBased", RuleBasedAgent),
        ("RuleBased", RuleBasedAgent, "Minimax", lambda: MinimaxAgent(depth=MINIMAX_DEPTH)),
        ("Minimax", lambda: MinimaxAgent(depth=MINIMAX_DEPTH), "Random", RandomAgent),
    ]

    all_summaries = []
    all_logs = {}

    for name_a, factory_a, name_b, factory_b in pairings:
        print(f"Running {name_a} vs {name_b} ({GAMES_PER_PAIRING} games)...")
        summary, logs = run_pairing(name_a, factory_a, name_b, factory_b)
        all_summaries.append(summary)
        all_logs[f"{name_a}_vs_{name_b}"] = logs
        print(json.dumps(summary, indent=2))
        print()

    # Write JSON (raw)
    with open("results.json", "w") as f:
        json.dump({"summaries": all_summaries, "games": all_logs}, f, indent=2)

    # Write CSV (summary table)
    with open("results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["pairing", "games", "agent_a", "agent_a_wins",
                          "agent_a_win_rate", "agent_a_avg_time_sec",
                          "agent_b", "agent_b_wins", "agent_b_win_rate",
                          "agent_b_avg_time_sec", "draws", "draw_rate", "seeds"])
        for s in all_summaries:
            keys = list(s.keys())
            name_a = s["pairing"].split(" vs ")[0]
            name_b = s["pairing"].split(" vs ")[1]
            writer.writerow([
                s["pairing"], s["games"],
                name_a, s[f"{name_a}_wins"], s[f"{name_a}_win_rate"],
                s[f"{name_a}_avg_decision_time_sec"],
                name_b, s[f"{name_b}_wins"], s[f"{name_b}_win_rate"],
                s[f"{name_b}_avg_decision_time_sec"],
                s["draws"], s["draw_rate"], s["seeds"],
            ])

    print("Wrote results.json and results.csv")


if __name__ == "__main__":
    main()
