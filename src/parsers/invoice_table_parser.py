import re
from typing import Dict, List, Any
from decimal import Decimal, ROUND_HALF_UP
import logging
from validator import _validate_arithmetic_checks

logger = logging.getLogger(__name__)


def parse_decimal(value: str) -> float:
    """Парсит строку в десятичное число"""
    if not value:
        return 0.0
    value = str(value).replace(" ", "").replace(",", ".")
    num = re.findall(r"\d+(?:\.\d+)?", value)
    if not num:
        return 0.0
    return float(Decimal(num[0]).quantize(Decimal("0.00"), rounding=ROUND_HALF_UP))


def parse_quantity(value: str) -> int:
    """Парсит количество товара"""
    if not value:
        return 0
    value = str(value).replace(" ", "").replace(",", ".")
    num = re.findall(r"\d+(?:\.\d+)?", value)
    if not num:
        return 0
    quantity_decimal = Decimal(num[0])
    return int(quantity_decimal.quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def _parse_invoice_table(self, table_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Парсинг табличной части счёта-фактуры"""
    logger.info("Запущен парсер таблицы счёта-фактуры")
    
    table_items = []
    line_no = 1

    for row in table_data:
        # Используем доступные ключи (обычно "0", "1", "2" и т.д. для таблиц camelot)
        name = str(row.get("0", "")).strip()

        # Пропускаем пустые строки и служебные строки
        if not name or name.startswith("Всего") or name.startswith("Итого") or name.isdigit():
            continue

        # Проверяем, что в строке есть числовые данные (количество)
        quantity_str = str(row.get("3", ""))
        if not re.search(r"\d+[,.\d+]", quantity_str):
            continue

        # Извлекаем данные из таблицы
        quantity = parse_quantity(quantity_str)
        price = parse_decimal(str(row.get("4", "")))
        price_wo_vat = parse_decimal(str(row.get("5", "")))
        vat_rate = str(row.get("7", "")).strip()
        vat_amount = parse_decimal(str(row.get("8", "")))
        total_with_vat = parse_decimal(str(row.get("9", "")))

        # Если ставка НДС не указана, определяем по сумме НДС
        if not vat_rate and vat_amount > 0 and price_wo_vat > 0:
            try:
                calculated_rate = (vat_amount / price_wo_vat) * 100
                if abs(calculated_rate - 18.0) < 0.1:
                    vat_rate = "18%"
                elif abs(calculated_rate - 20.0) < 0.1:
                    vat_rate = "20%"
                elif abs(calculated_rate - 10.0) < 0.1:
                    vat_rate = "10%"
                else:
                    vat_rate = f"{calculated_rate:.0f}%"
            except:
                vat_rate = "Без НДС"

        table_items.append({
            "line_number": line_no,
            "product_name": name,
            "unit": str(row.get("2", "")).strip(),
            "quantity": quantity,
            "price": price,
            "total_without_vat": price_wo_vat,
            "total_with_vat": total_with_vat,
            "vat_rate": vat_rate,
            "vat_amount": vat_amount
        })

        line_no += 1

    # Находим итоговую строку
    totals = {"total_without_vat": 0.0, "total_vat": 0.0, "total_with_vat": 0.0}
    
    if table_data:
        # Ищем итоговую строку (обычно последняя или предпоследняя)
        for i in range(len(table_data) - 1, max(-1, len(table_data) - 5), -1):
            row = table_data[i]
            name = str(row.get("0", "")).strip().lower()
            
            if "всего" in name or "итого" in name:
                totals = {
                    "total_without_vat": parse_decimal(str(row.get("5", ""))),
                    "total_vat": parse_decimal(str(row.get("8", ""))),
                    "total_with_vat": parse_decimal(str(row.get("9", "")))
                }
                break
        else:
            # Если не нашли явную итоговую строку, вычисляем сами
            totals = {
                "total_without_vat": sum(item["total_without_vat"] for item in table_items),
                "total_vat": sum(item["vat_amount"] for item in table_items),
                "total_with_vat": sum(item["total_with_vat"] for item in table_items)
            }

    # Проверка нумерации строк
    line_numbering_ok = True
    expected_line_numbers = list(range(1, len(table_items) + 1))
    actual_line_numbers = [item["line_number"] for item in table_items]
    
    if expected_line_numbers != actual_line_numbers:
        line_numbering_ok = False

    # Арифметическая проверка
    arithmetic_check = _validate_arithmetic_checks(table_items)

    result = {
        "vat_rate": table_items[0]["vat_rate"] if table_items else "Без НДС",
        "table_items": table_items,
        "totals": totals,
        "validation_results": {
            "line_numbering_check": {
                "status": "PASSED" if line_numbering_ok else "FAILED",
            },
            "arithmetic_check": {
                "status": "PASSED" if arithmetic_check["is_valid"] else "FAILED"
                } | ({"details": arithmetic_check, "message": f"Найдено {len(arithmetic_check['errors'])} ошибок"} 
                    if not arithmetic_check["is_valid"] else {})
        }
    }

    return result