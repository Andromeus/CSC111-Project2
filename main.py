"""CSC111 Project 2 ALIGNQUATTRO

MAIN FILE

Run this file to play a game of AlignQuattro against an MCTS Ai with difficulty of your choosing.

Can choose between text visualization and pygame visualization.
"""
from sympy.series.limits import heuristics

import game_logic
import game_display
import players
import player_mcts
import player_mcts_2


def run_game_console(red: players.Player, yellow: players.Player) -> tuple[str, list[tuple[str, int, int]]]:
    """Run a Minichess game between the two given players. Visualize with the given visualization request.

    Return the outcome: either 'red win', 'yellow win', or 'tie'.

    Preconditions:
        - visualization_type in {"none", "text", "pygame"}
    """
    game = game_logic.AlignQuattroGame()

    move_sequence = []
    current_player = red
    while game.get_outcome() == "in progress":
        game_logic.print_simple_visual(game.get_board())
        col_input = current_player.make_move(game)
        row_input = game.get_row_from_available_columns(col_input)
        game.make_move(col_input)
        if current_player is red:
            current_player = yellow
            player_str = "red"
        else:
            current_player = red
            player_str = "yellow"
        move_sequence.append((player_str, row_input, col_input))
        # can pass row_input, col_input to pygame here
    return game.get_outcome(), move_sequence


def run_game_pygame() -> None:
    """
    Opens pygame version of alignquattro
    """
    vis = game_display.AlignQuattroVisualization(players.HumanPlayerPygame(), players.RandomPlayer())
    vis.start_game()


def get_ai_info() -> players.Player | player_mcts.MCTSPlayer | player_mcts_2.MCTSPlayer:
    aiChoice = input("Choose the AI type: random, MCTS, DAG \n").lower().strip()
    while aiChoice not in {"random", "mcts", "dag"}:
        print("invalid input")
        aiChoice = input("Choose the AI type: random, MCTS, DAG \n").lower().strip()
    print("=" * 40)
    if aiChoice == "random":
        ai = players.RandomPlayer
    else:
        if aiChoice == "mcts":
            dag = False
        else:
            dag = True
        difficulty = input("Choose difficulty — easy / medium / hard / custom: ").strip().lower()
        while difficulty not in {"easy", "medium", "hard", "custom"}:
            print('invalid input')
            difficulty = input("Choose difficulty — easy / medium / hard / custom: ").strip().lower()
        if difficulty == "custom":
            sims = input("How many cycles do you want to run?: ")
            while not isinstance(sims, int):
                print('invalid input')
                sims = input("How many cycles do you want to run?: ")
        else:
            sims = {'easy': 400, 'hard': 7000}.get(difficulty, 1600)
        print("=" * 40)
        heuristics = input("Do you want heuristics? Y  |  N \n")
        while heuristics.strip().lower() not in {"y", "n"}:
            print("invalid input")
            heuristics = input("Do you want heuristics? Y  |  N \n")
        print("=" * 40)
        if heuristics.lower().strip() == "y":
            ai = player_mcts_2.MCTSPlayer(num_searches=sims, is_dag=dag)
        else:
            ai = player_mcts.MCTSPlayer(num_searches=sims, is_dag=dag)
    return ai


def main() -> None:
    """Run an interactive game of AlignQuattro against the MCTS AI."""
    play_mode = input("Choose your visualization method: Console  |  Pygame \n")
    while play_mode.strip().lower() not in {"console", "pygame"}:
        print("Invalid Choice")
        play_mode = input("Choose how you want to play: Console  |  Pygame \n")
    if play_mode == "pygame":
        run_game_pygame()
    print("=" * 40)

    gamemode = input("Choose how you want to play: AI vs AI  |  Human vs AI  |  Human vs Human \n")
    while gamemode.strip().lower() not in {"ai vs ai", "human vs ai", "ai vs human", "human vs human"}:
        print("Invalid choice")
        gamemode = input("Choose how you want to play: AI vs AI  |  Human vs AI  |  Human vs Human \n")

    if gamemode == "ai vs ai":
        print("You are playing AI vs AI")
        print("=" * 40)
        ai1 = get_ai_info()
        ai2 = get_ai_info()
        outcome, _ = run_game_console(ai1, ai2)

    elif gamemode == "human vs ai" or "ai vs human":
        print("You are playing Human vs AI")
        print("=" * 40)
        ai = get_ai_info()
        go_first = input("Do you want to go first? Y  |  N \n")
        while go_first.lower().strip() not in {"y", "n"}:
            print("invalid input")
            go_first = input("Do you want to go first? Y  |  N \n")
        if go_first == "y":
            outcome, _ = run_game_console(players.HumanPlayer(), ai)
            print("\nYou are RED  (R)   |   AI is YELLOW  (Y)")
        else:
            outcome, _ = run_game_console(ai, players.HumanPlayer())
            print("\nAI is RED  (R)   |   You are YELLOW  (Y)")
    else:
        print("You are playing Human vs Human")
        outcome, _ = run_game_console(players.HumanPlayer(), players.HumanPlayer())

    print("Columns are numbered 1–7 left to right.\n")

    if outcome == 'yellow win':
        print("Yellow Wins!")
    elif outcome == 'red win':
        print("Red Wins")
    else:
        print("It's a tie!")


    # # Tune num_searches for difficulty:
    # #   200  → easy/fast   (~50ms per AI move)
    # #   800  → medium      (~200ms per AI move)
    # #   2000 → hard        (~500ms per AI move)
    # difficulty = input("Choose difficulty — easy / medium / hard (default: medium): ").strip().lower()
    #
    #
    # colour = input("\nDo you want to go first? (yes / no, default: yes): ").strip().lower()
    #
    # if colour == 'no':
    #     print("\nAI goes first. Good luck!\n")
    #
    # else:
    #     print("\nYou go first. Good luck!\n")
    #     outcome, _ = run_game_console(human, ai, visualization_type="text")
    #     if outcome == 'red win':
    #         print("You win! Well done.")
    #     elif outcome == 'yellow win':
    #         print("AI wins! Better luck next time.")
    #     else:
    #         print("It's a tie!")

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    running = True
    print("=" * 40)
    print("   Welcome to ALIGNQUATTRO (Connect 4)")
    print("=" * 40)
    while running:
        main()
        exit = input("Do you want to quit: Y  |  N \n")
        while exit.lower().strip() not in {"y", "n"}:
            print("invalid input")
            exit = input("Do you want to quit: Y  |  N \n")
        if exit == "y":
            running = False

    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['static_type_checker'],
    #     'extra-imports': ['random', 'copy', 'game_display'],
    #     'allowed-io': ['run_game', 'run_games', 'print_simple_visual', 'HumanPlayer.make_move']
    #
    # })
