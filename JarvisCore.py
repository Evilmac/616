class JarvisCore:
    def __init__(self):
        self.current_msg = "Inicializando..."
        self.timer = 0
        self.interval = 3500  # cada 3.5s consulta a Ollama
        self.modules_state = {m: False for m in MODULES}
        self.last_spoken = ""  # evita repetir voz

    def toggle_module(self, index):
        name = MODULES[index]
        self.modules_state[name] = not self.modules_state[name]

    def active_ratio(self):
        total = len(self.modules_state)
        active = sum(1 for v in self.modules_state.values() if v)
        return active / total if total > 0 else 0

    def speak(self, text):
        """Habla el mensaje usando TTS offline."""
        global tts
        try:
            tts.stop()
            tts.say(text)
            tts.runAndWait()
        except:
            pass

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.interval:
            self.timer = 0

            # Obtener mensaje de Ollama
            nuevo_msg = consultar_ollama()
            self.current_msg = nuevo_msg

            # Hablar solo si es diferente al anterior
            if nuevo_msg != self.last_spoken:
                self.speak(nuevo_msg)
                self.last_spoken = nuevo_msg

    def draw(self, surface):
        cx, cy = WIDTH // 2, HEIGHT // 2

        # Núcleo visual
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

        title = SMALL_FONT.render("MÓDULOS JARVIS (clic para activar)", True, (0, 150, 255))
        surface.blit(title, (panel_x, panel_y))

        for i, name in enumerate(MODULES):
            y = panel_y + 30 + i * 25
            active = self.modules_state[name]
            color = (0, 255, 100) if active else (150, 150, 150)
            dot = (0, 255, 0) if active else (80, 80, 80)

            pygame.draw.circle(surface, dot, (panel_x + 5, y + 8), 5)
            txt = SMALL_FONT.render(name, True, color)
            surface.blit(txt, (panel_x + 20, y))

    def handle_click(self, pos):
        x, y = pos
        panel_x = 20
        panel_y = 20

        for i, name in enumerate(MODULES):
            item_y = panel_y + 30 + i * 25
            rect = pygame.Rect(panel_x, item_y, 350, 20)
            if rect.collidepoint(x, y):
                self.toggle_module(i)