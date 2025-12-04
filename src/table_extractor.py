import re
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TableRow:
    """Структура строки таблицы"""
    row_number: int
    product_name: str
    quantity: float
    price: float
    unit: Optional[str] = None
    product_code: Optional[str] = None
    total_without_nds: Optional[float] = None


class TableExtractor:
    """
    Извлекатель табличных данных из документов.
    Рабочая версия.
    """

    def __init__(self):
        logger.info("Инициализирован извлекатель табличных данных")

    def extract_table(self, text: str, doc_type: str) -> List[Dict[str, Any]]:
        """
        Основной метод извлечения табличных данных
        """
        lines = text.split('\n')
        table_rows = []
        row_counter = 1

        for i, line in enumerate(lines):
            line_clean = line.strip()

            # Пропускаем пустые и короткие строки
            if not line_clean or len(line_clean) < 10:
                continue

            # Останавливаемся на итогах
            if any(stop_word in line_clean.lower() for stop_word in
                   ['всего к оплате', 'итого', 'всего по накладной']):
                break

            # Парсим строку ДАЖЕ если не уверены, что это товар
            row_data = self._parse_table_row(line_clean, row_counter)
            if row_data:
                table_rows.append(row_data)
                row_counter += 1

        return self._convert_to_dicts(table_rows)

    def _parse_table_row(self, line: str, row_num: int) -> Optional[TableRow]:
        """Парсинг строки таблицы"""
        try:
            # Очищаем строку от мусора
            clean_line = self._clean_line(line)

            # Паттерн 1: "Пирог тирольский с вишней 796 шт 355,000 152,54"
            pattern1 = r'([А-Яа-яЁё][А-Яа-яЁё\s\-"]+?)\s+(\d+)\s+([а-я]+)\s+([\d\s,]+)\s+([\d\s,]+)'
            match1 = re.match(pattern1, clean_line)

            if match1:
                quantity = self._parse_number(match1.group(4))
                price = self._parse_number(match1.group(5))

                if quantity > 0 and price > 0 and quantity < 10000 and price < 10000:
                    return TableRow(
                        row_number=row_num,
                        product_name=self._clean_product_name(match1.group(1)),
                        product_code=match1.group(2),
                        unit=match1.group(3),
                        quantity=quantity,
                        price=price,
                        total_without_nds=quantity * price
                    )

            # Паттерн 2: "Пирог тирольский с вишней 355,000 152,54"
            pattern2 = r'([А-Яа-яЁё][А-Яа-яЁё\s\-"]+?)\s+([\d\s,]+)\s+([\d\s,]+)'
            match2 = re.match(pattern2, clean_line)

            if match2:
                quantity = self._parse_number(match2.group(2))
                price = self._parse_number(match2.group(3))

                if quantity > 0 and price > 0 and quantity < 10000 and price < 10000:
                    return TableRow(
                        row_number=row_num,
                        product_name=self._clean_product_name(match2.group(1)),
                        quantity=quantity,
                        price=price,
                        total_without_nds=quantity * price
                    )

            # Паттерн 3: Упрощенный - ищем любые два числа
            # Находим название (все до первого числа)
            name_match = re.match(r'^([^\d]+)', clean_line)
            if name_match:
                product_name = name_match.group(1).strip()

                # Находим все числа в строке
                numbers = re.findall(r'[\d\s,]+\.?\d*', clean_line)

                if len(numbers) >= 2:
                    # Пробуем последние два числа как количество и цену
                    for i in range(len(numbers) - 1):
                        quantity = self._parse_number(numbers[i])
                        price = self._parse_number(numbers[i + 1])

                        # Проверяем на реальные значения
                        if 0.1 < quantity < 10000 and 0.1 < price < 10000:
                            return TableRow(
                                row_number=row_num,
                                product_name=self._clean_product_name(product_name),
                                quantity=quantity,
                                price=price,
                                total_without_nds=quantity * price
                            )

        except Exception as e:
            logger.debug(f"Ошибка парсинга строки: {e}")

        return None

    def _clean_line(self, line: str) -> str:
        """Очистка строки"""
        cleaned = line.strip()
        # Убираем специальные символы
        cleaned = re.sub(r'[|—\-«»„"\']', ' ', cleaned)
        # Убираем лишние пробелы
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned

    def _clean_product_name(self, name: str) -> str:
        """Очистка названия товара"""
        cleaned = name.strip()
        # Убираем цифры и мусор в конце
        cleaned = re.sub(r'\s+\d+.*$', '', cleaned)
        # Убираем единицы измерения
        cleaned = re.sub(r'\s+(шт|кг|г|л|мл|штук)\s*$', '', cleaned, flags=re.IGNORECASE)
        # Убираем лишние пробелы
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned

    def _parse_number(self, number_str: str) -> float:
        """Парсинг числа"""
        try:
            cleaned = number_str.replace(' ', '').replace(',', '.')
            return float(cleaned)
        except:
            return 0.0

    def _convert_to_dicts(self, table_rows: List[TableRow]) -> List[Dict[str, Any]]:
        """Преобразование в словари"""
        result = []
        for row in table_rows:
            row_dict = {
                "row_number": row.row_number,
                "product_name": row.product_name,
                "quantity": round(row.quantity, 3),
                "price": round(row.price, 2),
                "total": round(row.total_without_nds or row.quantity * row.price, 2)
            }

            if row.unit:
                row_dict["unit"] = row.unit
            if row.product_code:
                row_dict["product_code"] = row.product_code
            if row.total_without_nds:
                row_dict["total_without_nds"] = round(row.total_without_nds, 2)

            result.append(row_dict)

        return result


# Глобальный экземпляр
table_extractor = TableExtractor()


def extract_table_data(text: str, doc_type: str) -> List[Dict[str, Any]]:
    """Основная функция"""
    return table_extractor.extract_table(text, doc_type)