import random
import string
import pygame
import requests

pygame.init()

# --- CONFIGURACIÓN ---
WIDTH, HEIGHT = 1080, 720
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jarvis Offline Assistant HUD")

FPS = 60
FONT = pygame.font.SysFont("consolas", 20, bold=True)
SMALL_FONT = pygame.font.SysFont("consolas", 16)

LETTER_COUNT = 160
SPEED_MIN = 1
SPEED_MAX = 4

# Módulos basados en tu megaprompt
MODULES = [
    "LLM local (llama.cpp + Mistral 7B)",
    "Memoria conversación",
    "Memoria vectorial (FAISS)",
    "RAG PDFs (PoDoFo)",
    "Voz IN (whisper.cpp)",
    "Voz OUT (eSpeak)",
    "Web UI (HTTP C++)",
]

# --- CONSULTA A OLLAMA ---
def consultar_ollama():
    prompt = (
        "Genera un mensaje técnico corto, estilo Jarvis, sobre el estado de un asistente offline. "
        "Debe sonar profesional, conciso y relacionado con módulos como FAISS, RAG, embeddings, voz o servidor HTTP."
    )

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3.2:1b", "prompt": prompt, "stream": False},
            timeout=5
        )

        texto = ""
        for line in response.iter_lines():
            if line:
                data = line.decode("utf-8")
                if '"response":"' in data:
                    fragment = data.split('"response":"')[1].split('"')[0]
                    texto += fragment

        return texto.strip() if texto else "Procesando..."
    except:
        return "Ollama no responde."


# --- CLASE LETRA (paquetes de datos) ---
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
        self.color = (0, random.randint(150, 255), 0)

    def update(self, mouse_pos, modules_active_ratio):
        mx, my = mouse_pos
        dist_x = self.x - mx
        dist_y = self.y - my
        dist = abs(dist_x) + abs(dist_y)

        # Huyen del ratón
        if dist < 120:
            if dist_x != 0:
                self.dx = 1 if dist_x > 0 else -1
            if dist_y != 0:
                self.dy = 1 if dist_y > 0 else -1
            self.speed = SPEED_MAX + 2
            self.color = (255, 80, 80)
        else:
            # Velocidad ligada a módulos activos
            base = SPEED_MIN
            extra = modules_active_ratio * 4
            self.speed = random.uniform(base, base + extra)
            self.color = (0, random.randint(150, 255), 0)

        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

        # Wrap-around
        if self.x < 0: self.x = WIDTH
        if self.x > WIDTH: self.x = 0
        if self.y < 0: self.y = HEIGHT
        if self.y > HEIGHT: self.y = 0

        # Flicker
        if random.random() < 0.02:
            self.char = random.choice(string.ascii_uppercase + string.digits)

    def draw(self, surface):
        text = FONT.render(self.char, True, self.color)
        surface.blit(text, (self.x, self.y))


# --- NÚCLEO JARVIS ---
class JarvisCore:
    def __init__(self):
        self.current_msg = "Inicializando..."
        self.timer = 0
        self.interval = 3500  # cada 3.5 segundos consulta a Ollama
        self.modules_state = {m: False for m in MODULES}

    def toggle_module(self, index):
        name = MODULES[index]
        self.modules_state[name] = not self.modules_state[name]

    def active_ratio(self):
        total = len(self.modules_state)
        active = sum(1 for v in self.modules_state.values() if v)
        return active / total if total > 0 else 0

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.interval:
            self.timer = 0
            self.current_msg = consultar_ollama()

    def draw(self, surface):
        cx, cy = WIDTH // 2, HEIGHT // 2

        # Núcleo
        pygame.draw.circle(surface, (0, 120, 255), (cx, cy), 80, 2)
        pygame.draw.circle(surface, (0, 200, 255), (cx, cy), 8)

        # Mensaje IA
        msg = self.current_msg
        text = SMALL_FONT.render(msg, True, (0, 200, 255))
        rect = text.get_rect(center=(cx, cy + 100))
        surface.blit(text, rect)

        # Panel de módulos
        panel_x = 20
        panel_y = 20
        panel_w = 360
        panel_h = 35 + 25 * len(MODULES)

        pygame.draw.rect(surface, (8, 8, 8), (panel_x - 10, panel_y - 10, panel_w, panel_h))
        pygame.draw.rect(surface, (0, 150, 255), (panel_x - 10, panel_y - 10, panel_w, panel_h), 1)

        title = SMALL_FONT.render("MÓDULOS JARVIS OFFLINE (clic para activar)", True, (0, 150, 255))
        surface.blit(title, (panel_x, panel_y))

        for i, name in enumerate(MODULES):
            y = panel_y + 30 + i * 22
            active = self.modules_state[name]
            color = (0, 220, 100) if active else (140, 140, 140)
            dot_color = (0, 255, 0) if active else (80, 80, 80)

            pygame.draw.circle(surface, dot_color, (panel_x + 5, y + 8), 5)
            txt = SMALL_FONT.render(name, True, color)
            surface.blit(txt, (panel_x + 18, y))

    def handle_click(self, pos):
        x, y = pos
        panel_x = 20
        panel_y = 20
        for i, name in enumerate(MODULES):
            item_y = panel_y + 30 + i * 22
            rect = pygame.Rect(panel_x - 10, item_y, 360, 20)
            if rect.collidepoint(x, y):
                self.toggle_module(i)


# --- CREAR LETRAS ---
letters = [Letter() for _ in range(LETTER_COUNT)]
jarvis = JarvisCore()

clock = pygame.time.Clock()
running = True

# --- LOOP PRINCIPAL ---
while running:
    dt = clock.tick(FPS)
    SCREEN.fill((0, 0, 0))

    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            jarvis.handle_click(mouse_pos)

    active_ratio = jarvis.active_ratio()

    for letter in letters:
        letter.update(mouse_pos, active_ratio)
        letter.draw(SCREEN)

    jarvis.update(dt)
    jarvis.draw(SCREEN)

    pygame.display.flip()

pygame.quit()