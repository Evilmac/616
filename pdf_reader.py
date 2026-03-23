import PyPDF2


class PDFReader:
    """
    Lector de PDFs que extrae texto completo.
    """

    def extract_text(self, pdf_path):
        """
        Recibe la ruta de un PDF y devuelve su texto.
        """
        try:
            text = ""

            with open(pdf_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)

                for page in reader.pages:
                    text += page.extract_text() or ""

            return text

        except Exception as e:
            return f"Error leyendo PDF: {str(e)}"