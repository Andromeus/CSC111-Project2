"""CSC111 Project 2 ALIGNQUATTRO

EXPERIMENT FILE

This file contains experiments to measure and compare the strength of different
AlignQuattro AI configurations. This includes:
    - heuristics_vs_non_heuristics: measures whether the win rate advantage of
      heuristic rollouts over random rollouts grows as the number of simulations increases,
      by running 20 games at each simulation count with alternating colors to cancel
      out the first-move advantage
"""

from game_logic import run_game
from new import MCTSPlayer


def heuristics_vs_non_heuristics() -> None:
    """Does the heuristic advantage grow with more simulations?"""

    configs = [
        (200, 30),  # low sims -> high variance -> more games
        (500, 24),
        (1000, 18),
        (2000, 12),  # high sims -> low variance -> fewer games needed
    ]
    total_games = sum(config[1] for config in configs) * 2
    total_wins = 0
    for sims, n_games in configs:
        heuristic_wins = 0

        for _ in range(n_games):
            outcome, _ = run_game(MCTSPlayer(sims, use_heuristics=True),
                                  MCTSPlayer(sims, use_heuristics=False))
            if outcome == 'red win':
                heuristic_wins += 1
            elif outcome == 'tie':
                heuristic_wins += 0.5  # count ties as half a win

        for _ in range(n_games):
            outcome, _ = run_game(MCTSPlayer(sims, use_heuristics=False),
                                  MCTSPlayer(sims, use_heuristics=True))
            if outcome == 'yellow win':
                heuristic_wins += 1
            elif outcome == 'tie':
                heuristic_wins += 0.5
        total = n_games * 2
        total_wins += heuristic_wins
        print(f'Sims: {sims} || Heuristic win rate: {heuristic_wins / total * 100:.1f}% ({heuristic_wins}/{total})')
    print(f'Overall heuristic win rate: {total_wins/total_games * 100:.1f}% ({total_wins}/{total_games})')


if __name__ == '__main__':
    heuristics_vs_non_heuristics()
