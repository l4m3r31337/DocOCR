from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import os

def extract_text(file_path):
    # Пути к инструментам
    poppler_path = r"C:\Program Files\poppler-25.07.0\Library\bin"
    tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    pytesseract.pytesseract.tesseract_cmd = tesseract_path

    if file_path.lower().endswith('.pdf'):
        images = convert_from_path(file_path, poppler_path=poppler_path)
        text = "\n".join(pytesseract.image_to_string(img, lang='rus+eng') for img in images)
    else:
        text = pytesseract.image_to_string(Image.open(file_path), lang='rus+eng')

    return text

if __name__ == "__main__":
    file_path = r"C:\Dev\DocOCR\tests\test 1.pdf"
    if not os.path.exists(file_path):
        print("Файл не найден:", file_path)
    else:
        print(extract_text(file_path))
