import pygame
import math
import random
import sys

# =========================
# CONFIGURAÇÕES INICIAIS
# =========================
pygame.init()

WIDTH, HEIGHT = 1000, 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroids - Python")

CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont("Arial", 28)
BIG_FONT = pygame.font.SysFont("Arial", 52)

WHITE = (255, 255, 255)
BLACK = (10, 10, 20)
GRAY = (120, 120, 120)
RED = (220, 60, 60)
YELLOW = (255, 220, 100)
GREEN = (100, 255, 140)
BLUE = (120, 180, 255)

MAX_LEVEL = 5  # FASE FINAL

# =========================
# FUNÇÕES AUXILIARES
# =========================
def wrap_position(x, y):
    if x < 0:
        x = WIDTH
    elif x > WIDTH:
        x = 0

    if y < 0:
        y = HEIGHT
    elif y > HEIGHT:
        y = 0

    return x, y

def distance(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)

# =========================
# CLASSE NAVE
# =========================
class Ship:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.angle = 0
        self.vel_x = 0
        self.vel_y = 0
        self.radius = 18
        self.alive = True
        self.invulnerable_timer = 120

    def update(self, keys):
        if not self.alive:
            return

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.angle += 4
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.angle -= 4

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            rad = math.radians(self.angle)
            self.vel_x += math.sin(rad) * 0.15
            self.vel_y += math.cos(rad) * 0.15

        self.vel_x *= 0.99
        self.vel_y *= 0.99

        speed = math.hypot(self.vel_x, self.vel_y)
        max_speed = 7
        if speed > max_speed:
            scale = max_speed / speed
            self.vel_x *= scale
            self.vel_y *= scale

        self.x += self.vel_x
        self.y -= self.vel_y

        self.x, self.y = wrap_position(self.x, self.y)

        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1

    def draw(self, screen, color=WHITE):
        if not self.alive:
            return

        if self.invulnerable_timer > 0 and (self.invulnerable_timer // 5) % 2 == 0:
            return

        rad = math.radians(self.angle)

        tip = (
            self.x + math.sin(rad) * 25,
            self.y - math.cos(rad) * 25
        )
        left = (
            self.x + math.sin(rad + math.radians(140)) * 20,
            self.y - math.cos(rad + math.radians(140)) * 20
        )
        right = (
            self.x + math.sin(rad - math.radians(140)) * 20,
            self.y - math.cos(rad - math.radians(140)) * 20
        )

        pygame.draw.polygon(screen, color, [tip, left, right], 2)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            flame = (
                self.x + math.sin(rad + math.pi) * 18,
                self.y - math.cos(rad + math.pi) * 18
            )
            flame_left = (
                self.x + math.sin(rad + math.radians(160)) * 10,
                self.y - math.cos(rad + math.radians(160)) * 10
            )
            flame_right = (
                self.x + math.sin(rad - math.radians(160)) * 10,
                self.y - math.cos(rad - math.radians(160)) * 10
            )
            pygame.draw.polygon(screen, YELLOW, [flame, flame_left, flame_right], 2)

    def shoot(self, offset_x=0, offset_y=0, angle_offset=0):
        rad = math.radians(self.angle + angle_offset)
        bullet_speed = 10
        bullet_dx = math.sin(rad) * bullet_speed
        bullet_dy = -math.cos(rad) * bullet_speed

        return Bullet(
            self.x + math.sin(rad) * 25 + offset_x,
            self.y - math.cos(rad) * 25 + offset_y,
            bullet_dx,
            bullet_dy
        )

# =========================
# NAVE AUXILIAR
# =========================
class HelperShip:
    def __init__(self, player, side=1):
        self.player = player
        self.side = side
        self.radius = 14

    def get_position(self):
        offset = 50 * self.side
        angle_rad = math.radians(self.player.angle + 90)
        hx = self.player.x + math.sin(angle_rad) * offset
        hy = self.player.y - math.cos(angle_rad) * offset
        return hx, hy

    def draw(self, screen):
        hx, hy = self.get_position()
        rad = math.radians(self.player.angle)

        tip = (
            hx + math.sin(rad) * 18,
            hy - math.cos(rad) * 18
        )
        left = (
            hx + math.sin(rad + math.radians(140)) * 14,
            hy - math.cos(rad + math.radians(140)) * 14
        )
        right = (
            hx + math.sin(rad - math.radians(140)) * 14,
            hy - math.cos(rad - math.radians(140)) * 14
        )

        pygame.draw.polygon(screen, BLUE, [tip, left, right], 2)

    def shoot(self):
        hx, hy = self.get_position()
        rad = math.radians(self.player.angle)
        bullet_speed = 10
        bullet_dx = math.sin(rad) * bullet_speed
        bullet_dy = -math.cos(rad) * bullet_speed

        return Bullet(
            hx + math.sin(rad) * 18,
            hy - math.cos(rad) * 18,
            bullet_dx,
            bullet_dy
        )

# =========================
# CLASSE TIRO
# =========================
class Bullet:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.life = 60
        self.radius = 3

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.x, self.y = wrap_position(self.x, self.y)
        self.life -= 1

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)

# =========================
# CLASSE ASTEROIDE
# =========================
class Asteroid:
    def __init__(self, x=None, y=None, size=3):
        self.size = size

        if x is None:
            self.x = random.choice([random.randint(0, 100), random.randint(WIDTH - 100, WIDTH)])
            self.y = random.choice([random.randint(0, 100), random.randint(HEIGHT - 100, HEIGHT)])
        else:
            self.x = x
            self.y = y

        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1, 2.5) + (4 - size) * 0.4
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed

        self.rotation = random.uniform(-2, 2)
        self.angle = random.uniform(0, 360)

        self.radius = {3: 40, 2: 25, 1: 15}[size]
        self.shape = self.generate_shape()

    def generate_shape(self):
        points = []
        num_points = random.randint(8, 12)
        for i in range(num_points):
            angle = (2 * math.pi / num_points) * i
            offset = random.uniform(0.75, 1.25)
            r = self.radius * offset
            points.append((angle, r))
        return points

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.angle += self.rotation
        self.x, self.y = wrap_position(self.x, self.y)

    def draw(self, screen):
        pts = []
        for ang, r in self.shape:
            final_ang = ang + math.radians(self.angle)
            px = self.x + math.cos(final_ang) * r
            py = self.y + math.sin(final_ang) * r
            pts.append((px, py))
        pygame.draw.polygon(screen, GRAY, pts, 2)

# =========================
# FUNÇÕES DO JOGO
# =========================
def create_asteroids(level):
    asteroids = []
    amount = 3 + level
    for _ in range(amount):
        asteroids.append(Asteroid(size=3))
    return asteroids

def split_asteroid(asteroid):
    new_asteroids = []
    if asteroid.size > 1:
        for _ in range(2):
            new_asteroids.append(Asteroid(asteroid.x, asteroid.y, asteroid.size - 1))
    return new_asteroids

def draw_text_center(surface, text, font, color, y):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(WIDTH // 2, y))
    surface.blit(rendered, rect)

def reset_game():
    ship = Ship()
    bullets = []
    level = 1
    score = 0
    lives = 3
    asteroids = create_asteroids(level)
    helper_ships = []
    shot_level = 1  # começa com 1 tiro
    return ship, bullets, asteroids, score, lives, level, helper_ships, shot_level

# =========================
# LOOP PRINCIPAL
# =========================
ship, bullets, asteroids, score, lives, level, helper_ships, shot_level = reset_game()

shoot_cooldown = 0
game_over = False
game_won = False
choosing_upgrade = False
running = True

while running:
    CLOCK.tick(60)
    SCREEN.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if choosing_upgrade:
                if event.key == pygame.K_1:
                    side = 1 if len(helper_ships) % 2 == 0 else -1
                    helper_ships.append(HelperShip(ship, side=side))
                    choosing_upgrade = False
                    asteroids = create_asteroids(level)
                    ship.invulnerable_timer = 120

                elif event.key == pygame.K_2:
                    shot_level += 2  # aumenta a quantidade de tiros
                    choosing_upgrade = False
                    asteroids = create_asteroids(level)
                    ship.invulnerable_timer = 120

            elif event.key == pygame.K_SPACE and not game_over and not game_won and ship.alive:
                if shoot_cooldown <= 0:
                    spacing = 14

                    if shot_level == 1:
                        bullets.append(ship.shoot())
                    else:
                        start = -(shot_level - 1) / 2
                        for i in range(shot_level):
                            offset_x = (start + i) * spacing
                            bullets.append(ship.shoot(offset_x=offset_x))

                    for helper in helper_ships:
                        bullets.append(helper.shoot())

                    shoot_cooldown = 12

            if event.key == pygame.K_r and (game_over or game_won):
                ship, bullets, asteroids, score, lives, level, helper_ships, shot_level = reset_game()
                game_over = False
                game_won = False
                choosing_upgrade = False

    keys = pygame.key.get_pressed()

    if shoot_cooldown > 0:
        shoot_cooldown -= 1

    if not game_over and not game_won and not choosing_upgrade:
        ship.update(keys)

        # Atualizar tiros
        for bullet in bullets[:]:
            bullet.update()
            if bullet.life <= 0:
                bullets.remove(bullet)

        # Atualizar asteroides
        for asteroid in asteroids:
            asteroid.update()

        # Colisão tiro x asteroide
        for bullet in bullets[:]:
            for asteroid in asteroids[:]:
                if distance(bullet.x, bullet.y, asteroid.x, asteroid.y) < asteroid.radius:
                    if bullet in bullets:
                        bullets.remove(bullet)
                    if asteroid in asteroids:
                        asteroids.remove(asteroid)
                        asteroids.extend(split_asteroid(asteroid))
                        score += {3: 20, 2: 50, 1: 100}[asteroid.size]
                    break

        # Colisão nave x asteroide
        if ship.invulnerable_timer <= 0 and ship.alive:
            for asteroid in asteroids:
                if distance(ship.x, ship.y, asteroid.x, asteroid.y) < (ship.radius + asteroid.radius - 5):
                    lives -= 1
                    if lives > 0:
                        ship.reset()
                    else:
                        ship.alive = False
                        game_over = True
                    break

        # PASSAR DE FASE OU VENCER
        if len(asteroids) == 0:
            if level >= MAX_LEVEL:
                game_won = True
            else:
                level += 1
                choosing_upgrade = True

    # Desenhar elementos
    ship.draw(SCREEN)

    for helper in helper_ships:
        helper.draw(SCREEN)

    for bullet in bullets:
        bullet.draw(SCREEN)

    for asteroid in asteroids:
        asteroid.draw(SCREEN)

    # HUD
    score_text = FONT.render(f"Pontuação: {score}", True, WHITE)
    lives_text = FONT.render(f"Vidas: {lives}", True, WHITE)
    level_text = FONT.render(f"Fase: {level}/{MAX_LEVEL}", True, WHITE)
    upgrade_text = FONT.render(f"Naves auxiliares: {len(helper_ships)} | Tiros: {shot_level}", True, GREEN)

    SCREEN.blit(score_text, (20, 20))
    SCREEN.blit(lives_text, (20, 55))
    SCREEN.blit(level_text, (20, 90))
    SCREEN.blit(upgrade_text, (20, 125))

    # Tela de escolha de upgrade
    if choosing_upgrade:
        draw_text_center(SCREEN, "ESCOLHA UM UPGRADE", BIG_FONT, GREEN, HEIGHT // 2 - 80)
        draw_text_center(SCREEN, "1 - Nave Auxiliar", FONT, BLUE, HEIGHT // 2)
        draw_text_center(SCREEN, "2 - +2 TIROS", FONT, YELLOW, HEIGHT // 2 + 50)

    # Tela de derrota
    if game_over:
        draw_text_center(SCREEN, "GAME OVER", BIG_FONT, RED, HEIGHT // 2 - 30)
        draw_text_center(SCREEN, "Pressione R para reiniciar", FONT, WHITE, HEIGHT // 2 + 30)

    # Tela de vitória
    if game_won:
        draw_text_center(SCREEN, "VOCÊ GANHOU!", BIG_FONT, GREEN, HEIGHT // 2 - 30)
        draw_text_center(SCREEN, f"Pontuação Final: {score}", FONT, WHITE, HEIGHT // 2 + 20)
        draw_text_center(SCREEN, "Pressione R para jogar novamente", FONT, WHITE, HEIGHT // 2 + 60)

    # Controles
    controls = FONT.render("Setas/A,D/W = mover | Espaço = atirar", True, (180, 180, 180))
    SCREEN.blit(controls, (WIDTH // 2 - 240, HEIGHT - 40))

    pygame.display.flip()

pygame.quit()
sys.exit()
