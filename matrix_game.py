import pygame
import random
import string

pygame.init()

# --- CONFIGURACIÓN ---
WIDTH, HEIGHT = 1080, 1080
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Matrix Pixel Game")

FPS = 60
FONT = pygame.font.SysFont("consolas", 24, bold=True)

LETTER_COUNT = 200
SPEED_MIN = 1
SPEED_MAX = 4

# --- CLASE LETRA ---
class Letter:
    def __init__(self):
        self.char = random.choice(string.ascii_uppercase + string.digits)
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.dx = random.choice([-1, 0, 1])
        self.dy = random.choice([-1, 0, 1])
        if self.dx == 0 and self.dy == 0:
            self.dx = 1
        self.speed = random.uniform(SPEED_MIN, SPEED_MAX)

    def update(self):
        # Movimiento
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

        # Wrap-around
        if self.x < 0: self.x = WIDTH
        if self.x > WIDTH: self.x = 0
        if self.y < 0: self.y = HEIGHT
        if self.y > HEIGHT: self.y = 0

        # Flicker aleatorio
        if random.random() < 0.02:
            self.char = random.choice(string.ascii_uppercase + string.digits)

    def draw(self, surface):
        text = FONT.render(self.char, True, (255, 0, 0))
        surface.blit(text, (self.x, self.y))

    def change_direction(self):
        self.dx = random.choice([-1, 0, 1])
        self.dy = random.choice([-1, 0, 1])
        if self.dx == 0 and self.dy == 0:
            self.dx = 1


# --- CREAR LETRAS ---
letters = [Letter() for _ in range(LETTER_COUNT)]

clock = pygame.time.Clock()
running = True

# --- LOOP PRINCIPAL ---
while running:
    clock.tick(FPS)
    SCREEN.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # CLICK: cambiar dirección
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            for letter in letters:
                if abs(letter.x - mx) < 20 and abs(letter.y - my) < 20:
                    letter.change_direction()

    # Actualizar y dibujar letras
    for letter in letters:
        letter.update()
        letter.draw(SCREEN)

    pygame.display.flip()

pygame.quit()