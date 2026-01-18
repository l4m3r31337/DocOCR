#!/usr/bin/env python3
"""
Точка входа для запуска как модуля: python -m src
"""
import sys
import os


# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(__file__))

from src.cli import main

if __name__ == "__main__":
    main()