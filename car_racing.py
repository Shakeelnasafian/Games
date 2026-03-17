import pygame
import random
import sys

# Initialize
pygame.init()

# Screen
WIDTH, HEIGHT = 500, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Racing")

# Colors
BLACK      = (0, 0, 0)
WHITE      = (255, 255, 255)
GRAY       = (50, 50, 50)
DARK_GRAY  = (80, 80, 80)
YELLOW     = (255, 220, 0)
RED        = (220, 30, 30)
BLUE       = (30, 100, 220)
GREEN      = (30, 200, 80)
ORANGE     = (230, 120, 30)

# Road boundaries
ROAD_LEFT  = 100
ROAD_RIGHT = 400
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT

# Lane centers (3 lanes)
LANES = [
    ROAD_LEFT + ROAD_WIDTH // 6,
    ROAD_LEFT + ROAD_WIDTH // 2,
    ROAD_LEFT + 5 * ROAD_WIDTH // 6,
]

PLAYER_WIDTH  = 40
PLAYER_HEIGHT = 70
ENEMY_WIDTH   = 40
ENEMY_HEIGHT  = 70

ENEMY_COLORS = [RED, ORANGE, GREEN, BLUE]

clock = pygame.time.Clock()
font_large = pygame.font.SysFont("Arial", 48, bold=True)
font_med   = pygame.font.SysFont("Arial", 28)
font_small = pygame.font.SysFont("Arial", 22)


def draw_road(dash_offset):
    """Draw road surface, edges, and dashed lane dividers."""
    # Road surface
    pygame.draw.rect(screen, DARK_GRAY, (ROAD_LEFT, 0, ROAD_WIDTH, HEIGHT))

    # Road edges (solid white lines)
    pygame.draw.line(screen, WHITE, (ROAD_LEFT, 0), (ROAD_LEFT, HEIGHT), 4)
    pygame.draw.line(screen, WHITE, (ROAD_RIGHT, 0), (ROAD_RIGHT, HEIGHT), 4)

    # Dashed lane dividers
    dash_h, gap_h = 40, 30
    for x in [ROAD_LEFT + ROAD_WIDTH // 3, ROAD_LEFT + 2 * ROAD_WIDTH // 3]:
        y = int(-dash_h + dash_offset % (dash_h + gap_h))
        while y < HEIGHT:
            pygame.draw.rect(screen, YELLOW, (x - 2, y, 4, dash_h))
            y += dash_h + gap_h


def draw_car(surface, x, y, w, h, color, is_player=False):
    """Draw a simple top-down car."""
    cx = x - w // 2

    # Car body
    pygame.draw.rect(surface, color, (cx, y, w, h), border_radius=8)

    # Windshields
    windshield_color = (180, 230, 255)
    pygame.draw.rect(surface, windshield_color, (cx + 6, y + 8, w - 12, 16), border_radius=4)
    pygame.draw.rect(surface, windshield_color, (cx + 6, y + h - 24, w - 12, 16), border_radius=4)

    # Wheels
    wheel_color = (20, 20, 20)
    for wx, wy in [(cx - 6, y + 8), (cx + w + 2, y + 8),
                   (cx - 6, y + h - 24), (cx + w + 2, y + h - 24)]:
        pygame.draw.rect(surface, wheel_color, (wx, wy, 8, 18), border_radius=3)

    # Headlights / taillights
    light_color = (255, 255, 180) if is_player else (255, 80, 80)
    pygame.draw.rect(surface, light_color, (cx + 4, y + h - 6, 10, 5), border_radius=2)
    pygame.draw.rect(surface, light_color, (cx + w - 14, y + h - 6, 10, 5), border_radius=2)


class Player:
    def __init__(self):
        self.lane = 1  # 0, 1, 2
        self.x = float(LANES[self.lane])
        self.y = HEIGHT - PLAYER_HEIGHT - 20
        self.target_x = self.x
        self.speed = 10  # pixels per frame for lane transition

    def move(self, direction):
        new_lane = self.lane + direction
        if 0 <= new_lane <= 2:
            self.lane = new_lane
            self.target_x = float(LANES[self.lane])

    def update(self):
        if self.x < self.target_x:
            self.x = min(self.x + self.speed, self.target_x)
        elif self.x > self.target_x:
            self.x = max(self.x - self.speed, self.target_x)

    def get_rect(self):
        return pygame.Rect(
            self.x - PLAYER_WIDTH // 2,
            self.y,
            PLAYER_WIDTH,
            PLAYER_HEIGHT,
        )

    def draw(self):
        draw_car(screen, int(self.x), self.y, PLAYER_WIDTH, PLAYER_HEIGHT, BLUE, is_player=True)


class Enemy:
    def __init__(self, speed):
        self.lane = random.randint(0, 2)
        self.x = float(LANES[self.lane])
        self.y = float(-ENEMY_HEIGHT)
        self.speed = speed
        self.color = random.choice(ENEMY_COLORS)

    def update(self):
        self.y += self.speed

    def get_rect(self):
        return pygame.Rect(
            self.x - ENEMY_WIDTH // 2,
            int(self.y),
            ENEMY_WIDTH,
            ENEMY_HEIGHT,
        )

    def draw(self):
        draw_car(screen, int(self.x), int(self.y), ENEMY_WIDTH, ENEMY_HEIGHT, self.color)

    def off_screen(self):
        return self.y > HEIGHT


def show_text_centered(text, font, color, y):
    surf = font.render(text, True, color)
    screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y))


def game_over_screen(score):
    screen.fill(BLACK)
    show_text_centered("GAME OVER", font_large, RED, HEIGHT // 2 - 80)
    show_text_centered(f"Score: {score}", font_med, WHITE, HEIGHT // 2)
    show_text_centered("Press R to Restart  |  Q to Quit", font_small, GRAY, HEIGHT // 2 + 60)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()


def main():
    while True:
        # --- Game state ---
        player       = Player()
        enemies      = []
        score        = 0
        base_speed   = 5.0
        enemy_speed  = base_speed
        spawn_timer  = 0
        spawn_interval = 60   # frames between spawns
        dash_offset  = 0.0

        running = True
        while running:
            clock.tick(60)

            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        player.move(-1)
                    if event.key in (pygame.K_RIGHT, pygame.K_d):
                        player.move(1)

            # Update
            player.update()

            score += 1
            # Increase difficulty every 300 points
            level = score // 300
            enemy_speed  = base_speed + level * 0.8
            spawn_interval = max(25, 60 - level * 5)

            dash_offset += enemy_speed

            spawn_timer += 1
            if spawn_timer >= spawn_interval:
                spawn_timer = 0
                enemies.append(Enemy(enemy_speed))

            for e in enemies:
                e.update()
            enemies = [e for e in enemies if not e.off_screen()]

            # Collision
            player_rect = player.get_rect()
            for e in enemies:
                if player_rect.colliderect(e.get_rect()):
                    running = False
                    break

            # Draw
            screen.fill(GRAY)
            draw_road(dash_offset)

            for e in enemies:
                e.draw()
            player.draw()

            # HUD
            score_surf = font_med.render(f"Score: {score}", True, WHITE)
            screen.blit(score_surf, (10, 10))
            level_surf = font_small.render(f"Level: {level + 1}", True, WHITE)
            screen.blit(level_surf, (10, 45))
            ctrl_surf = font_small.render("← → to steer", True, (160, 160, 160))
            screen.blit(ctrl_surf, (WIDTH - ctrl_surf.get_width() - 10, 10))

            pygame.display.flip()

        # Game over
        restart = game_over_screen(score)
        if not restart:
            break


if __name__ == "__main__":
    main()
