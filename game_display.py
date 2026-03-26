"""CSC111 Project 2 ALIGNQUATTRO

GAME DISPLAY FILE

This file is for running pygame and visualizing our project.
"""

import game_logic
import pygame


class AlignQuattroVisualization:
    """A class for representing an AlignQuattro game with pygame

    Instance Attributes:
        - screen
        - clock
        - running

    Representation Invariants:
        -
    """
    screen: pygame.display
    clock: pygame.time.Clock()
    running: bool

    def __init__(self) -> None:
        """Initialize AlignQuattroVisualization class."""
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()
        self.running = True
        self.draw_board()
        # self.run_game()  # This breaks the other loop, but not having it breaks pygame...?

    def draw_board(self) -> None:
        """Draws an empty board"""
        self.screen.fill("blue")
        circle_radius = 55
        white = (255, 255, 255)
        for row in range(6):
            center_y = (row + 1) * (10 + circle_radius) + circle_radius * row
            for column in range(7):
                center_x = (column + 1) * (65 + circle_radius) + circle_radius * column
                pygame.draw.circle(self.screen, white, (center_x, center_y), circle_radius)
        pygame.display.flip()

    def draw_circle(self, row: int, col: int, is_red: bool) -> None:
        """Draws a circle as the specified coordinates, where 0,0 is the top left and 5,6 is the bottom right.

        Preconditions:
            - 0 <= row <= 5
            - 0 <= col <= 6
        """
        if is_red:
            color = (255, 0, 0)
        else:
            color = (255, 255, 0)
        circle_radius = 55
        center_y = (row + 1) * (10 + circle_radius) + circle_radius * row
        center_x = (col + 1) * (65 + circle_radius) + circle_radius * col
        pygame.draw.circle(self.screen, color, (center_x, center_y), circle_radius)
        pygame.display.flip()

    def run_game(self) -> None:
        """Runs the pygame while loop to run the game"""
        while self.running:
            # poll for events
            # pygame.QUIT event means the user clicked X to close your window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # assuming move is a position in the board(row, column) as well as a color
            # get move in some way
            # move = row, column, color in some way

            # draw a new circle representing moved piece over the old circle representing empty piece

            # making transparent background rectangle surface
            # circle_surface = pygame.Surface((circle_radius * 2, circle_radius * 2), pygame.SRCALPHA) #
            # pygame.SRCALPHA makes it transparent

            # drawing the circle on the background surface
            # center_x = (column + 1) * (65 + 55) + 55 * column
            # center_y = (row + 1) * (10 + 55) + 55 * row
            # pygame.draw.circle(circle_surface, color, (center_x, center_y), circle_radius)

            # getting rectangle with circle to be replaced in it based on where move was made
            # rect_left = 65 * (column + 1) + 110 * column
            # rect_top = 10 * (row + 1) + 110 * row
            # replaced_rect = circle_surface.get_rect(rect_left, rect_top, circle_radius * 2, circle_radius * 2)
            # screen.blit(circle_surface, replaced_rect)

            # flip() the display to put your work on screen
            pygame.display.flip()

            self.clock.tick(60)  # limits FPS to 60

        pygame.quit()


# pygame.init()
# screen = pygame.display.set_mode((1280, 720))
# clock = pygame.time.Clock()
# running = True
#
# # draw empty board
# screen.fill("blue")
# circle_radius = 55
# White = (255, 255, 255)
# for row in range(6):
#     center_y = (row + 1) * (10 + circle_radius) + circle_radius * row
#     for column in range(7):
#         center_x = (column + 1) * (65 + circle_radius) + circle_radius * column
#         pygame.draw.circle(screen, White, (center_x, center_y), circle_radius)
# pygame.display.flip()

# while running:
#     # poll for events
#     # pygame.QUIT event means the user clicked X to close your window
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#
#     # assuming move is a position in the board(row, column) as well as a color
#     # get move in some way
#     # move = row, column, color in some way
#
#     # draw a new circle representing moved piece over the old circle representing empty piece
#
#     # making transparent background rectangle surface
#     circle_surface = pygame.Surface((circle_radius * 2, circle_radius * 2), pygame.SRCALPHA) #
#     # pygame.SRCALPHA makes it transparent
#
#     # drawing the circle on the background surface
#     # center_x = (column + 1) * (65 + 55) + 55 * column
#     # center_y = (row + 1) * (10 + 55) + 55 * row
#     # pygame.draw.circle(circle_surface, color, (center_x, center_y), circle_radius)
#
#     # getting rectangle with circle to be replaced in it based on where move was made
#     # rect_left = 65 * (column + 1) + 110 * column
#     # rect_top = 10 * (row + 1) + 110 * row
#     # replaced_rect = circle_surface.get_rect(rect_left, rect_top, circle_radius * 2, circle_radius * 2)
#     # screen.blit(circle_surface, replaced_rect)
#
#     # flip() the display to put your work on screen
#     pygame.display.flip()
#
#     clock.tick(60)  # limits FPS to 60
#
# pygame.quit()

if __name__ == '__main__':
    import doctest
    doctest.testmod()

    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['static_type_checker'],
    #     'extra-imports': []
    # })



