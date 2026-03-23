class ConversationMemory:
    """
    Memoria sencilla en RAM para guardar el historial de la conversación.
    """

    def __init__(self, max_messages=30):
        self.messages = []
        self.max_messages = max_messages

    def add_user_message(self, content):
        self._add_message("usuario", content)

    def add_assistant_message(self, content):
        self._add_message("asistente", content)

    def _add_message(self, role, content):
        self.messages.append({"role": role, "content": content})

        # Limitar tamaño de historial
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages :]

    def get_history(self):
        """
        Devuelve el historial en formato texto para meterlo en el prompt.
        """
        lines = []
        for msg in self.messages:
            prefix = "Usuario" if msg["role"] == "usuario" else "Asistente"
            lines.append(f"{prefix}: {msg['content']}")
        return "\n".join(lines)