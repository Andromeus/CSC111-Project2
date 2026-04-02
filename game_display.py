"""CSC111 Project 2 ALIGNQUATTRO

GAME DISPLAY FILE

This file is for running pygame and visualizing our project.
"""
import math
import sys

import pygame

import game_logic
import player_mcts

COLOR_DICTIONARY = {"white": (255, 255, 255), "blue": (0, 0, 255), "red": (255, 0, 0), "yellow": (255, 255, 0),
                    "biege": (255, 192, 103)}
GAME_STATES = {0: "menu", 1: "gameplay", 2: "data_visualization"}
RECTS = {"lower middle": pygame.Rect(540, 400, 200, 80), "lower middle 2": pygame.Rect(540, 500, 200, 80),
         "right": pygame.Rect(820, 400, 200, 80), "left": pygame.Rect(260, 400, 200, 80),
         "left difficulty": pygame.Rect(30, 400, 200, 80), "right difficulty": pygame.Rect(1050, 400, 200, 80),
         "left tree": pygame.Rect(30, 500, 200, 80), "right tree": pygame.Rect(1050, 500, 200, 80),
         "left heuristic": pygame.Rect(30, 600, 200, 80), "right heuristic": pygame.Rect(1050, 600, 200, 80)}


class AlignQuattroVisualization:
    """A class for representing an AlignQuattro game with pygame

    Instance Attributes:
        - screen: a pygame.Surface instance attribute through which the AlignQuattro game is visualized.
        - clock: a pygame.time.Clock instance attribute used for keeping track of time in pygame.
        - running: a boolean which controls the pygame game loop and keeps it running while true.
        - red: a players.Player or player_mcts.MCTSPlayer instance attribute representing the red player.
        - yellow: a players.Player or player_mcts.MCTSPlayer instance attribute representing the yellow player.
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

    def __init__(self, red_player: game_logic.Player | player_mcts.MCTSPlayer,
                 yellow_player: game_logic.Player | player_mcts.MCTSPlayer, g_state: int = 0) -> None:
        """Initialize AlignQuattroVisualization class.

        Preconditions:
            - isinstance(red, players.Player | player_mcts.MCTSPlayer)
            - isinstance(yellow, players.Player | player_mcts.MCTSPlayer)
        """
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()
        self.running = True
        self.red = red_player
        self.yellow = yellow_player
        self.game_state = g_state
        self.game = game_logic.AlignQuattroGame()

    def start_game(self) -> None:
        """Starts the game loop."""
        self.draw_menu()
        self.run_game_loop()

    def run_game_loop(self) -> None:
        """Runs the game loop to keep pygame up and running. Goes until the pygame window is closed."""
        current_player = self.red
        player_str = "red"
        player_1_choice = 1
        player_2_choice = 0
        red_dif = 0
        yel_dif = 0
        red_dag = True
        yel_dag = True
        red_heuristic = True
        yel_heuristic = True

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
                            self.change_player_types(True, player_1_choice, red_dif, red_dag, red_heuristic)
                        elif RECTS["right"].collidepoint(event.pos):
                            player_2_choice += 1
                            self.change_player_types(False, player_2_choice, yel_dif, yel_dag, yel_heuristic)
                        elif RECTS["left difficulty"].collidepoint(event.pos) and player_1_choice % 3 == 2:
                            red_dif += 1
                            red_dif %= 4
                            self.change_player_types(True, player_1_choice, red_dif, red_dag, red_heuristic)
                            self.type_customization_text(True, red_dif, red_dag, red_heuristic)
                        elif RECTS["left tree"].collidepoint(event.pos) and player_1_choice % 3 == 2:
                            red_dag = not red_dag
                            self.change_player_types(True, player_1_choice, red_dif, red_dag, red_heuristic)
                            self.type_customization_text(True, red_dif, red_dag, red_heuristic)
                        elif RECTS["left heuristic"].collidepoint(event.pos) and player_1_choice % 3 == 2:
                            red_heuristic = not red_heuristic
                            self.change_player_types(True, player_1_choice, red_dif, red_dag, red_heuristic)
                            self.type_customization_text(True, red_dif, red_dag, red_heuristic)
                        elif RECTS["right difficulty"].collidepoint(event.pos) and player_2_choice % 3 == 2:
                            yel_dif += 1
                            yel_dif %= 4
                            self.change_player_types(False, player_2_choice, yel_dif, yel_dag, yel_heuristic)
                            self.type_customization_text(False, yel_dif, yel_dag, yel_heuristic)
                        elif RECTS["right tree"].collidepoint(event.pos) and player_2_choice % 3 == 2:
                            yel_dag = not yel_dag
                            self.change_player_types(False, player_2_choice, yel_dif, yel_dag, yel_heuristic)
                            self.type_customization_text(False, yel_dif, yel_dag, yel_heuristic)
                        elif RECTS["right heuristic"].collidepoint(event.pos) and player_2_choice % 3 == 2:
                            yel_heuristic = not yel_heuristic
                            self.change_player_types(False, player_2_choice, yel_dif, yel_dag, yel_heuristic)
                            self.type_customization_text(False, yel_dif, yel_dag, yel_heuristic)
                    elif (GAME_STATES[self.game_state] == "gameplay"
                          and isinstance(current_player, game_logic.HumanPlayerPygame)
                          and self.game.get_outcome() == "in progress"):
                        x = event.pos[0]
                        c_input = math.floor((x - 32) / 175)
                        if c_input in self.game.get_available_columns():
                            current_player, player_str = self.make_move(
                                self.game, current_player, player_str, c_input)
                    elif GAME_STATES[self.game_state] == "gameplay" and self.game.outcome != "in progress":
                        self.game_state = 0  # return to menu when the game is finished
                        self.draw_menu(player_1_choice, player_2_choice, red_dif, yel_dif, red_dag,
                                       yel_dag, red_heuristic, yel_heuristic)
                    elif GAME_STATES[self.game_state] == "data_visualization":
                        self.game_state = 0  # return to menu when the game is finished
                        self.draw_menu(player_1_choice, player_2_choice, red_dif, yel_dif, red_dag,
                                       yel_dag, red_heuristic, yel_heuristic)

            if GAME_STATES[self.game_state] == "menu":
                upper_header = self.get_font(1).render("Welcome to ALIGNQUATTRO", True, COLOR_DICTIONARY["red"])
                upper_header_rect = upper_header.get_rect()
                upper_header_rect.center = (1280 // 2, 50)
                self.screen.blit(upper_header, upper_header_rect)
                # need something for buttons here to choose next action
            elif GAME_STATES[self.game_state] == "gameplay":
                if (not isinstance(current_player, game_logic.HumanPlayerPygame)
                        and self.game.get_outcome() == "in progress"):
                    col_input = current_player.make_move(self.game)
                    current_player, player_str = self.make_move(
                        self.game, current_player, player_str, col_input)
                    pygame.event.clear(pygame.MOUSEBUTTONDOWN)
                if self.game.get_outcome() != "in progress":
                    font = self.get_font(0)
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
        sys.exit()

    def draw_menu(self, c1: int = 1, c2: int = 0, red_dif: int = 0, yel_dif: int = 0, red_dag: bool = True,
                  yel_dag: bool = True, red_h: bool = True, yel_h: bool = True) -> None:
        """Draws the main menu for AlignQuattro, where c1 and c2 are the choices for players 1 and 2."""
        self.screen.fill(COLOR_DICTIONARY["biege"])
        middle_header = self.get_font(0).render("START", True, COLOR_DICTIONARY["yellow"], COLOR_DICTIONARY["red"])
        middle_header_rect = middle_header.get_rect()
        middle_header_rect.center = (1280 // 2, 440)

        lower_header = self.get_font(0).render("DATA", True, COLOR_DICTIONARY["yellow"], COLOR_DICTIONARY["red"])
        lower_header_rect = lower_header.get_rect()
        lower_header_rect.center = (1280 // 2, 540)

        player1_choice_header = self.get_font(0).render("Red Player", True, COLOR_DICTIONARY["red"])
        player1_choice_rect = player1_choice_header.get_rect()
        player1_choice_rect.center = (1280 // 2 - 280, 380)

        player2_choice_header = self.get_font(0).render("Yellow Player", True, COLOR_DICTIONARY["red"])
        player2_choice_rect = player2_choice_header.get_rect()
        player2_choice_rect.center = (1280 // 2 + 280, 380)

        pygame.draw.rect(self.screen, COLOR_DICTIONARY["red"], RECTS["lower middle"],
                         0, 10, 10, 10, 10)
        pygame.draw.rect(self.screen, COLOR_DICTIONARY['red'], RECTS["lower middle 2"],
                         0, 10, 10, 10, 10)
        pygame.draw.rect(self.screen, COLOR_DICTIONARY['red'], RECTS["left"],
                         0, 10, 10, 10, 10)
        pygame.draw.rect(self.screen, COLOR_DICTIONARY['red'], RECTS["right"],
                         0, 10, 10, 10, 10)
        self.change_player_types(True, c1, red_dif, red_dag, red_h)
        self.change_player_types(False, c2, yel_dif, yel_dag, yel_h)
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

    def change_player_types(self, is_left: bool, choice: int, difficulty: int, is_dag: bool, use_h: bool) -> None:
        """
        Displays which type each player is on their buttons and modifies each player to fit the types displayed.
        The type is changed when the button is clicked
        """
        player_dict = {0: "Random", 1: "Human", 2: "MCTS Agent"}
        num_options = len(player_dict)
        message = player_dict[choice % num_options]
        difficulty_dictionary = {0: 400, 1: 1600, 2: 10000, 3: 50000}

        if is_left:
            xpos = 1280 // 2 - 280
            side = "left"
        else:
            xpos = 1280 // 2 + 280
            side = "right"

        choice_header = self.get_font(0).render(message, True, COLOR_DICTIONARY["yellow"])
        choice_rect = choice_header.get_rect()
        choice_rect.center = (xpos, 440)

        pygame.draw.rect(self.screen, COLOR_DICTIONARY['red'], RECTS[side], 0, 10, 10, 10, 10)

        self.screen.blit(choice_header, choice_rect)

        if choice % num_options == 0:
            adjusted_player = game_logic.RandomPlayer()
            custom_color = COLOR_DICTIONARY['biege']
        elif choice % num_options == 1:
            adjusted_player = game_logic.HumanPlayerPygame()
            custom_color = COLOR_DICTIONARY['biege']
        else:
            adjusted_player = player_mcts.MCTSPlayer(difficulty_dictionary[difficulty], math.sqrt(2), is_dag, use_h)
            custom_color = COLOR_DICTIONARY['red']

        if is_left:
            for left_rect in ["left difficulty", "left tree", "left heuristic"]:
                pygame.draw.rect(self.screen, custom_color, RECTS[left_rect], 0, 10, 10, 10, 10)
            self.red = adjusted_player
        else:
            for right_rect in ["right difficulty", "right tree", "right heuristic"]:
                pygame.draw.rect(self.screen, custom_color, RECTS[right_rect], 0, 10, 10, 10, 10)
            self.yellow = adjusted_player

        if custom_color == COLOR_DICTIONARY['red']:
            self.type_customization_text(is_left, difficulty, is_dag, use_h)

    def type_customization_text(self, is_left: bool, diff: int, is_dag: bool, is_h: bool) -> None:
        """Updates left / right textboxes of the MCTS Agent customization buttons based on specifications

        is_left determines which side of the screen to update
        diff is an int mapping to a difficulty to update
        is_dag is a bool representing whether to display dag or tree
        is_h is a bool representing whether to display heuristic or no heuristic
        """
        if is_left:
            x_pos = 130
            for left_rect in ["left difficulty", "left tree", "left heuristic"]:
                pygame.draw.rect(self.screen, COLOR_DICTIONARY['red'], RECTS[left_rect], 0, 10, 10, 10, 10)
        else:
            x_pos = 1150
            for right_rect in ["right difficulty", "right tree", "right heuristic"]:
                pygame.draw.rect(self.screen, COLOR_DICTIONARY['red'], RECTS[right_rect], 0, 10, 10, 10, 10)
        diff_dict = {0: "Easy", 1: "Medium", 2: "Hard", 3: "Slooow"}
        dag_dict = {True: "DAG", False: "Tree"}
        heuristic_dict = {True: "Heuristic", False: "No Heuristic"}

        player1_choice_header = self.get_font(0).render("Red Player", True, COLOR_DICTIONARY["red"])
        player1_choice_rect = player1_choice_header.get_rect()
        player1_choice_rect.center = (1280 // 2 - 280, 380)

        diff_text = self.get_font(0).render(diff_dict[diff], True, COLOR_DICTIONARY["white"])
        diff_rect = diff_text.get_rect()
        diff_rect.center = (x_pos, 440)

        dag_text = self.get_font(0).render(dag_dict[is_dag], True, COLOR_DICTIONARY["white"])
        dag_rect = dag_text.get_rect()
        dag_rect.center = (x_pos, 540)

        h_text = self.get_font(0).render(heuristic_dict[is_h], True, COLOR_DICTIONARY["white"])
        h_rect = h_text.get_rect()
        h_rect.center = (x_pos, 640)

        self.screen.blit(diff_text, diff_rect)
        self.screen.blit(dag_text, dag_rect)
        self.screen.blit(h_text, h_rect)

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

        font = self.get_font(0)
        title_font = self.get_font(1)
        header = title_font.render("Data Visualizations", True, COLOR_DICTIONARY["blue"])
        text = font.render("Click anywhere to return to menu.", True, COLOR_DICTIONARY["blue"])

        header_rect = header.get_rect()
        header_rect.center = (350, 100)

        text_rect = text.get_rect()
        text_rect.center = (350, 150)

        vs_baseline = pygame.image.load('images/experiments_against_baseline.jpg')
        vs_baseline = pygame.transform.scale(vs_baseline, (600, 350))

        tree_vs_dag = pygame.image.load('images/experiments_tree_vs_dag.jpg')
        tree_vs_dag = pygame.transform.scale(tree_vs_dag, (600, 350))

        heuristics_vs_not = pygame.image.load('images/Heuristics_vs_Non_Heuristics_Win_Rate.jpg')
        heuristics_vs_not = pygame.transform.scale(heuristics_vs_not, (600, 350))

        self.screen.blit(vs_baseline, (680, 0))
        self.screen.blit(tree_vs_dag, (0, 350))
        self.screen.blit(heuristics_vs_not, (680, 350))

        self.screen.blit(header, header_rect)
        self.screen.blit(text, text_rect)

    def get_font(self, font_choice: int) -> pygame.font.Font:
        """Returns a font based on a dictionary mapping integers to fonts."""
        fonts = {0: pygame.font.Font('freesansbold.ttf', 32),
                 1: pygame.font.Font('freesansbold.ttf', 64)}
        return fonts[font_choice]


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['static_type_checker'],
        'extra-imports': ['math', 'pygame', 'game_logic', 'player_mcts']
    })

    red = game_logic.HumanPlayerPygame()
    yellow = game_logic.RandomPlayer()
    vis = AlignQuattroVisualization(red, yellow)
    vis.start_game()
