import pyttsx3


class VoiceOutput:
    """
    Convierte texto en voz usando pyttsx3 (motor local).
    """

    def __init__(self, rate=170, volume=1.0, voice_id=None):
        self.engine = pyttsx3.init()

        # Velocidad de habla
        self.engine.setProperty("rate", rate)

        # Volumen
        self.engine.setProperty("volume", volume)

        # Selección de voz (si se especifica)
        if voice_id is not None:
            self.engine.setProperty("voice", voice_id)

    def speak(self, text):
        """
        Reproduce el texto en voz alta.
        """
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Error al reproducir voz: {str(e)}")


# Función directa para usar en app.py
def speak_text(text):
    speaker = VoiceOutput()
    speaker.speak(text)