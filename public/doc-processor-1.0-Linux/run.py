#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Кросс-платформенный запускатор для Windows и Linux
"""
import sys
import os

def is_windows():
    return sys.platform.startswith('win')

def setup_environment():
    """Настройка окружения для разных ОС"""
    
    # Настройка кодировки
    if sys.version_info >= (3, 7):
        # UTF-8 по умолчанию в Python 3.7+
        pass
    else:
        # Для старых версий
        try:
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
        except:
            pass
    
    # Включение цветов в Windows
    if is_windows():
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except:
            pass

def main():
    """Основная функция запуска"""
    setup_environment()
    
    # Добавляем текущую папку в путь для импорта
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(current_dir, 'src'))
    
    try:
        from src.cli import main as cli_main
        return cli_main()
    except ImportError:
        print("Ошибка: Не удалось найти модули программы.")
        print("Установите зависимости: pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())