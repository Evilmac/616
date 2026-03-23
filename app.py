import gradio as gr
from llm_core import LocalLLM
from memory import ConversationMemory
from vector_memory import VectorMemory
from pdf_reader import PDFReader
from voice_input import transcribe_audio
from voice_output import speak_text


# Inicialización de módulos
llm = LocalLLM()
memory = ConversationMemory()
vector_store = VectorMemory()
pdf_reader = PDFReader()


def process_text(user_input):
    """
    Procesa texto del usuario:e
    
    - Guarda memoria de conversación
    - Recupera contexto RAG
    - Genera respuesta del LLM
    - Devuelve respuesta final
    """
    memory.add_user_message(user_input)

    # Recuperar contexto desde memoria vectorial
    rag_context = vector_store.search(user_input)

    prompt = f"""
    CONTEXTO RELEVANTE:
    {rag_context}

    HISTORIAL:
    {memory.get_history()}

    USUARIO:
    {user_input}

    ASISTENTE:
    """

    response = llm.generate(prompt)
    memory.add_assistant_message(response)

    return response


def process_pdf(pdf_file):
    """
    Lee un PDF, extrae texto y lo indexa en FAISS.
    """
    text = pdf_reader.extract_text(pdf_file)
    vector_store.add_document(text)
    return "PDF procesado e indexado correctamente."


def process_voice(audio_file):
    """
    Convierte voz a texto y procesa como mensaje normal.
    """
    text = transcribe_audio(audio_file)
    response = process_text(text)
    speak_text(response)
    return response


# Interfaz web con Gradio
def launch_ui():
    with gr.Blocks(title="Jarvis Offline") as ui:
        gr.Markdown("# 🤖 Jarvis Offline — Asistente IA 100% Local")

        with gr.Tab("Chat"):
            chat_input = gr.Textbox(label="Escribe aquí")
            chat_output = gr.Textbox(label="Respuesta")
            chat_button = gr.Button("Enviar")
            chat_button.click(process_text, chat_input, chat_output)

        with gr.Tab("PDFs"):
            pdf_input = gr.File(label="Sube un PDF")
            pdf_output = gr.Textbox(label="Estado")
            pdf_button = gr.Button("Procesar PDF")
            pdf_button.click(process_pdf, pdf_input, pdf_output)

        with gr.Tab("Voz"):
            audio_input = gr.Audio(sources="microphone", type="filepath")
            audio_output = gr.Textbox(label="Respuesta por voz")
            audio_button = gr.Button("Hablar")
            audio_button.click(process_voice, audio_input, audio_output)

    ui.launch()


if __name__ == "__main__":
    launch_ui()