"""CSC111 Project 2 ALIGNQUATTRO

GAME LOGIC FILE

This file contains the basic game logic for a game of AlignQuattro (aka connect4). This includes
    - An AlignQuattroGame class, containing a 6x7 board and several methods like make_move and check_win to
    help run a game of AlignQuattro
    - A Piece class, representing a single piece in an AlignQuattro game, which can be red, yellow, or empty
    - A Player abstract class with the abstract method make_move, and subclasses meant to implement different
    move stategies
    - methods run_game and run_games

"""

from __future__ import annotations

import random
import copy
import game_display


class AlignQuattroGame:
    """
    A class representing an Align Quattro Game

    Instance Attributes:
      - outcome: a string representing the outcome of the game (red win, yellow win, tie, or in progress)
      - _board: a 6 x 7 2d array of Piece objects, where self._board[0][0] is represents the top left of the board
      and self._board[5][6] represents the bottom right corner of the board.
      - _valid_moves: a dictionary mapping each column (integers 0-6) to the lowest available row
      (integers 0-5, or -1 if the column is full) to place a Piece
      - _is_red_move: bool for whether it is red player's turn or not

    Representation Invariants:
        - self.outcome in {'red win', 'yellow win', 'tie', 'in progress'}
        - len(self._board) == 6 and len(self._board[0]) == 7
        - all([x in self._valid_moves for x in range(0, 7)])
        - all([-1 <= self._valid_moves[y] <= 5 for y in range(0,7)])

    ***DOCTESTS HERE EVENTUALLY***

    """
    outcome: str
    _board: list[list[Piece]]
    _valid_moves: dict[int, int]
    _is_red_move: bool

    def __init__(self, board: list[list[Piece]] = None,
                 is_red_move: bool = True, game_outcome: str = 'in progress') -> None:
        """Initializes AlignQuattroGame"""
        if board is not None:
            self._board = board
        else:
            self._board = []
            self._valid_moves = {6: 5}
            for i in range(0, 6):
                self._board.append([])
                self._valid_moves[i] = 5
                for j in range(0, 7):
                    self._board[i].append(Piece(i, j))
        self._is_red_move = is_red_move
        self.outcome = game_outcome

    def get_available_columns(self) -> list[int]:
        """Returns a list of integers representing columns still open for moves (so 0-6)"""
        return [x for x in self._valid_moves if self._valid_moves[x] >= 0]

    def make_move(self, col: int) -> None:
        """Makes a move in an AlignQuattroGame, including four steps:
        Changes the piece_type of a piece from empty to red or yellow at the lowest available row in the given
        column of self._board,
        Toggles self._is_red_move to update whose turn it is,
        Updates self._valid_moves by subtracting one from the specified column to show that row has been filled, and
        Executes self.check_win to potentially update self.outcome if the game is ended by this move.

        Preconditions:
            - col in self.get_available_columns()

        """
        row = self._valid_moves[col]
        if self._is_red_move:
            player = 'red'
        else:
            player = 'yellow'
        self._board[row][col].set_piece_type(player)
        self._valid_moves[col] -= 1
        self.check_win(row, col)
        self._is_red_move = not self._is_red_move

    def check_win(self, r: int, c: int) -> None:
        """Checks for a win or a tie based on where a piece was placed. Assumes the piece was the last piece to
        be placed, and all pieces are up to date. Changes self.outcome to 'red win' 'yellow win' or 'tie', or
        leaves it as in progress if no wins or ties are found.

        Checks for ties by referencing self._valid_moves

        Checks for wins by searching through four possible win conditions:
        1. Vertical
        2. Horizontal
        3. Postive Diagonal
        4. Negative Diagonal

        Preconditions:
            - 0 <= r <= 5
            - 0 <= c <= 6
        """
        if self._is_red_move:
            player = 'red'
            win = 'red win'
        else:
            player = 'yellow'
            win = 'yellow win'

        vertical = self.check_direction_win(r, c, "vertical", player)
        horizontal = self.check_direction_win(r, c, "horizontal", player)
        pos_diag = self.check_direction_win(r, c, "positive diagonal", player)
        neg_diag = self.check_direction_win(r, c, "negative diagonal", player)

        if any([vertical, horizontal, pos_diag, neg_diag]):
            self.outcome = win
            return

        # check for a tie
        if all([self._valid_moves[x] == -1 for x in self._valid_moves]):
            self.outcome = 'tie'

    def check_direction_win(self, r: int, c: int, direction: str, player: str) -> bool:
        """Checks for horizontal, vertical, positive diagonal, and negative diagonal alignments of 4.

        Returns true if there are four in a row (or line anyway) and false otherwise.

        Preconditions:
            - 0 <= r <= 5
            - 0 <= c <= 6
            - direction in {"horizontal", "vertical", "positive diagonal", "negative diagonal"}
            - player in {'red', 'yellow'}
        """
        i = 1
        aligned_so_far = 1
        indices = self.update_row_col_indices(direction, r, c, i)
        first_row_index, first_col_index = indices[0], indices[1]
        second_row_index, second_col_index = indices[2], indices[3]

        while i < 4 and -1 < first_row_index < 6 and -1 < first_col_index < 7:
            if self._board[first_row_index][first_col_index].get_piece_type() == player:
                aligned_so_far += 1
                i += 1
                indices = self.update_row_col_indices(direction, r, c, i)
                first_row_index, first_col_index = indices[0], indices[1]
            else:
                i = 4
        i = 1
        while i < 4 and -1 < second_row_index < 6 and -1 < second_col_index < 7:
            if self._board[second_row_index][second_col_index].get_piece_type() == player:
                aligned_so_far += 1
                i += 1
                indices = self.update_row_col_indices(direction, r, c, i)
                second_row_index, second_col_index = indices[2], indices[3]
            else:
                i = 4
        return aligned_so_far >= 4

    def update_row_col_indices(self, direction: str, r: int, c: int, i: int) -> tuple[int, int, int, int]:
        """Helper function for the check_direction_win helper function which returns a tuple representing
        an update first_row_index, first_col_index, second_row_index, and second_col_index based direction and i

        Preconditions:
            - 0 <= r <= 5
            - 0 <= c <= 6
            - direction in {"horizontal", "vertical", "positive diagonal", "negative diagonal"}
        """
        if direction == "horizontal":
            first_row_index, first_col_index, second_row_index, second_col_index = r, c + i, r, c - i
        elif direction == "positive diagonal":
            first_row_index, first_col_index, second_row_index, second_col_index = r + i, c + i, r - i, c - i
        elif direction == "negative diagonal":
            first_row_index, first_col_index, second_row_index, second_col_index = r - i, c + i, r + i, c - i
        else:
            first_row_index, first_col_index, second_row_index, second_col_index = r + i, c, r - i, c
        return first_row_index, first_col_index, second_row_index, second_col_index

    def get_outcome(self) -> str:
        """Returns self.outcome"""
        return self.outcome

    def get_board(self) -> list[list[Piece]]:
        """Returns self._board."""
        return self._board

    def get_row_from_available_columns(self, input_col: int) -> int:
        """Returns the lowest row for the given column, or self._valid_moves[input_col]"""
        return self._valid_moves[input_col]


class Piece:
    """A class representing a red/yellow/empty piece in an Align Quattro game.

    Instance Attributes:
      - _piece_type: string representing the red, yellow, empty)
      - _row_pos: integer representing a piece's row position in a given AlignQuattroGame board
      - _col_pos: integer representing a piece's column position in a given AlignQuattroGame board

    Representation Invariants:
      - self._piece_type in {'red', 'yellow', 'empty'}
      - 0 <= self._row_pos <= 5
      - 0 <= self._col_pos <= 6

    """

    _piece_type: str
    _row_pos: int
    _col_pos: int

    def __init__(self, row_val: int, col_val: int, p_type: str = 'empty') -> None:
        """Initializes Piece as empty by default, or else as a specified type, either 'red' or 'yellow'"""
        self._piece_type = p_type
        self._row_pos = row_val
        self._col_pos = col_val

    def get_piece_type(self) -> str:
        """Returns self._piece_type"""
        return self._piece_type

    def set_piece_type(self, set_type: str) -> None:
        """Sets self._piece_type to the specified type

        Preconditions:
            - set_type in {'red', 'yellow', 'empty'}
        """
        self._piece_type = set_type


class Player:
    """An abstract class representing an AlignQuattro AI.

    This class can be subclassed to implement different strategies for playing AlignQuattro.
    """

    def make_move(self, game: AlignQuattroGame) -> int:
        """Make a move given the current game.

        Preconditions:
            - There is at least one valid move for the given game
        """
        raise NotImplementedError


class RandomPlayer(Player):
    """An AlignQuattro player whose strategy is to make a random move each turn."""

    def make_move(self, game: AlignQuattroGame) -> int:
        """Make a move given the current game.

        Preconditions:
            - There is at least one valid move for the given game
        """
        possible_moves = game.get_available_columns()
        return random.choice(possible_moves)


class HumanPlayer(Player):
    """An AlignQuattro player which take real human input to make human decided moves each turn."""

    def make_move(self, game: AlignQuattroGame) -> int:
        """Waits for human player to type a number 1 - 7 to select a column."""
        choice = input("Choose a column, 1-7: ")
        options = {'1', '2', '3', '4', '5', '6', '7'}
        while choice not in options:
            print("That was an invalid option; try again.")
            choice = input("\nChoose a column, 1-7: ")
        return int(choice) - 1


################################################################################
# Functions for running games
################################################################################

def run_games(n: int, red: Player, yellow: Player, visualization_type: str = "none") -> None:
    """Run n games using the given Players. Visualize with the specified visualization request.

    Preconditions:
        - n >= 1
        - visualization_type in {"none", "text", "pygame"}
    """
    stats = {'red win': 0, 'yellow win': 0, 'tie': 0}
    for i in range(0, n):
        red_copy = copy.deepcopy(red)
        yellow_copy = copy.deepcopy(yellow)

        winner, _ = run_game(red_copy, yellow_copy, visualization_type)
        stats[winner] += 1
        print(f'Game {i} winner: {winner}')

    for outcome in stats:
        print(f'{outcome}: {stats[outcome]}/{n} ({100.0 * stats[outcome] / n:.2f}%)')


def run_game(red: Player, yellow: Player, visualization_type: str = "none") -> tuple[str, list[tuple[str, int, int]]]:
    """Run a Minichess game between the two given players. Visualize with the given visualization request.

    Return the outcome: either 'red win', 'yellow win', or 'tie'.

    Preconditions:
        - visualization_type in {"none", "text", "pygame"}
    """
    game = AlignQuattroGame()

    move_sequence = []
    current_player = red
    player_str = "red"
    row_input, col_input = -1, -1
    vis = None
    if visualization_type == "pygame":
        vis = game_display.AlignQuattroVisualization()
    while game.get_outcome() == "in progress":
        if visualization_type == "text":
            print_simple_visual(game.get_board())
        elif visualization_type == "pygame" and row_input != -1:
            vis.draw_circle(row_input, col_input, player_str == "red")
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


def print_simple_visual(board: list[list[Piece]]) -> None:
    """Prints out a visualization of a board, with Os Rs and Ys for empty, red, and yellow."""
    visual = "ALIGNQUATTRO BOARD: \n"
    for r in range(0, 6):
        for c in range(0, 7):
            if board[r][c].get_piece_type() == "empty":
                piece = "O "
            elif board[r][c].get_piece_type() == "red":
                piece = "R "
            else:
                piece = "Y "
            visual += piece
        visual += "\n"
    print(visual)


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['static_type_checker'],
    #     'extra-imports': ['random', 'copy', 'game_display'],
    #     'allowed-io': ['run_game', 'run_games', 'print_simple_visual', 'HumanPlayer.make_move']
    #
    # })
