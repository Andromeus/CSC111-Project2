# main file, we can combine everything into here later

import game_logic
import game_display
import player_mcts_2



def run_game(red: game_logic.Player, yellow: game_logic.Player, visualization_type: str = "none") -> tuple[str, list[tuple[str, int, int]]]:
    """Run a Minichess game between the two given players. Visualize with the given visualization request.

    Return the outcome: either 'red win', 'yellow win', or 'tie'.

    Preconditions:
        - visualization_type in {"none", "text", "pygame"}
    """
    game = game_logic.AlignQuattroGame()

    move_sequence = []
    current_player = red
    player_str = "red"
    row_input, col_input = -1, -1
    vis = None
    if visualization_type == "pygame":
        vis = game_display.AlignQuattroVisualization(red, yellow)
        vis.run_game()
    while game.get_outcome() == "in progress":
        if visualization_type == "text":
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


if __name__ == '__main__':
    import doctest
    doctest.testmod()
    run_game(game_logic.HumanPlayerPygame(), player_mcts_2.MCTSPlayer(), "pygame")

    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['static_type_checker'],
    #     'extra-imports': ['random', 'copy', 'game_display'],
    #     'allowed-io': ['run_game', 'run_games', 'print_simple_visual', 'HumanPlayer.make_move']
    #
    # })
