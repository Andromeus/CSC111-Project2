import random
import game_logic
import player_mcts
import player_mcts_2


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


class HumanPlayer(Player):
    """An AlignQuattro player which take real human input to make human decided moves each turn."""

    def make_move(self, game: game_logic.AlignQuattroGame) -> int:
        """Waits for human player to type a number 1 - 7 to select a column."""
        choice = input("Choose a column, 1-7: ")
        options = {str(x + 1) for x in game.get_available_columns()}
        while choice not in options:
            print("That was an invalid option; try again.")
            choice = input("\nChoose a column, 1-7: ")
        return int(choice) - 1


class HumanPlayerPygame(Player):
    """An AlignQuattro player which takes real human input to make human decided moves each turn.

    Uses pygame mouse input to make moves based on the column clicked.
    """
    def make_move(self, game: game_logic.AlignQuattroGame) -> int:
        """Allow the pygame game loop to make moves instead of making a move directly."""
        pass
