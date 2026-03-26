import random
import game_logic


class Player:
    """ An abstract class representing a Align_Quattro Player.

    This class can be subclassed to implement different strategies for playing chess as well as whether the input
    is player based or AI based.
    """

    def make_move(self, game: game_logic.AlignQuattroGame) -> int:
        """Make a move given the current game.

        Preconditions:
            - the move is a number between 0 and 6
        """
        raise NotImplementedError


class RandomPlayer(Player):
    """A Align_Quattro AI whose strategy is always picking a random move."""

    def make_move(self, game: game_logic.AlignQuattroGame) -> int:
        """Make a move given the current game.

        Preconditions:
            - the move is a number between 0 and 6
        """
        random_move = random.randint(0, 6)
        return random_move

