from PIL import Image
import pytesseract

def ler_imagem(caminho_arquivo):
    """
    Lê texto de uma imagem usando OCR.
    """
    try:
        # Se você instalou o tesseract em um caminho não padrão, descomente e ajuste a linha abaixo
        # pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

        texto = pytesseract.image_to_string(Image.open(caminho_arquivo))
        return texto
    except Exception as e:
        return f"Erro ao ler imagem: {e}"
