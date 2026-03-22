import tkinter as tk
from tkinter import scrolledtext
import threading

class Plugin:
    nombre = "interfaz"

    def __init__(self, asistente):
        self.asistente = asistente
        self.comandos = {"gui": self.lanzar_interfaz}

    def lanzar_interfaz(self, _):
        # Ejecutamos la ventana en un hilo separado para no bloquear el núcleo
        threading.Thread(target=self._crear_ventana, daemon=True).start()
        return "🖥️ Interfaz gráfica iniciada."

    def _crear_ventana(self):
        root = tk.Tk()
        root.title(f"{self.asistente.nombre} - Panel de Control Local")
        root.geometry("600x500")
        root.configure(bg="#1e1e1e")

        # Título
        label = tk.Label(root, text="SISTEMA JARVIS V6", fg="#00ff00", bg="#1e1e1e", font=("Courier", 16, "bold"))
        label.pack(pady=10)

        # Área de chat
        self.chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, bg="#2d2d2d", fg="white", font=("Consolas", 10))
        self.chat_area.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        # Entrada de texto
        self.entrada = tk.Entry(root, bg="#3d3d3d", fg="white", insertbackground="white", font=("Consolas", 11))
        self.entrada.pack(padx=20, pady=10, fill=tk.X)
        self.entrada.bind("<Return>", lambda e: self._enviar())

        # Botón de enviar
        btn_enviar = tk.Button(root, text="EJECUTAR", command=self._enviar, bg="#007acc", fg="white", font=("Arial", 10, "bold"))
        btn_enviar.pack(pady=5)

        root.mainloop()

    def _enviar(self):
        texto = self.entrada.get()
        if texto:
            self.chat_area.insert(tk.END, f"\n👤 Tú: {texto}\n")
            self.entrada.delete(0, tk.END)
            
            # Procesar y responder
            respuesta = self.asistente.procesar(texto)
            self.chat_area.insert(tk.END, f"🤖 Jarvis: {respuesta}\n")
            self.chat_area.see(tk.END)