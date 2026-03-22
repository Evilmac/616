import os
import json
import importlib
import datetime
import threading

DATA_DIR = "data"
MEMORIA_FILE = os.path.join(DATA_DIR, "memoria.json")
MODULOS_DIR = "modulos"

class Memoria:
    def __init__(self, ruta=MEMORIA_FILE):
        self.ruta = ruta
        os.makedirs(os.path.dirname(self.ruta), exist_ok=True)
        self.datos = {"objetivos": [], "historial_ia": [], "tareas_programadas": []}
        self.cargar()

    def cargar(self):
        if os.path.exists(self.ruta):
            with open(self.ruta, "r", encoding="utf-8") as f:
                try:
                    self.datos.update(json.load(f))
                except: pass

    def guardar(self):
        with open(self.ruta, "w", encoding="utf-8") as f:
            json.dump(self.datos, f, ensure_ascii=False, indent=2)

    def __getitem__(self, clave):
        return self.datos.get(clave)

    def __setitem__(self, clave, valor):
        self.datos[clave] = valor
        self.guardar()

class Asistente:
    def __init__(self, nombre="Jarvis"):
        self.nombre = nombre
        self.memoria = Memoria()
        self.comandos = {}
        self.modulos = {}
        self._registrar_basicos()
        self.cargar_modulos()

    def _registrar_basicos(self):
        self.comandos["ayuda"] = self.cmd_ayuda
        self.comandos["modulos"] = self.cmd_modulos
        self.comandos["recargar"] = self.cmd_recargar
        self.comandos["salir"] = lambda _: "__SALIR__"

    def cargar_modulos(self):
        # Limpiamos comandos antes de recargar (excepto básicos)
        self.comandos = {}
        self._registrar_basicos()
        
        os.makedirs(MODULOS_DIR, exist_ok=True)
        # Importante: Añadir el directorio de módulos al path para importlib
        import sys
        if MODULOS_DIR not in sys.path:
            sys.path.append(os.path.abspath(MODULOS_DIR))

        for archivo in os.listdir(MODULOS_DIR):
            if archivo.endswith(".py"):
                nombre_mod = archivo[:-3]
                try:
                    # Carga dinámica
                    modulo = importlib.import_module(nombre_mod)
                    importlib.reload(modulo)
                    if hasattr(modulo, "Plugin"):
                        p = modulo.Plugin(self)
                        self.modulos[p.nombre] = p
                        for cmd, func in p.comandos.items():
                            self.comandos[cmd] = func
                except Exception as e:
                    print(f"⚠️ Error cargando {archivo}: {e}")

    def cmd_ayuda(self, _):
        return "🛠️ Comandos: " + ", ".join(sorted(self.comandos.keys()))

    def cmd_modulos(self, _):
        return "🧩 Módulos activos: " + ", ".join(self.modulos.keys())

    def cmd_recargar(self, _):
        self.cargar_modulos()
        return "🔄 Sistema y plugins actualizados."

    def procesar(self, texto):
        texto = texto.strip()
        if not texto: return "..."
        partes = texto.split(" ", 1)
        cmd = partes[0].lower()
        args = partes[1] if len(partes) > 1 else ""

        if cmd in self.comandos:
            return self.comandos[cmd](args)
        
        # Fallback a IA si el comando no existe y el plugin IA está cargado
        if "preguntar" in self.comandos:
            return self.comandos["preguntar"](texto)
        
        return f"❌ Comando '{cmd}' no reconocido. Escribe 'ayuda'."

def bucle_terminal(asistente):
    print(f"--- {asistente.nombre} V6 (Terminal Mode) ---")
    while True:
        try:
            entrada = input("> ")
            res = asistente.procesar(entrada)
            if res == "__SALIR__":
                print("Cerrando sistema...")
                os._exit(0) # Cierra todo, incluyendo la GUI
            print(res)
        except EOFError: break
        except KeyboardInterrupt: break

if __name__ == "__main__":
    jarvis = Asistente("Jarvis")
    
    # Lanzamos la terminal en el hilo principal
    # La GUI se lanzará en un hilo aparte cuando escribas 'gui'
    bucle_terminal(jarvis)