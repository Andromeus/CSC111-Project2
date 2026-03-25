"""CSC111 Project 2 (To be expanded)"""

from __future__ import annotations


class AlignQuattroGame:
    """
    A class representing an Align Quattro Game

    Instance Attributes:
      - _board: a 6 x 7 2d array of Piece objects, where self._board[0][0] is represents the top left of the board
      and self._board[5][6] represents the bottom right corner of the board.
      - _valid_moves: a dictionary mapping each column (integers 0-6) to the lowest available row
      (integers 0-5, or -1 if the column is full) to place a Piece
      - _is_red_move: bool for whether it is red player's turn or not

    Representation Invariants:
        - len(self._board) == 6 and len(self._board[0]) == 7
        - all([x in self._valid_moves for x in range(0, 7)])
        - all([-1 <= self._valid_moves[y] <= 5 for y in range(0,7)])

    ***DOCTESTS HERE EVENTUALLY***

    """

    _board: list[list[Piece]]
    _valid_moves: dict[int, int]
    _is_red_move: bool

    def __init__(self, board: list[list[Piece]] = None,
                 is_red_move: bool = True) -> None:
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


class Piece:
    """A class representing a red/yellow/empty piece in an Align Quattro game.

    Instance Attributes:
      - _piece_type: string representing the red, yellow, empty)
      - _row_pos: integer representing a piece's row position in a given AlignQuattroGame board
      - _col_pos: integer representing a piece's column position in a given AlignQuattroGame board

    Representation Invariants:
      - self._piece_type in {'red', 'yellow', 'empty'}
      - 0 <= self._row_pos <= 6
      - 0 <= self._col_pos <= 7

    """

    _piece_type: str
    _row_pos: int
    _col_pos: int

    def __init__(self, row_val: int, col_val: int, p_type: str='empty') -> None:
        """Initializes Piece as empty by default, or else as a specified type, either 'red' or 'yellow'"""

        self.piece_type = p_type
        self._row_pos = row_val
        self._col_pos = col_val


if __name__ == '__main__':
    import doctest
    doctest.testmod()
