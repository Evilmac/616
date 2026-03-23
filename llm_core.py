import subprocess
import json


class LocalLLM:
    """
    Interfaz para comunicarse con un modelo LLM local usando Ollama.
    """

    def __init__(self, model_name="llama3"):
        self.model_name = model_name

    def generate(self, prompt):
        """
        Envía un prompt al modelo local y devuelve la respuesta generada.
        """
        try:
            result = subprocess.run(
                ["ollama", "run", self.model_name],
                input=prompt.encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            output = result.stdout.decode("utf-8").strip()

            # Ollama devuelve JSON línea por línea
            try:
                json_lines = [json.loads(line) for line in output.split("\n") if line.strip()]
                final_text = "".join([chunk.get("response", "") for chunk in json_lines])
                return final_text

            except json.JSONDecodeError:
                # Si no es JSON, devolvemos el texto tal cual
                return output

        except Exception as e:
            return f"Error ejecutando el modelo local: {str(e)}"