import pygame
import sys
import random

# Initialize Pygame
pygame.init()
   
# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
BLOCK_SIZE = 20
FPS = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Setup display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Snake Game')
clock = pygame.time.Clock()

# Font for score
font = pygame.font.SysFont('arial', 25)


def draw_block(color, position):
    rect = pygame.Rect((position[0], position[1]), (BLOCK_SIZE, BLOCK_SIZE))
    pygame.draw.rect(screen, color, rect)


def show_score(score):
    text = font.render(f'Score: {score}', True, WHITE)
    screen.blit(text, (10, 10))


def game_over_screen(score):
    over_font = pygame.font.SysFont('arial', 50)
    over_text = over_font.render('Game Over', True, RED)
    score_text = font.render(f'Final Score: {score}', True, WHITE)

    screen.fill(BLACK)
    screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2,
                             SCREEN_HEIGHT // 3))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2,
                              SCREEN_HEIGHT // 2))
    pygame.display.flip()
    pygame.time.delay(3000)
    pygame.quit()
    sys.exit()


def main():
    # Initial snake parameters
    snake = [(100, 100), (80, 100), (60, 100)]
    direction = 'RIGHT'
    change_to = direction

    # Initial food position
    food_pos = (random.randrange(1, SCREEN_WIDTH // BLOCK_SIZE) * BLOCK_SIZE,
                random.randrange(1, SCREEN_HEIGHT // BLOCK_SIZE) * BLOCK_SIZE)
    score = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != 'DOWN':
                    change_to = 'UP'
                elif event.key == pygame.K_DOWN and direction != 'UP':
                    change_to = 'DOWN'
                elif event.key == pygame.K_LEFT and direction != 'RIGHT':
                    change_to = 'LEFT'
                elif event.key == pygame.K_RIGHT and direction != 'LEFT':
                    change_to = 'RIGHT'

        direction = change_to

        # Move snake
        head_x, head_y = snake[0]
        if direction == 'UP':
            head_y -= BLOCK_SIZE
        elif direction == 'DOWN':
            head_y += BLOCK_SIZE
        elif direction == 'LEFT':
            head_x -= BLOCK_SIZE
        elif direction == 'RIGHT':
            head_x += BLOCK_SIZE

        new_head = (head_x, head_y)
        snake.insert(0, new_head)

        # Check if snake ate food
        if snake[0] == food_pos:
            score += 1
            food_pos = (random.randrange(1, SCREEN_WIDTH // BLOCK_SIZE) * BLOCK_SIZE,
                        random.randrange(1, SCREEN_HEIGHT // BLOCK_SIZE) * BLOCK_SIZE)
        else:
            snake.pop()

        # Check for collisions
        if (head_x < 0 or head_x >= SCREEN_WIDTH or
                head_y < 0 or head_y >= SCREEN_HEIGHT or
                new_head in snake[1:]):
            game_over_screen(score)

        # Draw everything
        screen.fill(BLACK)
        for block in snake:
            draw_block(GREEN, block)
        draw_block(RED, food_pos)
        show_score(score)

        pygame.display.update()
        clock.tick(FPS)


if __name__ == '__main__':
    main()
