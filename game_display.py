import game_logic
import pygame
pending_moves = []


def intialize_game():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()

    # draw empty board
    screen.fill("blue")
    circle_radius = 55
    White = (255, 255, 255)
    for row in range(6):
        center_y = (row + 1) * (10 + circle_radius) + circle_radius * row
        for column in range(7):
            center_x = (column + 1) * (65 + circle_radius) + circle_radius * column
            pygame.draw.circle(screen, White, (center_x, center_y), circle_radius)
    pygame.display.flip()

    return screen, clock, circle_radius


def update_game(row, col, color):
    pending_moves.append((row, col, color))


def draw_circle(screen, row: int, column: int, circle_radius: int, type: str):

    # making transparent background rectangle surface
    circle_surface = pygame.Surface((circle_radius * 2, circle_radius * 2), pygame.SRCALPHA)  #
    # pygame.SRCALPHA makes it transparent

    # drawing the circle on the background surface
    center_x = (column + 1) * (65 + 55) + 55 * column
    center_y = (row + 1) * (10 + 55) + 55 * row
    if type == "red":
        color = (255, 0, 0)
    else:
        color = (0, 255, 0)

    pygame.draw.circle(circle_surface, color, (center_x, center_y), circle_radius)

    # getting rectangle with circle to be replaced in it based on where move was made
    rect_left = 65 * (column + 1) + 110 * column
    rect_top = 10 * (row + 1) + 110 * row
    replaced_rect = circle_surface.get_rect(rect_left, rect_top, circle_radius * 2, circle_radius * 2)
    screen.blit(circle_surface, replaced_rect)


def game_loop(screen, clock):
    running = True
    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        while len(pending_moves) > 0:
            row, col, color = pending_moves.pop(0)
            draw_circle(screen, row, col, 55, color)

        pygame.display.flip()
        clock.tick(60)

        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60
    pygame.quit()


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['static_type_checker'],
    #     'extra-imports': []
    # })

