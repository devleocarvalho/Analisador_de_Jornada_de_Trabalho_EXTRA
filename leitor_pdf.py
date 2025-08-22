import PyPDF2

def ler_pdf(caminho_arquivo):
    """
    Lê o conteúdo de um arquivo .pdf e retorna o texto completo.
    """
    texto_completo = ""
    try:
        with open(caminho_arquivo, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                texto_completo += page.extract_text()
        return texto_completo
    except Exception as e:
        return f"Erro ao ler arquivo PDF: {e}"
