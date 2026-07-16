# CP468 Assignment 2 — Connect Four AI

## Team Members
- Asad Malik — Game engine implementation, correctness testing, project integration, report writing
- Saad Siddiqui — Rule-Based agent implementation
- Adam Ali — Minimax agent + heuristic evaluation implementation
- Daniyal Naqvi — Experiment harness, results analysis
- Omar Hamza — Demonstration video, README documentation

## Demonstration Video
[INSERT LINK HERE]

## Project Structure
```
A2/
├── README.md
├── Report.pdf
└── src/
    ├── engine.py       # Game engine: board, moves, win/draw detection
    ├── agents.py       # RandomAgent, RuleBasedAgent, MinimaxAgent
    ├── experiment.py   # Runs the 3 required pairings, 30 games each
    ├── main.py         # CLI: watch a demo match or play against the AI
    ├── results.json     # Raw per-game experiment output (generated)
    └── results.csv      # Summary table (generated)
```

## Requirements
- Python 3.10+ (tested on Python 3.12.3)
- No external libraries required — standard library only (`random`, `time`,
  `json`, `csv`).

## How to Run

### 1. Watch a demo match (AI vs AI)
```bash
cd src
python main.py demo
```
This runs RuleBased (X) vs Minimax (O, depth 4), seed=7, and prints the
board after every move along with each agent's decision time. Use this for
the demonstration video.

### 2. Play against the Minimax agent yourself
```bash
cd src
python main.py human
```
You are player 1 (X). Enter a column number (0-6) when prompted.

### 3. Reproduce the experimental results
```bash
cd src
python experiment.py
```
This runs all three required pairings:
- Random vs RuleBased
- RuleBased vs Minimax
- Minimax vs Random

Each pairing plays 30 games, alternating which agent moves first (15/15).
Minimax uses a fixed search depth of 4. Results are printed to the console
and written to `results.json` (full per-game log) and `results.csv`
(summary table with win rate, draw rate, and average decision time per
agent per pairing).

**Reproducibility:** every game's random source is a `random.Random`
seeded deterministically as `MASTER_SEED * 1000 + game_index`, with
`MASTER_SEED = 42` (see the top of `experiment.py`). Re-running
`experiment.py` with no changes will reproduce identical results.

## Machine Specs Used for Reported Timings
*(Fill in with the machine you actually ran the final experiments on —
this must match what you report in Report.pdf)*
- CPU: [e.g. Intel Core i7-1165G7 @ 2.80GHz]
- RAM: [e.g. 16 GB]
- OS: [e.g. Windows 11 / macOS 14 / Ubuntu 22.04]
- Language: Python 3.12.3

## Agent Summary
| Agent | Strategy |
|---|---|
| Random | Uniform random legal move |
| RuleBased | Win if possible → block opponent's win → prefer center → extend own lines/threats (see Report.pdf for exact rule priority) |
| Minimax | Depth-4 minimax with alpha-beta pruning; windowed heuristic (rows/cols/diagonals) + center-column bonus at the depth cutoff |

All tie-breaking (RuleBased and Minimax) is uniform-random over equally
scored moves, using the seeded RNG passed into `choose_move`.

## Academic Integrity
This implementation uses only the Python standard library
(`random`, `time`, `json`, `csv`). No external code or AI-generated
snippets were copied without modification — the Minimax and heuristic
design follows the guidance given in the assignment handout (windowed
scoring evaluation function).
