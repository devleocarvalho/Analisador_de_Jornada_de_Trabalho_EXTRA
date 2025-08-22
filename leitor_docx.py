import docx

def ler_docx(caminho_arquivo):
    """
    Lê o conteúdo de um arquivo .docx e retorna o texto completo.
    """
    texto_completo = []
    try:
        doc = docx.Document(caminho_arquivo)
        for para in doc.paragraphs:
            texto_completo.append(para.text)
        return "\n".join(texto_completo)
    except Exception as e:
        return f"Erro ao ler arquivo DOCX: {e}"
