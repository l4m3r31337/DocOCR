import re
import json
import logging
from typing import Dict, List, Any
from datetime import datetime
import os

logger = logging.getLogger(__name__)

try:
    from .table_extractor import extract_table_data
except ImportError:
    from table_extractor import extract_table_data


class DataParser:
    """Парсер документов"""

    def __init__(self):
        logger.info("Инициализирован парсер данных")

    def parse_document(self, text: str, doc_type: str) -> Dict[str, Any]:
        """Основной метод"""
        try:
            result = {
                "document_type": doc_type,
                "header": self._parse_header(text, doc_type),
                "table_data": extract_table_data(text, doc_type),
                "totals": self._parse_totals(text, doc_type),
                "metadata": {
                    "parsing_date": datetime.now().isoformat(),
                    "text_length": len(text)
                }
            }

            return result

        except Exception as e:
            logger.error(f"Ошибка парсинга: {e}")
            return self._create_error_result(doc_type, str(e))

    def _parse_header(self, text: str, doc_type: str) -> Dict[str, Any]:
        """Парсинг шапки"""
        header = {}

        # Номер документа
        if doc_type == "СЧЕТ_ФАКТУРА":
            match = re.search(r'Счет-фактура\s*[№N]?\s*(\d+)', text)
        elif doc_type == "ТОРГ-12":
            match = re.search(r'ТОРГ-12\s*[№N]?\s*(\d+)', text) or re.search(r'Накладная\s*[№N]?\s*(\d+)', text)
        elif doc_type == "УПД":
            match = re.search(r'УПД\s*[№N]?\s*(\d+)', text) or re.search(r'Счет-фактура\s*[№N]?\s*(\d+)', text)
        else:
            match = re.search(r'[№N]\s*(\d{4,})', text)

        header["doc_number"] = match.group(1) if match else None

        # Дата документа - ИЗБЕГАЕМ ДАТУ ПОСТАНОВЛЕНИЯ
        # Ищем "от" и дату, но проверяем контекст
        date_matches = list(re.finditer(r'от\s*(\d{1,2}\s+[а-я]+\s+\d{4}|\d{1,2}\.\d{1,2}\.\d{4})', text))

        for date_match in date_matches:
            date_str = date_match.group(1)
            # Проверяем, не дата ли это постановления
            start = max(0, date_match.start() - 100)
            end = min(len(text), date_match.end() + 100)
            context = text[start:end].lower()

            if 'постановл' not in context and 'правительств' not in context:
                header["doc_date"] = re.sub(r'\s+г\.?\s*$', '', date_str)
                break

        # Продавец/Поставщик
        if doc_type == "ТОРГ-12":
            match = re.search(r'Поставщик[^\n]*\n([^\n]+)', text)
            if match:
                header["supplier"] = match.group(1).strip().split(',')[0]
        else:
            match = re.search(r'Продавец[:\s]*([^\n]+)', text, re.IGNORECASE)
            if match:
                header["seller"] = match.group(1).strip()

        # Покупатель/Грузополучатель
        if doc_type == "ТОРГ-12":
            match = re.search(r'Грузополучатель[^\n]*\n([^\n]+)', text)
            if match:
                header["receiver"] = match.group(1).strip().split(',')[0]
        else:
            match = re.search(r'Покупатель[:\s]*([^\n]+)', text, re.IGNORECASE)
            if match:
                header["buyer"] = match.group(1).strip()

        # ИНН/КПП
        match = re.search(r'ИНН[:\s/]*(\d{10,12})', text, re.IGNORECASE)
        if match:
            header["inn"] = match.group(1)

        # Статус УПД
        if doc_type == "УПД":
            match = re.search(r'Статус[:\s]*\[?(\d)\]?', text)
            if match:
                header["status"] = match.group(1)

        return header

    def _parse_totals(self, text: str, doc_type: str) -> Dict[str, Any]:
        """Парсинг итогов"""
        totals = {}

        match = re.search(r'Всего к оплате[:\s]*([\d\s,]+)', text, re.IGNORECASE)
        if not match:
            match = re.search(r'Всего[:\s]*([\d\s,]+)', text, re.IGNORECASE)

        if match:
            totals["total_amount"] = self._parse_number(match.group(1))

        return totals

    def _parse_number(self, number_str: str) -> float:
        """Парсинг числа"""
        try:
            return float(number_str.replace(' ', '').replace(',', '.'))
        except:
            return 0.0

    def _create_error_result(self, doc_type: str, error: str) -> Dict[str, Any]:
        """Результат с ошибкой"""
        return {
            "document_type": doc_type,
            "header": {},
            "table_data": [],
            "totals": {},
            "metadata": {
                "parsing_date": datetime.now().isoformat(),
                "error": error
            }
        }


data_parser = DataParser()


def parse_document_data(text: str, doc_type: str) -> Dict[str, Any]:
    return data_parser.parse_document(text, doc_type)


def save_to_json(data: Dict[str, Any], filename: str) -> bool:
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"JSON сохранен: {filename}")
        return True
    except Exception as e:
        logger.error(f"Ошибка сохранения JSON: {e}")
        return False