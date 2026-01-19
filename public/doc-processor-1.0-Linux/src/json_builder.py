import json
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger("DocProcessor")


def save_to_json(data: Dict[str, Any], filename: str) -> str:
    """
    Сохранение результата в JSON файл
    
    Args:
        data: Данные для сохранения
        filename: Полный путь к файлу
        
    Returns:
        str: Путь к сохраненному файлу
    """
    try:
         # Создаем директорию, если ее нет
        # Используем Path для корректной обработки путей
        output_path = Path(filename)
        
        # Создаем родительскую директорию, если она указана
        if output_path.parent:  # Проверяем, есть ли родительская директория
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.debug(f"Данные сохранены в файл: {filename}")
        return filename
        
    except Exception as e:
        logger.error(f"Ошибка сохранения в файл {filename}: {e}")
        raise