import pygame
import sys
import random
import math

pygame.init()

WIDTH, HEIGHT = 600, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fruit Cut")

FPS = 60
clock = pygame.time.Clock()

WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
RED    = (220, 30,  30)
YELLOW = (255, 220, 0)
ORANGE = (255, 140, 0)

FRUIT_TYPES = [
    ("watermelon", (50, 180, 50),  (220, 50,  50),  35),
    ("apple",      (220, 30,  30), (255, 200, 150), 28),
    ("orange",     (255, 140, 0),  (255, 210, 120), 30),
    ("lemon",      (255, 230, 0),  (255, 245, 160), 25),
    ("plum",       (140, 40,  200),(220, 150, 220), 24),
]


# ─── helpers ──────────────────────────────────────────────────────────────────

def point_segment_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def draw_half_circle(surface, color, inner_color, cx, cy, radius, left, alpha):
    size = radius * 2 + 4
    buf = pygame.Surface((size, size), pygame.SRCALPHA)
    c = (radius + 2, radius + 2)
    pygame.draw.circle(buf, (*color, alpha), c, radius)
    # paint the flat cut face
    if left:
        pygame.draw.rect(buf, (*inner_color, alpha), (c[0], 0, radius + 2, size))
    else:
        pygame.draw.rect(buf, (*inner_color, alpha), (0, 0, c[0], size))
    # re-clip to circle edge
    mask = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(mask, (0, 0, 0, 255), c, radius)
    buf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surface.blit(buf, (cx - radius - 2, cy - radius - 2))


# ─── game objects ─────────────────────────────────────────────────────────────

class Fruit:
    def __init__(self):
        name, color, inner_color, radius = random.choice(FRUIT_TYPES)
        self.color       = color
        self.inner_color = inner_color
        self.radius      = radius
        self.x    = random.randint(radius + 60, WIDTH - radius - 60)
        self.y    = HEIGHT + radius
        self.vx   = random.uniform(-2.5, 2.5)
        self.vy   = random.uniform(-17, -13)
        self.angle    = 0.0
        self.rot_spd  = random.uniform(-4, 4)

    def update(self):
        self.vy    += 0.38
        self.x     += self.vx
        self.y     += self.vy
        self.angle += self.rot_spd

    def draw(self, surface):
        buf = pygame.Surface((self.radius * 2 + 4, self.radius * 2 + 4), pygame.SRCALPHA)
        c = (self.radius + 2, self.radius + 2)
        pygame.draw.circle(buf, self.color, c, self.radius)
        # shine
        pygame.draw.circle(buf, (255, 255, 255, 160),
                           (c[0] - self.radius // 3, c[1] - self.radius // 3),
                           self.radius // 4)
        rotated = pygame.transform.rotate(buf, self.angle)
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated, rect)

    def off_screen(self):
        return self.y > HEIGHT + self.radius + 10

    def hit_by(self, x1, y1, x2, y2):
        return point_segment_dist(self.x, self.y, x1, y1, x2, y2) <= self.radius


class Half:
    """One half of a sliced fruit."""
    def __init__(self, x, y, vx, vy, color, inner_color, radius, left):
        self.x, self.y = x, y
        self.vx = vx + (random.uniform(-4, -1) if left else random.uniform(1, 4))
        self.vy = vy + random.uniform(-3, -0.5)
        self.color       = color
        self.inner_color = inner_color
        self.radius      = radius
        self.left        = left
        self.alpha       = 255
        self.angle       = 0.0
        self.rot_spd     = random.uniform(-6, 6)

    def update(self):
        self.vy    += 0.38
        self.x     += self.vx
        self.y     += self.vy
        self.angle += self.rot_spd
        self.alpha  = max(0, self.alpha - 4)

    def draw(self, surface):
        if self.alpha <= 0:
            return
        draw_half_circle(surface, self.color, self.inner_color,
                         int(self.x), int(self.y), self.radius, self.left, self.alpha)

    def done(self):
        return self.alpha <= 0 or self.y > HEIGHT + 60


class Bomb:
    def __init__(self):
        self.x    = random.randint(60, WIDTH - 60)
        self.y    = HEIGHT + 30
        self.vx   = random.uniform(-2, 2)
        self.vy   = random.uniform(-15, -12)
        self.radius = 26
        self.angle  = 0.0
        self.rot_spd = random.uniform(-3, 3)

    def update(self):
        self.vy    += 0.38
        self.x     += self.vx
        self.y     += self.vy
        self.angle += self.rot_spd

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        pygame.draw.circle(surface, (35, 35, 35), (cx, cy), self.radius)
        pygame.draw.circle(surface, (80, 80, 80), (cx, cy), self.radius, 3)
        # fuse
        fuse_end = (cx + self.radius // 2 + 5, cy - self.radius - 14)
        pygame.draw.line(surface, (160, 110, 50),
                         (cx + self.radius // 2, cy - self.radius),
                         fuse_end, 2)
        pygame.draw.circle(surface, YELLOW, fuse_end, 5)

    def off_screen(self):
        return self.y > HEIGHT + self.radius + 10

    def hit_by(self, x1, y1, x2, y2):
        return point_segment_dist(self.x, self.y, x1, y1, x2, y2) <= self.radius


class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = float(x), float(y)
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        spd   = random.uniform(2, 9)
        self.vx, self.vy = math.cos(angle) * spd, math.sin(angle) * spd
        self.alpha  = 255
        self.radius = random.randint(3, 7)

    def update(self):
        self.vy    += 0.25
        self.x     += self.vx
        self.y     += self.vy
        self.alpha  = max(0, self.alpha - 10)

    def draw(self, surface):
        if self.alpha <= 0:
            return
        buf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(buf, (*self.color, self.alpha),
                           (self.radius, self.radius), self.radius)
        surface.blit(buf, (int(self.x) - self.radius, int(self.y) - self.radius))

    def done(self):
        return self.alpha <= 0


class Blade:
    MAX = 18

    def __init__(self):
        self.pts = []      # list of (x, y, alpha)

    def add(self, x, y):
        self.pts.append([x, y, 255])
        if len(self.pts) > self.MAX:
            self.pts.pop(0)

    def update(self):
        self.pts = [[x, y, max(0, a - 18)] for x, y, a in self.pts]

    def draw(self, surface):
        for i in range(1, len(self.pts)):
            x1, y1, _ = self.pts[i - 1]
            x2, y2, a  = self.pts[i]
            if a > 0:
                w = max(1, int(5 * a / 255))
                pygame.draw.line(surface, (255, 255, int(180 * a / 255)),
                                 (x1, y1), (x2, y2), w)

    def last_segment(self):
        if len(self.pts) >= 2:
            return self.pts[-2][:2], self.pts[-1][:2]
        return None, None

    def clear(self):
        self.pts.clear()


# ─── background ───────────────────────────────────────────────────────────────

def draw_bg(surface):
    surface.fill((18, 18, 36))
    for y in range(0, HEIGHT, 55):
        pygame.draw.rect(surface, (28, 55, 28), (0,        y, 14, 45), border_radius=4)
        pygame.draw.rect(surface, (28, 55, 28), (WIDTH-14, y, 14, 45), border_radius=4)


# ─── main loop ────────────────────────────────────────────────────────────────

def main():
    fruits:    list[Fruit]    = []
    halves:    list[Half]     = []
    bombs:     list[Bomb]     = []
    particles: list[Particle] = []
    blade = Blade()

    score = 0
    lives = 3
    slicing = False

    spawn_timer    = 0
    spawn_interval = 85     # decreases over time (harder)

    font_lg = pygame.font.SysFont(None, 62)
    font_md = pygame.font.SysFont(None, 36)
    font_sm = pygame.font.SysFont(None, 28)

    game_over        = False
    game_over_reason = ""

    while True:
        clock.tick(FPS)

        # ── events ──────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if event.key == pygame.K_r and game_over:
                    main(); return
            if event.type == pygame.MOUSEBUTTONDOWN:
                slicing = True
                blade.clear()
            if event.type == pygame.MOUSEBUTTONUP:
                slicing = False
                blade.clear()

        # ── gameplay ────────────────────────────────────────────────────────
        if not game_over:
            # spawn
            spawn_timer += 1
            if spawn_timer >= spawn_interval:
                spawn_timer = 0
                for _ in range(random.randint(1, 3)):
                    if random.random() < 0.15:
                        bombs.append(Bomb())
                    else:
                        fruits.append(Fruit())
                spawn_interval = max(38, spawn_interval - 1)

            # blade tracking
            if slicing:
                mx, my = pygame.mouse.get_pos()
                blade.add(mx, my)
            blade.update()

            # slice detection
            seg = blade.last_segment()
            if slicing and seg[0]:
                (x1, y1), (x2, y2) = seg

                for fruit in fruits[:]:
                    if fruit.hit_by(x1, y1, x2, y2):
                        score += 1
                        halves.append(Half(fruit.x, fruit.y, fruit.vx, fruit.vy,
                                           fruit.color, fruit.inner_color, fruit.radius, True))
                        halves.append(Half(fruit.x, fruit.y, fruit.vx, fruit.vy,
                                           fruit.color, fruit.inner_color, fruit.radius, False))
                        for _ in range(14):
                            particles.append(Particle(fruit.x, fruit.y, fruit.inner_color))
                        fruits.remove(fruit)

                for bomb in bombs[:]:
                    if bomb.hit_by(x1, y1, x2, y2):
                        game_over        = True
                        game_over_reason = "You sliced a bomb!"
                        for _ in range(25):
                            particles.append(Particle(bomb.x, bomb.y, (255, 100, 0)))
                        bombs.remove(bomb)

            # update & cull fruits
            for fruit in fruits[:]:
                fruit.update()
                if fruit.off_screen():
                    lives -= 1
                    fruits.remove(fruit)
                    if lives <= 0:
                        game_over        = True
                        game_over_reason = "You missed too many fruits!"

            for bomb in bombs[:]:
                bomb.update()
                if bomb.off_screen():
                    bombs.remove(bomb)

            for half in halves[:]:
                half.update()
                if half.done():
                    halves.remove(half)

            for p in particles[:]:
                p.update()
                if p.done():
                    particles.remove(p)

        # ── draw ────────────────────────────────────────────────────────────
        draw_bg(screen)

        for fruit    in fruits:    fruit.draw(screen)
        for bomb     in bombs:     bomb.draw(screen)
        for half     in halves:    half.draw(screen)
        for particle in particles: particle.draw(screen)
        blade.draw(screen)

        # HUD
        screen.blit(font_md.render(f"Score: {score}", True, WHITE), (20, 18))
        for i in range(lives):
            pygame.draw.circle(screen, RED, (WIDTH - 30 - i * 32, 32), 11)

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))

            def blit_center(surf, y):
                screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y))

            blit_center(font_lg.render("GAME OVER",         True, RED),    HEIGHT // 2 - 90)
            blit_center(font_md.render(game_over_reason,    True, WHITE),  HEIGHT // 2 - 20)
            blit_center(font_md.render(f"Score: {score}",   True, YELLOW), HEIGHT // 2 + 30)
            blit_center(font_sm.render("R – restart   ESC – quit",
                                       True, (180, 180, 180)),              HEIGHT // 2 + 90)

        pygame.display.flip()


if __name__ == "__main__":
    main()
