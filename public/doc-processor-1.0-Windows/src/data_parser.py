import json
import re
from typing import Dict, Any
import logging
from parsers import torg_12_header_parser, upd_header_parser, invoice_header_parser

logger = logging.getLogger("DocProcessor")


class DocumentParser:
    def __init__(self):
        self.parsers = {
            'СЧЕТ_ФАКТУРА': self._parse_invoice_header, 
            'УПД': self._parse_upd_header,
            'ТОРГ-12': self._parse_torg12_header
        }

    def _clean_text(self, text: str) -> str:
        """Очищает текст от лишних пробелов и символов"""
        if not text:
            return ""
        return text.replace('\n', ' ').replace('\r', ' ').strip()

    def _extract_inn_kpp(self, text: str, prefix: str) -> Dict[str, str]:
        """Извлекает ИНН и КПП из текста"""
        result = {"inn": "", "kpp": ""}

        # Паттерн для ИНН/КПП
        patterns = [
            rf'{prefix}.*?ИНН\s*[:/]?\s*(\d{{10}}|\d{{12}}).*?КПП\s*[:/]?\s*(\d{{9}})',
            rf'ИНН[/\\]КПП\s*{prefix}[:\s]*(\d+)[/\s]*(\d+)',
            rf'{prefix}.*?ИНН\s*(\d{{10}}|\d{{12}}).*?КПП\s*(\d{{9}})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                result["inn"] = match.group(1)
                result["kpp"] = match.group(2) if len(
                    match.groups()) > 1 else ""
                break

        return result

    def parse(self, document_type: str, text: str) -> Dict[str, Any]:
        """
        Основной метод парсинга документа (только шапка)

        Args:
            document_type: Тип документа (определён классификатором)
            text: Текст документа для парсинга

        Returns:
            Словарь с распарсенными данными из шапки
        """
        logger.debug(f"Парсим документ типа: {document_type}")

        if document_type not in self.parsers:
            logger.error(f"Неизвестный тип документа: {document_type}")
            raise ValueError(f"Парсер для типа {document_type} не реализован")

        return self.parsers[document_type](text)

    def _parse_invoice_header(self, text: str) -> Dict[str, Any]:
        return invoice_header_parser._parse_invoice_header(self, text)

    def _parse_upd_header(self, text: str) -> Dict[str, Any]:
        return upd_header_parser._parse_upd_header(self, text)

    def _parse_torg12_header(self, text: str) -> Dict[str, Any]:
        return torg_12_header_parser._parse_torg12_header(self, text)

    def save_to_json(self, data: Dict[str, Any], filename: str) -> None:
        """Сохранение результата в JSON файл"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug(f"Данные сохранены в файл: {filename}")
        except Exception as e:
            logger.error(f"Ошибка сохранения в файл {filename}: {e}")
            raise


# Функция для использования в пайплайне
def parse_document(document_type: str, text: str) -> Dict[str, Any]:
    """
    Основная функция парсинга шапки документа

    Args:
        document_type: Тип документа от классификатора
        text: Текст документа

    Returns:
        Словарь с распарсенными данными из шапки
    """
    parser = DocumentParser()
    return parser.parse(document_type, text)
