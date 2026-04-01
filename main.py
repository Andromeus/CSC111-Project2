"""CSC111 Winter 2026 Project 2: Interactive Main Program

Instructions
===========

Run this file to play a game of AlignQuattro against an MCTS Ai with difficulty of your choosing. You can choose
between text visualization and pygame visualization modes.

Copyright and Usage Information
===============================

This file is the intellectual property of the AlignQuattro Team. It may not
be copied, modified, distributed, or used without the permission of the
authors.

Copyright (c) 2026 AlignQuattro Team
"""

import game_logic
import game_display
import player_mcts


def run_game_console(red: game_logic.Player, yellow: game_logic.Player) -> tuple[str, list[tuple[str, int, int]]]:
    """Run a AlignQuattor game between the two given players. Visualize in the console

    Return the outcome: either 'red win', 'yellow win', or 'tie'.
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
    Run a AlignQuattro game between the two given players.
    Initializes a AlignQuattorVisualization object, which is the pygame game of AlignQuattro
    and starts the game on the main screen
    """
    vis = game_display.AlignQuattroVisualization(game_logic.HumanPlayerPygame(), game_logic.RandomPlayer())
    vis.start_game()


def get_ai_info() -> game_logic.Player | player_mcts.MCTSPlayer:
    """ Get info for AI if player is an AI

    Return a random AI or a MCTS AI

    MCTS AI has a chosen difficulty(number of cycles), which can be one of the prechosen
    settings: easy, medium, or hard, or with a custom amount of cycles and can be chosed to be DAG or not be DAG,
    and with Heuristics or without
    """
    ai_choice = input("Choose the AI type: random, MCTS, DAG \n").lower().strip()
    while ai_choice not in {"random", "mcts", "dag"}:
        print("invalid input")
        ai_choice = input("Choose the AI type: random, MCTS, DAG \n").lower().strip()
    print("=" * 40)
    if ai_choice == "random":
        ai = game_logic.RandomPlayer
    else:
        if ai_choice == "mcts":
            dag = False
        else:
            dag = True
        difficulty = input("Choose difficulty — easy / medium / hard / custom: ").strip().lower()
        while difficulty not in {"easy", "medium", "hard", "custom"}:
            print('invalid input')
            difficulty = input("Choose difficulty — easy / medium / hard / custom: ").strip().lower()
        if difficulty == "custom":
            sims = input("How many cycles do you want to run?: ")
            while not isinstance(int(sims), int):
                print('invalid input')
                sims = input("How many cycles do you want to run?: ")
            sims = int(sims)
        else:
            sims = {'easy': 400, 'hard': 10000}.get(difficulty, 1600)
        print("=" * 40)
        have_heuristics = input("Do you want heuristics? Y  |  N \n").lower().strip()
        while have_heuristics not in {"y", "n"}:
            print("invalid input")
            have_heuristics = input("Do you want heuristics? Y  |  N \n").lower().strip()
        print("=" * 40)
        if have_heuristics == "y":
            ai = player_mcts.MCTSPlayer(num_searches=sims, is_dag=dag, use_heuristics=True)
        else:
            ai = player_mcts.MCTSPlayer(num_searches=sims, is_dag=dag, use_heuristics=False)
    return ai


def main() -> None:
    """Run an interactive game of AlignQuattro against the MCTS AI.

    The player can choose to visualize the game in the console or in pygame

    If player chooses console, they can select how they want to play,
    the types of players and customize the players are they AI
    """
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

    elif gamemode in {"human vs ai", "ai vs human"}:
        print("You are playing Human vs AI")
        print("=" * 40)
        go_first = input("Do you want to go first? Y  |  N \n")
        while go_first.lower().strip() not in {"y", "n"}:
            print("invalid input")
            go_first = input("Do you want to go first? Y  |  N \n")
        ai = get_ai_info()
        if go_first == "y":
            outcome, _ = run_game_console(game_logic.HumanPlayer(), ai)
            print("\nYou are RED  (R)   |   AI is YELLOW  (Y)")
        else:
            outcome, _ = run_game_console(ai, game_logic.HumanPlayer())
            print("\nAI is RED  (R)   |   You are YELLOW  (Y)")
    else:
        print("You are playing Human vs Human")
        outcome, _ = run_game_console(game_logic.HumanPlayer(), game_logic.HumanPlayer())

    print("Columns are numbered 1–7 left to right.\n")

    if outcome == 'yellow win':
        print("Yellow Wins!")
    elif outcome == 'red win':
        print("Red Wins")
    else:
        print("It's a tie!")


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

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['static_type_checker'],
        'extra-imports': ['random', 'copy', 'game_display', 'game_logic', 'players', 'player_mcts'],
        'allowed-io': ['main', 'get_ai_info', 'run_game_console', 'run_game', 'run_games', 'print_simple_visual',
                       'HumanPlayer.make_move']
    })
