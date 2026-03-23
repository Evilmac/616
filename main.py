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