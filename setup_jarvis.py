import os
import sys
import subprocess

def instalar_librerias():
    print("📦 Instalando dependencias (esto puede tardar un poco)...")
    librerias = ["requests", "schedule", "sentence-transformers", "faiss-cpu"]
    subprocess.check_call([sys.executable, "-m", "pip", "install"] + librerias)

def crear_sistema():
    # Definición de archivos y contenido
    archivos = {
        "main.py": """
import os, json, importlib, datetime
class Memoria:
    def __init__(self, ruta="data/memoria.json"):
        self.ruta = ruta
        os.makedirs("data", exist_ok=True)
        self.datos = {"objetivos": [], "historial": []}
        if os.path.exists(ruta):
            with open(ruta, "r") as f: self.datos.update(json.load(f))
    def guardar(self):
        with open(self.ruta, "w") as f: json.dump(self.datos, f, indent=2)
    def __getitem__(self, k): return self.datos.get(k)
    def __setitem__(self, k, v): self.datos[k] = v; self.guardar()

class Asistente:
    def __init__(self):
        self.memoria = Memoria()
        self.comandos = {}
        self._cargar_basicos()
        self.cargar_plugins()
    def _cargar_basicos(self):
        self.comandos = {"ayuda": lambda _: "Comandos: "+", ".join(self.comandos.keys()), "salir": lambda _: "__SALIR__"}
    def cargar_plugins(self):
        os.makedirs("modulos", exist_ok=True)
        for f in os.listdir("modulos"):
            if f.endswith(".py"):
                m = importlib.import_module(f"modulos.{f[:-3]}")
                importlib.reload(m)
                if hasattr(m, "Plugin"):
                    p = m.Plugin(self)
                    for c, func in p.comandos.items(): self.comandos[c] = func
    def procesar(self, t):
        p = t.strip().split(" ", 1)
        c = p[0].lower()
        a = p[1] if len(p)>1 else ""
        if c in self.comandos: return self.comandos[c](a)
        if "preguntar" in self.comandos: return self.comandos["preguntar"](t)
        return "Comando no reconocido."

if __name__ == "__main__":
    jarvis = Asistente()
    print("--- Jarvis Online ---")
    while True:
        e = input("> "); r = jarvis.procesar(e)
        if r == "__SALIR__": break
        print(r)
""",
        "modulos/ia.py": """
import requests
class Plugin:
    nombre = "ia"
    def __init__(self, a): self.a = a; self.comandos = {"preguntar": self.ask}
    def ask(self, prompt):
        try:
            r = requests.post("http://localhost:11434/api/generate", 
                             json={"model": "llama3", "prompt": f"Eres Jarvis. Contexto: {self.a.memoria['objetivos']}. Usuario: {prompt}", "stream": False})
            return r.json()['response']
        except: return "Asegúrate de tener Ollama abierto."
""",
        "modulos/sistema.py": """
import subprocess
class Plugin:
    nombre = "sistema"
    def __init__(self, a): self.a = a; self.comandos = {"ejecutar": self.ps, "gpu": self.gpu}
    def ps(self, c):
        r = subprocess.run(["powershell", "-Command", c], capture_output=True, text=True, encoding='latin-1')
        return r.stdout if r.returncode==0 else r.stderr
    def gpu(self, _):
        return self.ps("nvidia-smi --query-gpu=utilization.gpu,temperature.gpu --format=csv,noheader")
""",
        "modulos/objetivos.py": """
class Plugin:
    nombre = "objetivos"
    def __init__(self, a): self.a = a; self.comandos = {"objetivo": self.add}
    def add(self, t):
        o = self.a.memoria["objetivos"]; o.append(t); self.a.memoria["objetivos"] = o
        return f"Objetivo guardado: {t}"
"""
    }

    print("📂 Creando archivos y carpetas...")
    os.makedirs("modulos", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("conocimiento", exist_ok=True)

    for ruta, contenido in archivos.items():
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(contenido.strip())
        print(f"✔️ {ruta}")

if __name__ == "__main__":
    instalar_librerias()
    crear_sistema()
    print("\n🚀 TODO LISTO. Pasos finales:")
    print("1. Abre la aplicación Ollama.")
    print("2. Ejecuta: python main.py")