"""
Конфигурация путей к внешним зависимостям
"""
import os
import sys
from pathlib import Path
import platform


class Config:
    """Класс для управления конфигурацией путей"""
    
    def __init__(self):
        self.system = platform.system()
        self._find_tesseract()
        self._find_poppler()
    
    def _find_tesseract(self):
        """Поиск Tesseract в системе"""
        # Возможные пути для Windows
        windows_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Tesseract-OCR\tesseract.exe",
        ]
        
        # Возможные пути для Linux/macOS
        unix_paths = [
            "/usr/bin/tesseract",
            "/usr/local/bin/tesseract",
            "/opt/homebrew/bin/tesseract",  # macOS Homebrew
        ]
        
        # Сначала проверяем переменную окружения
        tesseract_cmd = os.environ.get('TESSERACT_CMD')
        if tesseract_cmd and Path(tesseract_cmd).exists():
            self.tesseract_path = tesseract_cmd
            print(f"✓ Tesseract найден через переменную окружения: {self.tesseract_path}")
            return
        
        # Проверяем системные пути в зависимости от ОС
        paths_to_check = windows_paths if self.system == "Windows" else unix_paths
        
        for path in paths_to_check:
            if Path(path).exists():
                self.tesseract_path = path
                print(f"✓ Tesseract найден: {self.tesseract_path}")
                return
        
        # Проверяем PATH
        try:
            import shutil
            tesseract_path = shutil.which("tesseract")
            if tesseract_path:
                self.tesseract_path = tesseract_path
                print(f"✓ Tesseract найден в PATH: {self.tesseract_path}")
                return
        except:
            pass
        
        # Не найден
        self.tesseract_path = None
        print("⚠️  Tesseract не найден. Пожалуйста, установите его.")
        self._print_installation_instructions()
    
    def _find_poppler(self):
        """Поиск Poppler в системе"""
        if self.system == "Windows":
            # Возможные пути для Windows
            windows_poppler_paths = [
                r"C:\Program Files\poppler-25.07.0\Library\bin",
                r"C:\Program Files\poppler-24.08.0\Library\bin",
                r"C:\Program Files\poppler-23.11.0\Library\bin",
                r"C:\Program Files\poppler\Library\bin",
            ]
            
            for path in windows_poppler_paths:
                if Path(path).exists():
                    self.poppler_path = path
                    print(f"✓ Poppler найден: {self.poppler_path}")
                    return
            
            # Пробуем найти в PATH
            poppler_bin = os.environ.get('POPPLER_PATH')
            if poppler_bin and Path(poppler_bin).exists():
                self.poppler_path = poppler_bin
                print(f"✓ Poppler найден через переменную окружения: {self.poppler_path}")
                return
        
        # Для Linux/macOS Poppler обычно в PATH
        self.poppler_path = None
        if self.system != "Windows":
            print("ℹ️  Poppler не требуется для Linux/macOS (используется системный)")
    
    def _print_installation_instructions(self):
        """Вывод инструкций по установке"""
        print("\n" + "="*60)
        print("📦 ИНСТРУКЦИЯ ПО УСТАНОВКЕ ЗАВИСИМОСТЕЙ")
        print("="*60)
        
        if self.system == "Windows":
            print("Для Windows:")
            print("1. Установите Tesseract OCR:")
            print("   Скачайте с: https://github.com/UB-Mannheim/tesseract/wiki")
            print("   Убедитесь, что выбрали русский язык (rus) при установке")
            print("\n2. Установите Poppler:")
            print("   Скачайте с: https://github.com/oschwartz10612/poppler-windows/releases/")
            print("   Распакуйте в C:\\Program Files\\poppler-XX.XX.X\\")
        elif self.system == "Linux":
            print("Для Linux (Ubuntu/Debian):")
            print("  sudo apt update && sudo apt install tesseract-ocr tesseract-ocr-rus poppler-utils")
        elif self.system == "Darwin":  # macOS
            print("Для macOS:")
            print("  brew install tesseract tesseract-lang poppler")
        
        print("\nИли укажите пути вручную через переменные окружения:")
        print("  Windows: set TESSERACT_CMD=C:\\Path\\To\\tesseract.exe")
        print("           set POPPLER_PATH=C:\\Path\\To\\poppler\\bin")
        print("  Linux/macOS: export TESSERACT_CMD=/usr/bin/tesseract")
        print("="*60)
    
    def is_ready(self) -> bool:
        """Проверка, все ли зависимости найдены"""
        if self.system == "Windows":
            return self.tesseract_path is not None and self.poppler_path is not None
        else:
            return self.tesseract_path is not None


# Глобальный экземпляр конфигурации
config = Config()


def check_dependencies():
    """Функция для проверки зависимостей при запуске"""
    print("\n🔍 ПРОВЕРКА ЗАВИСИМОСТЕЙ")
    print("-" * 40)
    
    ready = config.is_ready()
    
    if ready:
        print("✅ Все зависимости найдены")
        print(f"   Tesseract: {config.tesseract_path}")
        if config.poppler_path:
            print(f"   Poppler: {config.poppler_path}")
    else:
        print("❌ Не все зависимости установлены")
    
    print("-" * 40)
    return ready