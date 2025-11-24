import re
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class DataParser:
    """
    Парсер для структурирования данных из распознанного текста
    """

    def __init__(self):
        logger.info("Инициализирован парсер данных")

    def parse_document(self, text: str, doc_type: str) -> Dict[str, Any]:
        """
        Основной метод парсинга документа
        """
        try:
            result = {
                "document_type": doc_type,
                "header": self._parse_header(text, doc_type),
                "table_data": self._parse_table(text, doc_type),
                "totals": self._parse_totals(text, doc_type),
                "metadata": {
                    "parsing_date": datetime.now().isoformat(),
                    "text_length": len(text),
                    "confidence": "medium"
                }
            }
            return result

        except Exception as e:
            logger.error(f"Ошибка парсинга: {e}")
            return self._create_error_result(doc_type, str(e))

    def _parse_header(self, text: str, doc_type: str) -> Dict[str, Any]:
        """Парсинг шапки документа"""
        header = {}

        # Номер документа
        if doc_type == "СЧЕТ_ФАКТУРА":
            doc_match = re.search(r'Счет-фактура №\s*(\S+)', text)
        elif doc_type == "ТОРГ-12":
            doc_match = re.search(r'ТОРГ-12\s*№\s*(\S+)', text)
        elif doc_type == "УПД":
            doc_match = re.search(r'УПД\s*№\s*(\S+)', text)
        else:
            doc_match = re.search(r'№\s*(\S+)', text)

        if doc_match:
            header["doc_number"] = doc_match.group(1)

        # Дата документа
        date_match = re.search(r'от\s*(\d{1,2}\s*[а-я]+\s*\d{4}|\d{1,2}\.\d{1,2}\.\d{4})', text)
        if date_match:
            header["doc_date"] = date_match.group(1)

        # Продавец/Поставщик
        seller_match = re.search(r'Продавец[:]?\s*([^\n]+)', text)
        if seller_match:
            header["seller"] = seller_match.group(1).strip()
        else:
            supplier_match = re.search(r'Поставщик[:]?\s*([^\n]+)', text)
            if supplier_match:
                header["supplier"] = supplier_match.group(1).strip()

        # ИНН/КПП
        inn_match = re.search(r'ИНН/КПП\s*(\d{10,12})[/\s]*(\d{9})', text)
        if inn_match:
            header["inn"] = inn_match.group(1)
            header["kpp"] = inn_match.group(2)

        # Покупатель/Грузополучатель
        buyer_match = re.search(r'Покупатель[:]?\s*([^\n]+)', text)
        if buyer_match:
            header["buyer"] = buyer_match.group(1).strip()

        return header

    def _parse_table(self, text: str, doc_type: str) -> List[Dict[str, Any]]:
        """Парсинг табличной части"""
        table_data = []
        lines = text.split('\n')

        # Ищем начало таблицы
        start_index = -1
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in ['наименование', 'товар', 'номенклатура']):
                start_index = i + 1
                break

        if start_index == -1:
            return table_data

        # Парсим строки таблицы
        row_count = 0
        for i in range(start_index, min(start_index + 50, len(lines))):
            line = lines[i].strip()
            if not line or len(line) < 10:
                continue

            # Останавливаемся на итогах
            if any(stop_word in line.lower() for stop_word in ['всего', 'итого', 'всего к оплате']):
                break

            # Парсим строку
            row_data = self._parse_table_row(line)
            if row_data:
                row_count += 1
                row_data["row_number"] = row_count
                table_data.append(row_data)

        return table_data

    def _parse_table_row(self, line: str) -> Optional[Dict[str, Any]]:
        """Парсинг одной строки таблицы"""
        try:
            # Простой парсинг - ищем паттерн "название число число число"
            # Пример: "Пирог тирольский с вишней 796 шт 355,000 152,54"

            # Ищем название товара (все до первого числа)
            name_match = re.match(r'^([^\d]+?)\s+(\d+)\s+([^\d]+)\s+([\d,]+)\s+([\d,]+)', line)
            if name_match:
                return {
                    "product_name": name_match.group(1).strip(),
                    "product_code": name_match.group(2),
                    "unit": name_match.group(3).strip(),
                    "quantity": self._clean_number(name_match.group(4)),
                    "price": self._clean_number(name_match.group(5))
                }

            # Альтернативный паттерн
            alt_match = re.search(r'([А-Яа-яЁё\s"]+)\s+(\d+)\s+([^\d]+)\s+([\d,]+)', line)
            if alt_match:
                return {
                    "product_name": alt_match.group(1).strip(),
                    "product_code": alt_match.group(2),
                    "unit": alt_match.group(3).strip(),
                    "quantity": self._clean_number(alt_match.group(4))
                }

        except Exception as e:
            logger.debug(f"Ошибка парсинга строки: {e}")

        return None

    def _parse_totals(self, text: str, doc_type: str) -> Dict[str, Any]:
        """Парсинг итоговых сумм"""
        totals = {}

        # Ищем итоговые суммы
        total_match = re.search(r'Всего к оплате\s*([\d\s,]+)\s*x\s*([\d\s,]+)\s*([\d\s,]+)', text)
        if total_match:
            totals["total_without_nds"] = self._clean_number(total_match.group(1))
            totals["total_nds"] = self._clean_number(total_match.group(2))
            totals["total_with_nds"] = self._clean_number(total_match.group(3))

        return totals

    def _clean_number(self, number_str: str) -> float:
        """Очистка числа от пробелов и замена запятых"""
        try:
            cleaned = number_str.replace(' ', '').replace(',', '.')
            return float(cleaned)
        except:
            return 0.0

    def _create_error_result(self, doc_type: str, error: str) -> Dict[str, Any]:
        """Создание результата с ошибкой"""
        return {
            "document_type": doc_type,
            "header": {},
            "table_data": [],
            "totals": {},
            "metadata": {
                "parsing_date": datetime.now().isoformat(),
                "error": error,
                "confidence": "low"
            }
        }


# Создаем экземпляр для использования
data_parser = DataParser()


def parse_document_data(text: str, doc_type: str) -> Dict[str, Any]:
    """
    Основная функция для парсинга документа
    """
    return data_parser.parse_document(text, doc_type)


def save_to_json(data: Dict[str, Any], filename: str):
    """
    Сохранение данных в JSON файл
    """
    try:
        # Создаем папку если ее нет
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ JSON сохранен: {filename}")
        return True

    except Exception as e:
        print(f"❌ Ошибка сохранения JSON: {e}")
        return False