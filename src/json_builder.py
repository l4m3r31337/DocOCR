import json
import os
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


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
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Данные сохранены в файл: {filename}")
        return filename
        
    except Exception as e:
        logger.error(f"Ошибка сохранения в файл {filename}: {e}")
        raise