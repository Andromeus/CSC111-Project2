
import game_logic
import pygame

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

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

while running:
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
    circle_surface = pygame.Surface((circle_radius * 2, circle_radius * 2), pygame.SRCALPHA) #
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

    clock.tick(60)  # limits FPS to 60

pygame.quit()
