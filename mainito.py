"""CSC111 Project 2 ALIGNQUATTRO

MAIN FILE

Run this file to play a game of AlignQuattro against the MCTS AI.
"""

from game_logic_2 import HumanPlayer, RandomPlayer, run_game, run_games
from player_mcts_2 import MCTSPlayer


def main() -> None:
    """Run an interactive game of AlignQuattro against the MCTS AI."""

    print("=" * 40)
    print("   Welcome to ALIGNQUATTRO (Connect 4)")
    print("=" * 40)
    print("\nYou are RED  (R)   |   AI is YELLOW  (Y)")
    print("Columns are numbered 1–7 left to right.\n")

    # Tune num_searches for difficulty:
    #   200  → easy/fast   (~50ms per AI move)
    #   800  → medium      (~200ms per AI move)
    #   2000 → hard        (~500ms per AI move)
    difficulty = input("Choose difficulty — easy / medium / hard (default: medium): ").strip().lower()
    sims = {'easy': 400, 'hard': 5000}.get(difficulty, 1600)

    human = HumanPlayer()
    ai = MCTSPlayer(num_searches=sims, is_dag=True)

    colour = input("\nDo you want to go first? (yes / no, default: yes): ").strip().lower()

    if colour == 'no':
        print("\nAI goes first. Good luck!\n")
        outcome, _ = run_game(ai, human, visualization_type="text")
        if outcome == 'yellow win':
            print("You win! Well done.")
        elif outcome == 'red win':
            print("AI wins! Better luck next time.")
        else:
            print("It's a tie!")
    else:
        print("\nYou go first. Good luck!\n")
        outcome, _ = run_game(human, ai, visualization_type="text")
        if outcome == 'red win':
            print("You win! Well done.")
        elif outcome == 'yellow win':
            print("AI wins! Better luck next time.")
        else:
            print("It's a tie!")


if __name__ == '__main__':
    main()
