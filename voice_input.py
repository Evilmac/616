import whisper_timestamped as whisper

model = whisper.load_model("small")

def transcribe_audio(audio_path):
    result = whisper.transcribe(model, audio_path)
    return result["text"]

class VoiceInput:
    """
    Transcripción de voz a texto usando Whisper local.
    """

    def __init__(self, model_name="small"):
        # Carga del modelo Whisper local
        self.model = whisper.load_model(model_name)

    def transcribe_audio(self, audio_path):
        """
        Recibe un archivo de audio y devuelve el texto transcrito.
        """
        try:
            result = self.model.transcribe(audio_path)
            return result.get("text", "").strip()

        except Exception as e:
            return f"Error al transcribir audio: {str(e)}"


# Función directa para usar en app.py
def transcribe_audio(audio_path):
    model = VoiceInput()
    return model.transcribe_audio(audio_path)