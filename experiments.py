"""CSC111 Project 2 ALIGNQUATTRO

EXPERIMENT FILE

This file contains experiments to measure and compare the strength of different
AlignQuattro AI configurations. This includes:
    - heuristics_vs_non_heuristics: measures whether the win rate advantage of
      heuristic rollouts over random rollouts grows as the number of simulations increases,
      by running 20 games at each simulation count with alternating colors to cancel
      out the first-move advantage
"""
import random
import csv
from game_logic import run_game
from player_mcts import MCTSPlayer

random.seed(42)
# Simulation counts for the tested MCTS player
baseline_model_search_counts = [100, 200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000, 2200, 2400]
dag_vs_tree_model_search_counts = [100, 200, 400, 600, 800, 1000, 1200, 1400, 1600]

# Baseline model is the weak MCTS player with only 200 searches
baseline_model_search_count = 200
num_games = 20


def heuristics_vs_non_heuristics() -> None:
    """Does the heuristic advantage grow with more simulations?"""

    configs = [
        (200, 30),  # Since there are less simulations/searches, we increase the iterations to account for variance
        (500, 24),
        (1000, 18),
        (2000, 12),
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


def mcts_vs_baseline() -> None:
    """Run MCTS-vs-MCTS experiments and save the results to a CSV file.

    The baseline player always uses 100 searches for the MCTS, while the search count of the tested player iterates
    over baseline_model_search_counts. For each simulation count, games are alternated by colour so that the
    tested player can play both sides. The results are written to experiments_against_baseline.csv.
    """
    with open('experiments_against_baseline.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([
            'simulation_count',
            'games_played',
            'strong_wins',
            'strong_losses',
            'ties',
            'strong_win_rate'
        ])

        for searches in baseline_model_search_counts:
            strong_wins = 0
            strong_losses = 0
            ties = 0

            for game_num in range(num_games):
                strong_ai = MCTSPlayer(num_searches=searches, is_dag=True)
                weak_ai = MCTSPlayer(num_searches=baseline_model_search_count, is_dag=True)

                # Alternate colours to reduce bias of the tested player
                if game_num % 2 == 0:
                    red_player = strong_ai
                    yellow_player = weak_ai
                    strong_is_red = True
                else:
                    red_player = weak_ai
                    yellow_player = strong_ai
                    strong_is_red = False

                outcome, _ = run_game(
                    red_player,
                    yellow_player,
                    visualization_type='none'
                )

                if ((outcome == 'red win' and strong_is_red) or (outcome == 'yellow win' and not strong_is_red)):
                    strong_wins += 1
                elif outcome == 'tie':
                    ties += 1
                else:
                    strong_losses += 1

            strong_win_rate = (strong_wins + ties * 0.5) / num_games

            writer.writerow([
                searches,
                num_games,
                strong_wins,
                strong_losses,
                ties,
                round(strong_win_rate, 3)
            ])

            print(
                f"{searches} searches: "
                f"{strong_wins} strong wins, {strong_losses} strong losses, {ties} ties "
                f"(strong win rate = {strong_win_rate:.3f})"
            )


def run_tree_vs_dag_experiments() -> None:
    """Compare DAG-MCTS against tree-MCTS win rate for the same number of searches.

    The DAG win rate is recorded to experiments_dag_vs_tree.csv.
    """
    with open('experiments_dag_vs_tree.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)

        writer.writerow([
            'search_count',
            'games_played',
            'dag_wins',
            'tree_wins',
            'ties',
            'dag_win_rate'
        ])
        csv_file.flush()

        for searches in dag_vs_tree_model_search_counts:
            dag_wins = 0
            tree_wins = 0
            ties = 0

            for game_num in range(num_games):
                dag_ai = MCTSPlayer(
                    num_searches=searches,
                    is_dag=True
                )

                tree_ai = MCTSPlayer(
                    num_searches=searches,
                    is_dag=False
                )

                if game_num % 2 == 0:
                    red_player = dag_ai
                    yellow_player = tree_ai
                    dag_is_red = True
                else:
                    red_player = tree_ai
                    yellow_player = dag_ai
                    dag_is_red = False

                outcome, _ = run_game(
                    red_player,
                    yellow_player,
                    visualization_type='none'
                )

                if ((outcome == 'red win' and dag_is_red)
                        or (outcome == 'yellow win' and not dag_is_red)):
                    dag_wins += 1
                elif outcome == 'tie':
                    ties += 1
                else:
                    tree_wins += 1

            dag_win_rate = (dag_wins + ties * 0.5) / num_games

            writer.writerow([
                searches,
                num_games,
                dag_wins,
                tree_wins,
                ties,
                round(dag_win_rate, 3)
            ])
            csv_file.flush()

            print(
                f"{searches} searches: "
                f"DAG wins = {dag_wins}, Tree wins = {tree_wins}, Ties = {ties} "
                f"(DAG win rate = {dag_win_rate:.3f})"
            )

