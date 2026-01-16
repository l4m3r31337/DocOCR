from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import os
import sys
from pathlib import Path
import shutil

def find_tesseract():
    """Найти Tesseract в системе"""
    # 1. Переменная окружения
    env = os.environ.get('TESSERACT_CMD')
    if env and Path(env).exists():
        return env
    
    # 2. Системный PATH
    path_cmd = shutil.which("tesseract")
    if path_cmd:
        return path_cmd
    
    # 3. Стандартные пути Windows
    if sys.platform == "win32":
        paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]
        for p in paths:
            if Path(p).exists():
                return p
    
    # 4. Стандартные пути Linux
    else:
        paths = ["/usr/bin/tesseract", "/usr/local/bin/tesseract"]
        for p in paths:
            if Path(p).exists():
                return p
    
    return None

def find_poppler():
    """Найти Poppler в системе"""
    # 1. Переменная окружения
    env = os.environ.get('POPPLER_PATH')
    if env and Path(env).exists():
        return env
    
    # 2. Найти pdftoppm в PATH
    pdftoppm = shutil.which("pdftoppm")
    if pdftoppm:
        return str(Path(pdftoppm).parent)
    
    # 3. Стандартные пути Windows
    if sys.platform == "win32":
        paths = [
            r"C:\Program Files\poppler-25.07.0\Library\bin",
            r"C:\Program Files\poppler-24.08.0\Library\bin",
            r"C:\poppler\Library\bin",
        ]
        for p in paths:
            if Path(p).exists():
                return p
    
    return None

def extract_text(file_path):
    """Универсальное извлечение текста"""
    # Находим пути
    tesseract_path = find_tesseract()
    poppler_path = find_poppler()
    
    if not tesseract_path:
        print("  Tesseract не найден")
        return ""
    
    # Настраиваем Tesseract
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    # Конфиг OCR
    config = "--oem 3 --psm 4 -l rus+eng"
    
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"  Файл не найден: {file_path}")
        return ""
    
    try:
        if file_path.suffix.lower() == '.pdf':
            # Обработка PDF
            if poppler_path:
                images = convert_from_path(str(file_path), poppler_path=poppler_path)
            else:
                images = convert_from_path(str(file_path))
            
            text = "\n".join(pytesseract.image_to_string(img, config=config) for img in images)
        else:
            # Обработка изображений
            text = pytesseract.image_to_string(Image.open(str(file_path)), config=config)
        
        return text
        
    except Exception as e:
        print(f"  Ошибка OCR: {e}")
        return ""