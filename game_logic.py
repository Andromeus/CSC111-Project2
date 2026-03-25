class Align_Quattro_game:
    """
    _game: a 2x2 array describing the state of each slot in the game
    _valid_moves: a dictionary mapping each column to the lowest empty slot in the column
    _is_red_move: bool for whether it is red player's turn or not
    """

    _board: list[list[_Piece]]
    _valid_moves: dict[int, int]
    _is_red_move: bool
    # _move count(optional)

    def __init__(self, board: list[list[[_Piece]]],
                 is_red_move: bool = True) -> None:
        self._board =

class _Piece:
    """
    _type: type of piece(red, yellow, empty)

    Preconditions:
    - _type in {'red', 'yellow', 'empty}
    """

    _type = str

    def __init__(self, type = 'empty') -> None:
        self._type = type
