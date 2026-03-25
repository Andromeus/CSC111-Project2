
import game_logic
import pygame

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

# draw empty board
screen.fill("blue")
circle_radius = 55
White = (255, 255, 255, 255)
for row in range(6):
    center_y = (row + 1) * (10 + 55) + 55 * row
    for column in range(7):
        center_x = (column + 1) * (65 + 55) + 55 * column
        pygame.draw.circle(screen, White, (center_x, center_y), circle_radius)
pygame.display.flip()

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # wipe the spot of the move with a color to wipe it away from last frame


    # RENDER YOUR GAME HERE

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
