"""CSC111 Project 2 ALIGNQUATTRO

GAME DISPLAY FILE

This file is for running pygame and visualizing our project.
"""
import math

import pygame
import game_logic
import players
import player_mcts
import player_mcts_2

COLOR_DICTIONARY = {"white": (255, 255, 255), "blue": (0, 0, 255), "red": (255, 0, 0), "yellow": (255, 255, 0)}
GAME_STATES = {0: "menu", 1: "gameplay", 2: "data_visualization"}


class AlignQuattroVisualization:
    """A class for representing an AlignQuattro game with pygame

    Instance Attributes:
        - screen: a pygame.Surface instance attribute through which the AlignQuattro game is visualized.
        - clock: a pygame.time.Clock instance attribute used for keeping track of time in pygame.
        - running: a boolean which controls the pygame game loop and keeps it running while true.
        - red: a game_logic.Player instance attribute representing the red player.
        - yellow: a game_logic.Player instance attribute representing the yellow player.
        - game_state: an int representing the current game_state, based on the GAME_STATES dictionary.

    Representation Invariants
        - -1 < self.game_state < len(GAME_STATES)
    """
    screen: pygame.Surface
    clock: pygame.time.Clock
    running: bool
    red: game_logic.Player
    yellow: game_logic.Player
    game_state: int
    game: game_logic.AlignQuattroGame
    fonts: dict[int, pygame.font]

    def __init__(self, red: players.Player | player_mcts.MCTSPlayer | player_mcts_2.MCTSPlayer,
                 yellow: players.Player | player_mcts.MCTSPlayer | player_mcts_2.MCTSPlayer, g_state: int = 0) -> None:
        """Initialize AlignQuattroVisualization class.

        Preconditions:
            - isinstance(red, game_logic.Player)
            - isinstance(yellow, game_logic.Player)
        """
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()
        self.running = True
        self.red = red
        self.yellow = yellow
        self.game_state = g_state
        self.game = game_logic.AlignQuattroGame()
        self.fonts = {0: pygame.font.Font('freesansbold.ttf', 32),
                      1: pygame.font.Font('freesansbold.ttf', 64)}

    def start_game(self):
        self.draw_menu()
        self.run_game_loop()

    def run_game_loop(self) -> None:
        """Runs the game loop to keep pygame up and running. Goes until the pygame window is closed."""
        current_player = self.red
        player_str = "red"
        game_ongoing = True

        while self.running:
            # pygame.QUIT event means the user clicked X to close your window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    # game over screen
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if GAME_STATES[self.game_state] == "menu":
                        self.start_new_game()  # needs to only be when mouse position is in a certain region
                    elif (GAME_STATES[self.game_state] == "gameplay" and
                          isinstance(current_player, game_logic.HumanPlayerPygame) and
                          self.game.get_outcome() == "in progress"):
                        x = event.pos[0]
                        c_input = math.floor((x - 32) / 175)
                        if c_input in self.game.get_available_columns():
                            current_player, player_str = self.make_move(self.game, current_player, player_str, c_input)
                    elif GAME_STATES[self.game_state] == "gameplay" and self.game.outcome != "in progress":
                        self.game_state = 0  # return to menu when the game is finished
                        self.draw_menu()
                    elif GAME_STATES[self.game_state] == "data_visualization":
                        pass
                        # some sort of button to return to menu here

            if GAME_STATES[self.game_state] == "menu":
                upper_header = self.fonts[0].render("Welcome to ALIGNQUATTRO", True,
                                               COLOR_DICTIONARY["red"], COLOR_DICTIONARY["yellow"])
                upper_header_rect = upper_header.get_rect()
                upper_header_rect.center = (1280 // 2, 50)
                self.screen.blit(upper_header, upper_header_rect)
                # need something for buttons here to choose next action
            elif GAME_STATES[self.game_state] == "gameplay":
                if not isinstance(current_player, game_logic.HumanPlayerPygame):
                    col_input = current_player.make_move(self.game)
                    current_player, player_str = self.make_move(self.game, current_player, player_str, col_input)
                    pygame.event.clear(pygame.MOUSEBUTTONDOWN)
                if self.game.get_outcome() != "in progress":
                    font = self.fonts[0]
                    text = font.render(f"{self.game.get_outcome()} Click anywhere to return to menu.", True,
                                       COLOR_DICTIONARY["red"], COLOR_DICTIONARY["yellow"])
                    text_rect = text.get_rect()
                    text_rect.center = (1280 // 2, 720 // 2)
                    self.screen.blit(text, text_rect)
                    game_ongoing = False
                else:
                    game_ongoing = True
            elif GAME_STATES[self.game_state] == "data_visualization":
                pass
            # Display plots and stuff here

            pygame.display.flip()
            self.clock.tick(60)  # limits FPS to 60
        pygame.quit()

    def draw_menu(self) -> None:
        """Draws the main menu for AlignQuattro"""
        self.screen.fill(COLOR_DICTIONARY["white"])
        middle_header = self.fonts[0].render("Click anywhere to start", True,
                                             COLOR_DICTIONARY["red"], COLOR_DICTIONARY["yellow"])
        middle_header_rect = middle_header.get_rect()
        middle_header_rect.center = (1280 // 2, 720 // 2)
        self.screen.blit(middle_header, middle_header_rect)

    def start_new_game(self) -> None:
        """Starts a new game with the given red and yellow players, by creating a new game and switching game state."""
        self.game = game_logic.AlignQuattroGame()
        self.game_state = 1
        self.draw_board()

    def draw_board(self) -> None:
        """Draws an empty board"""
        self.screen.fill(COLOR_DICTIONARY["blue"])
        circle_radius = 55
        for row in range(6):
            center_y = (row + 1) * (10 + circle_radius) + circle_radius * row
            pygame.draw.line(self.screen, COLOR_DICTIONARY["white"], (32 + 175 * (row + 1), 0),
                             (32 + 175 * (row + 1), 1280), 3)
            for column in range(7):
                center_x = (column + 1) * (65 + circle_radius) + circle_radius * column
                pygame.draw.circle(self.screen, COLOR_DICTIONARY["white"], (center_x, center_y), circle_radius)
        pygame.display.flip()

    def draw_circle(self, row: int, col: int, is_red: bool) -> None:
        """Draws a circle as the specified coordinates, where 0,0 is the top left and 5,6 is the bottom right.

        Preconditions:
            - 0 <= row <= 5
            - 0 <= col <= 6
        """
        if is_red:
            color = COLOR_DICTIONARY["red"]
        else:
            color = COLOR_DICTIONARY["yellow"]
        circle_radius = 55
        center_y = (row + 1) * (10 + circle_radius) + circle_radius * row
        center_x = (col + 1) * (65 + circle_radius) + circle_radius * col
        pygame.draw.circle(self.screen, color, (center_x, center_y), circle_radius)
        pygame.display.flip()

    def make_move(self, game: game_logic.AlignQuattroGame, current_player: game_logic.Player,
                  player_str: str, col_input: int) -> tuple:
        """Makes a move in the provided game and adjusts current player and player string accordingly.

        Preconditions:
            - -1 < col_input < 7
        """
        row_input = game.get_row_from_available_columns(col_input)
        game.make_move(col_input)
        self.draw_circle(row_input, col_input, player_str == "red")
        if current_player is self.red:
            current_player = self.yellow
            player_str = "yellow"
        else:
            current_player = self.red
            player_str = "red"
        return current_player, player_str


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['static_type_checker'],
        'extra-imports': ['math', 'pygame', 'game_logic']
    })
