"""CSC111 Project 2 ALIGNQUATTRO

GAME DISPLAY FILE

This file is for running pygame and visualizing our project.
"""
import math

import pygame
import game_logic
import player_mcts

COLOR_DICTIONARY = {"white": (255, 255, 255), "blue": (0, 0, 255), "red": (255, 0, 0), "yellow": (255, 255, 0),
                    "biege": (255, 192, 103)}
GAME_STATES = {0: "menu", 1: "gameplay", 2: "data_visualization"}
RECTS = {"lower middle": pygame.Rect(
    540, 400, 200, 80), "lower middle 2": pygame.Rect(540, 500, 200, 80),
    "right": pygame.Rect(770, 400, 400, 80), "left": pygame.Rect(110, 400, 400, 80)}


class AlignQuattroVisualization:
    """A class for representing an AlignQuattro game with pygame

    Instance Attributes:
        - screen: a pygame.Surface instance attribute through which the AlignQuattro game is visualized.
        - clock: a pygame.time.Clock instance attribute used for keeping track of time in pygame.
        - running: a boolean which controls the pygame game loop and keeps it running while true.
        - red: a players.Player or player_mcts.MCTSPlayer or player_mcts_2.MCTSPlayer instance attribute representing the red player.
        - yellow: a players.Player or player_mcts.MCTSPlayer or player_mcts_2.MCTSPlayer instance attribute representing the yellow player.
        - game_state: an int representing the current game_state, based on the GAME_STATES dictionary.

    Representation Invariants
        - -1 < self.game_state < len(GAME_STATES)
    """
    screen: pygame.Surface
    clock: pygame.time.Clock
    running: bool
    red: game_logic.Player | player_mcts.MCTSPlayer
    yellow: game_logic.Player | player_mcts.MCTSPlayer
    game_state: int
    game: game_logic.AlignQuattroGame
    fonts: dict[int, pygame.font]

    def __init__(self, red: game_logic.Player | player_mcts.MCTSPlayer,
                 yellow: game_logic.Player | player_mcts.MCTSPlayer, g_state: int = 0) -> None:
        """Initialize AlignQuattroVisualization class.

        Preconditions:
            - isinstance(red, players.Player | player_mcts.MCTSPlayer | player_mcts_2.MCTSPlayer)
            - isinstance(yellow, players.Player | player_mcts.MCTSPlayer | player_mcts_2.MCTSPlayer)
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
        """Starts the game loop and draws the starting menu."""
        self.draw_menu()
        self.run_game_loop()

    def run_game_loop(self) -> None:
        """Runs the game loop to keep pygame up and running. Goes until the pygame window is closed."""
        current_player = self.red
        player_str = "red"
        player_1_choice = 1
        player_2_choice = 0

        while self.running:
            # pygame.QUIT event means the user clicked X to close your window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    # game over screen
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if GAME_STATES[self.game_state] == "menu":
                        if RECTS["lower middle"].collidepoint(event.pos):
                            self.start_new_game()
                            current_player = self.red
                            player_str = "red"
                        elif RECTS["lower middle 2"].collidepoint(event.pos):
                            self.show_data()
                        elif RECTS["left"].collidepoint(event.pos):
                            player_1_choice += 1
                            self.change_player_types(player_1_choice, player_2_choice)
                        elif RECTS["right"].collidepoint(event.pos):
                            player_2_choice += 1
                            self.change_player_types(player_1_choice, player_2_choice)
                    elif (GAME_STATES[self.game_state] == "gameplay" and
                          isinstance(current_player, game_logic.HumanPlayerPygame) and
                          self.game.get_outcome() == "in progress"):
                        x = event.pos[0]
                        c_input = math.floor((x - 32) / 175)
                        if c_input in self.game.get_available_columns():
                            current_player, player_str = self.make_move(
                                self.game, current_player, player_str, c_input)
                    elif GAME_STATES[self.game_state] == "gameplay" and self.game.outcome != "in progress":
                        self.game_state = 0  # return to menu when the game is finished
                        self.draw_menu(player_1_choice, player_2_choice)
                    elif GAME_STATES[self.game_state] == "data_visualization":
                        self.game_state = 0  # return to menu when the game is finished
                        self.draw_menu(player_1_choice, player_2_choice)

            if GAME_STATES[self.game_state] == "menu":
                upper_header = self.fonts[1].render("Welcome to ALIGNQUATTRO",
                                                    True, COLOR_DICTIONARY["red"])
                upper_header_rect = upper_header.get_rect()
                upper_header_rect.center = (1280 // 2, 50)
                self.screen.blit(upper_header, upper_header_rect)
                # need something for buttons here to choose next action
            elif GAME_STATES[self.game_state] == "gameplay":
                if (not isinstance(current_player, game_logic.HumanPlayerPygame) and
                        self.game.get_outcome() == "in progress"):
                    col_input = current_player.make_move(self.game)
                    current_player, player_str = self.make_move(
                        self.game, current_player, player_str, col_input)
                    pygame.event.clear(pygame.MOUSEBUTTONDOWN)
                if self.game.get_outcome() != "in progress":
                    font = self.fonts[0]
                    text = font.render(f"{self.game.get_outcome()} Click anywhere to return to menu.", True,
                                       COLOR_DICTIONARY["red"], COLOR_DICTIONARY["yellow"])
                    text_rect = text.get_rect()
                    text_rect.center = (1280 // 2, 720 // 2)
                    self.screen.blit(text, text_rect)
            elif GAME_STATES[self.game_state] == "data_visualization":
                pass
            # Display plots and stuff here

            pygame.display.flip()
            self.clock.tick(60)  # limits FPS to 60
        pygame.quit()

    def draw_menu(self, c1: int = 1, c2: int = 0) -> None:
        """Draws the main menu for AlignQuattro, where c1 and c2 are the choices for players 1 and 2."""
        self.screen.fill(COLOR_DICTIONARY["biege"])
        middle_header = self.fonts[0].render("START", True,
                                             COLOR_DICTIONARY["yellow"], COLOR_DICTIONARY["red"])
        middle_header_rect = middle_header.get_rect()
        middle_header_rect.center = (1280 // 2, 440)

        lower_header = self.fonts[0].render("DATA", True,
                                            COLOR_DICTIONARY["yellow"], COLOR_DICTIONARY["red"])
        lower_header_rect = lower_header.get_rect()
        lower_header_rect.center = (1280 // 2, 540)

        player1_choice_header = self.fonts[0].render("Red Player", True, COLOR_DICTIONARY["red"])
        player1_choice_rect = player1_choice_header.get_rect()
        player1_choice_rect.center = (1280 // 2 - 330, 380)

        player2_choice_header = self.fonts[0].render("Yellow Player", True, COLOR_DICTIONARY["red"])
        player2_choice_rect = player2_choice_header.get_rect()
        player2_choice_rect.center = (1280 // 2 + 330, 380)

        pygame.draw.rect(self.screen, COLOR_DICTIONARY["red"], RECTS["lower middle"],
                         0, 10, 10, 10, 10)
        pygame.draw.rect(self.screen, COLOR_DICTIONARY['red'], RECTS["lower middle 2"],
                         0, 10, 10, 10, 10)
        pygame.draw.rect(self.screen, COLOR_DICTIONARY['red'], RECTS["left"],
                         0, 10, 10, 10, 10)
        pygame.draw.rect(self.screen, COLOR_DICTIONARY['red'], RECTS["right"],
                         0, 10, 10, 10, 10)
        self.change_player_types(c1, c2)
        self.screen.blit(middle_header, middle_header_rect)
        self.screen.blit(lower_header, lower_header_rect)
        self.screen.blit(player1_choice_header, player1_choice_rect)
        self.screen.blit(player2_choice_header, player2_choice_rect)

        for i in range(4):
            circle_radius = 80
            center_x = 340 + 200 * i
            center_y = 250
            pygame.draw.circle(
                self.screen, COLOR_DICTIONARY["red"], (center_x, center_y), circle_radius)

        pygame.display.flip()

    def change_player_types(self, choice1: int, choice2: int) -> None:
        """
        Displays which type each player is on their buttons and modifies each player to fit the types displayed.
        The type is changed when the button is clicked
        """
        player_dict = {0: "Random", 1: "Human", 2: "MCTS Easy", 3: "MCTS Medium", 4: "MCTS Hard", 5: "MCTS Slooow",
                       6: "MCTS Easy Heuristic", 7: "MCTS Medium Heuristic", 8: "MCTS Hard Heuristic",
                       9: "MCTS Slooow Heuristic",
                       10: "DAG Easy", 11: "DAG Medium", 12: "DAG Hard", 13: "DAG Slooow",
                       14: "DAG Easy Heuristic", 15: "DAG Medium Heuristic", 16: "DAG Hard Heuristic",
                       17: "DAG Slooow Heuristic"}

        m1 = player_dict[choice1 % 18]
        m2 = player_dict[choice2 % 18]

        player1_choice_header = self.fonts[0].render(m1, True,
                                                     COLOR_DICTIONARY["yellow"], COLOR_DICTIONARY["red"])
        player1_choice_rect = player1_choice_header.get_rect()
        player1_choice_rect.center = (1280 // 2 - 330, 440)

        player2_choice_header = self.fonts[0].render(m2, True,
                                                     COLOR_DICTIONARY["yellow"], COLOR_DICTIONARY["red"])
        player2_choice_rect = player2_choice_header.get_rect()
        player2_choice_rect.center = (1280 // 2 + 330, 440)
        pygame.draw.rect(self.screen, COLOR_DICTIONARY['red'], RECTS["left"],
                         0, 10, 10, 10, 10)
        pygame.draw.rect(self.screen, COLOR_DICTIONARY['red'], RECTS["right"],
                         0, 10, 10, 10, 10)
        self.screen.blit(player1_choice_header, player1_choice_rect)
        self.screen.blit(player2_choice_header, player2_choice_rect)
        self.change_role("red", choice1)
        self.change_role("yellow", choice2)

    def change_role(self, player: str, choice: int) -> None:
        """
        Changes the type based on player as well as the choice displayed on the button
        """

        if player == "red":
            if choice % 18 == 0:
                self.red = game_logic.RandomPlayer()
            elif choice % 18 == 1:

                self.red = game_logic.HumanPlayerPygame()
            elif choice % 18 == 2:

                self.red = player_mcts.MCTSPlayer(400, is_dag=False, use_heuristics=False)
            elif choice % 18 == 3:
                self.red = player_mcts.MCTSPlayer(is_dag=False, use_heuristics=False)
            elif choice % 18 == 4:
                self.red = player_mcts.MCTSPlayer(20000, is_dag=False, use_heuristics=False)
            elif choice % 18 == 5:
                self.red = player_mcts.MCTSPlayer(50000, is_dag=False, use_heuristics=False)

            elif choice % 18 == 6:
                self.red = player_mcts.MCTSPlayer(400, is_dag=False, use_heuristics=True)
            elif choice % 18 == 7:
                self.red = player_mcts.MCTSPlayer(is_dag=False, use_heuristics=True)
            elif choice % 18 == 8:
                self.red = player_mcts.MCTSPlayer(20000, is_dag=False, use_heuristics=True)
            elif choice % 18 == 9:
                self.red = player_mcts.MCTSPlayer(50000, is_dag=False, use_heuristics=True)

            elif choice % 18 == 10:
                self.red = player_mcts.MCTSPlayer(400, is_dag=True, use_heuristics=False)
            elif choice % 18 == 11:
                self.red = player_mcts.MCTSPlayer(is_dag=True, use_heuristics=False)
            elif choice % 18 == 12:
                self.red = player_mcts.MCTSPlayer(20000, is_dag=True, use_heuristics=False)
            elif choice % 18 == 13:
                self.red = player_mcts.MCTSPlayer(50000, is_dag=True, use_heuristics=False)

            elif choice % 18 == 14:
                self.red = player_mcts.MCTSPlayer(400, is_dag=True, use_heuristics=True)
            elif choice % 18 == 15:
                self.red = player_mcts.MCTSPlayer(is_dag=True, use_heuristics=True)
            elif choice % 18 == 16:
                self.red = player_mcts.MCTSPlayer(20000, is_dag=True, use_heuristics=True)
            elif choice % 18 == 17:
                self.red = player_mcts.MCTSPlayer(50000, is_dag=True, use_heuristics=True)
        else:
            if choice % 18 == 0:
                self.yellow = game_logic.RandomPlayer()
            elif choice % 18 == 1:

                self.yellow = game_logic.HumanPlayerPygame()
            elif choice % 18 == 2:

                self.yellow = player_mcts.MCTSPlayer(400, is_dag=False, use_heuristics=False)
            elif choice % 18 == 3:
                self.yellow = player_mcts.MCTSPlayer(is_dag=False, use_heuristics=False)
            elif choice % 18 == 4:
                self.yellow = player_mcts.MCTSPlayer(20000, is_dag=False, use_heuristics=False)
            elif choice % 18 == 5:
                self.yellow = player_mcts.MCTSPlayer(50000, is_dag=False, use_heuristics=False)

            elif choice % 18 == 6:
                self.yellow = player_mcts.MCTSPlayer(400, is_dag=False, use_heuristics=True)
            elif choice % 18 == 7:
                self.yellow = player_mcts.MCTSPlayer(is_dag=False, use_heuristics=True)
            elif choice % 18 == 8:
                self.yellow = player_mcts.MCTSPlayer(20000, is_dag=False, use_heuristics=True)
            elif choice % 18 == 9:
                self.yellow = player_mcts.MCTSPlayer(50000, is_dag=False, use_heuristics=True)

            elif choice % 18 == 10:
                self.yellow = player_mcts.MCTSPlayer(400, is_dag=True, use_heuristics=False)
            elif choice % 18 == 11:
                self.yellow = player_mcts.MCTSPlayer(is_dag=True, use_heuristics=False)
            elif choice % 18 == 12:
                self.yellow = player_mcts.MCTSPlayer(20000, is_dag=True, use_heuristics=False)
            elif choice % 18 == 13:
                self.yellow = player_mcts.MCTSPlayer(50000, is_dag=True, use_heuristics=False)

            elif choice % 18 == 14:
                self.yellow = player_mcts.MCTSPlayer(400, is_dag=True, use_heuristics=True)
            elif choice % 18 == 15:
                self.yellow = player_mcts.MCTSPlayer(is_dag=True, use_heuristics=True)
            elif choice % 18 == 16:
                self.yellow = player_mcts.MCTSPlayer(20000, is_dag=True, use_heuristics=True)
            elif choice % 18 == 17:
                self.yellow = player_mcts.MCTSPlayer(50000, is_dag=True, use_heuristics=True)

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
                center_x = (column + 1) * (65 + circle_radius) + \
                    circle_radius * column
                pygame.draw.circle(
                    self.screen, COLOR_DICTIONARY["white"], (center_x, center_y), circle_radius)
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
        pygame.draw.circle(self.screen, color,
                           (center_x, center_y), circle_radius)
        pygame.display.flip()

    def make_move(self, game: game_logic.AlignQuattroGame,
                  current_player: game_logic.Player | player_mcts.MCTSPlayer,
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

    def show_data(self) -> None:
        """Display Data and switch to the data screen."""
        self.game_state = 2

        self.screen.fill(COLOR_DICTIONARY["white"])

        font = self.fonts[0]
        text = font.render("Click anywhere to return to menu.", True,
                           COLOR_DICTIONARY["blue"])
        text_rect = text.get_rect()
        text_rect.center = (1280 // 2, 720 // 2)
        self.screen.blit(text, text_rect)

        # display graphs etc here


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['static_type_checker'],
    #     'extra-imports': ['math', 'pygame', 'game_logic']
    # })

    red = game_logic.HumanPlayerPygame()
    yellow = game_logic.RandomPlayer()
    vis = AlignQuattroVisualization(red, yellow)
    vis.start_game()
