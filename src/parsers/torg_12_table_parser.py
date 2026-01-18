import re
from typing import Dict, List, Any, Optional
from decimal import Decimal, ROUND_HALF_UP, DecimalException
import math
import logging
from validator import _validate_arithmetic_checks

logger = logging.getLogger(__name__)


def parse_number(value: Any) -> Decimal:
    """Преобразует строку с числом в Decimal"""
    if value is None or value == "" or (isinstance(value, float) and math.isnan(value)):
        return Decimal('0')
    
    if isinstance(value, (int, float, Decimal)):
        return Decimal(str(value))
    
    str_value = str(value).strip()
    if not str_value:
        return Decimal('0')
    
    str_value = str_value.replace(',', '.')
    str_value = re.sub(r'[^\d\s.-]', '', str_value)
    
    if not str_value or str_value == '-':
        return Decimal('0')
    
    try:
        str_value = str_value.replace(' ', '')
        return Decimal(str_value)
    except:
        return Decimal('0')


def extract_vat_rate_and_amount(value: str) -> tuple:
    """Извлекает ставку НДС и сумму из строки"""
    if not value:
        return "Без НДС", Decimal('0')
    
    value = str(value).strip()
    
    if "без ндс" in value.lower():
        match = re.search(r'([\d\s,]+(?:\.\d+)?)', value)
        if match:
            amount_str = match.group(1)
            amount = parse_number(amount_str)
            return "Без НДС", amount
        return "Без НДС", Decimal('0')
    
    vat_rate_match = re.search(r'(\d+%)', value)
    vat_rate = "Без НДС"
    
    if vat_rate_match:
        vat_rate = vat_rate_match.group(1)
    
    numbers = re.findall(r'[\d\s,]+(?:\.\d+)?', value)
    amount = Decimal('0')
    
    if numbers:
        amount_str = numbers[0]
        amount = parse_number(amount_str)
    
    return vat_rate, amount


def _parse_torg_12_table(self, table_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Парсинг табличной части ТОРГ-12"""
    logger.info("Запущен парсер таблицы ТОРГ-12")
    
    table_items = []
    line_counter = 1
    
    for row in table_data:
        # Получаем значения из нужных колонок для ТОРГ-12
        col0 = row.get("0", "")
        col1 = row.get("1", "")
        col3 = row.get("3", "")
        col9 = row.get("9", "")
        col10 = row.get("10", "")
        col11 = row.get("11", "")
        col12 = row.get("12", "")
        col13 = row.get("13", "")
        col14 = row.get("14", "")
        
        # Пропускаем строки без названия товара
        if not col1 or col1 == "":
            continue
        
        # Пропускаем заголовки таблицы
        if (isinstance(col1, str) and 
            any(keyword in col1.lower() for keyword in ["товар", "наименование"])):
            continue
        
        # Пропускаем строки с номерами колонок
        if (isinstance(col1, str) and col1.strip() in ["1", "2", "3"]):
            continue
        
        # Пропускаем итоговые строки
        if isinstance(col0, str) and ("итого" in col0.lower() or "всего" in col0.lower()):
            continue
        if isinstance(col1, str) and ("итого" in col1.lower() or "всего" in col1.lower()):
            continue
        
        # Извлекаем номер и название товара из col1
        product_info = str(col1).strip()
        match = re.match(r'^(\d+)\s+(.+)$', product_info)
        if match:
            product_name = match.group(2).strip()
        else:
            product_name = product_info
        
        # Извлекаем базовые данные
        quantity = parse_number(col9)
        price = parse_number(col10)
        total_with_vat = parse_number(col14)
        vat_amount = parse_number(col13)
        
        # Определяем данные о сумме без НДС и ставке НДС
        total_without_vat = Decimal('0')
        vat_rate = "Без НДС"
        
        # Пробуем извлечь данные из col11
        if col11 and str(col11).strip():
            vat_rate_from_col11, amount_from_col11 = extract_vat_rate_and_amount(str(col11))
            if amount_from_col11 > 0:
                total_without_vat = amount_from_col11
            if vat_rate_from_col11 != "Без НДС":
                vat_rate = vat_rate_from_col11
        
        # Если не нашли в col11, пробуем col12
        if total_without_vat == 0 and col12 and str(col12).strip():
            vat_rate_from_col12, amount_from_col12 = extract_vat_rate_and_amount(str(col12))
            if amount_from_col12 > 0:
                total_without_vat = amount_from_col12
            if vat_rate_from_col12 != "Без НДС" and vat_rate == "Без НДС":
                vat_rate = vat_rate_from_col12
        
        # Если ставка НДС все еще не определена, но есть сумма НДС
        if vat_rate == "Без НДС" and vat_amount > 0:
            vat_rate = "18%"
        
        # Если документ без НДС
        if vat_rate == "Без НДС":
            if total_with_vat > 0:
                total_without_vat = total_with_vat
            vat_amount = Decimal('0')
        else:
            # Если есть НДС, но сумма без НДС не найдена
            if total_without_vat == 0 and total_with_vat > 0 and vat_amount > 0:
                total_without_vat = total_with_vat - vat_amount
            # Если сумма НДС не найдена
            elif vat_amount == 0 and total_with_vat > 0 and total_without_vat > 0:
                vat_amount = total_with_vat - total_without_vat
        
        # Если общая сумма не задана
        if total_with_vat == 0 and total_without_vat > 0 and vat_amount > 0:
            total_with_vat = total_without_vat + vat_amount
        
        # Округляем значения
        def round_decimal(value: Decimal) -> Decimal:
            return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        unit = str(col3).strip() if col3 and str(col3).strip() != "nan" else "шт"
        
        if product_name and (float(quantity) > 0 or float(price) > 0):
            table_items.append({
                "line_number": line_counter,
                "product_name": product_name,
                "unit": unit,
                "quantity": float(round_decimal(quantity)),
                "price": float(round_decimal(price)),
                "total_without_vat": float(round_decimal(total_without_vat)),
                "total_with_vat": float(round_decimal(total_with_vat)),
                "vat_rate": vat_rate,
                "vat_amount": float(round_decimal(vat_amount))
            })
            line_counter += 1
    
    # Находим строку с итогами
    totals = {"total_without_vat": 0.0, "total_vat": 0.0, "total_with_vat": 0.0}
    
    if table_data:
        for i in range(len(table_data) - 1, max(0, len(table_data) - 10), -1):
            row = table_data[i]
            col11 = row.get("11", "")
            col13 = row.get("13", "")
            col14 = row.get("14", "")
            
            total_without_vat = parse_number(col11)
            total_vat = parse_number(col13)
            total_with_vat = parse_number(col14)
            
            if total_with_vat > 100000:
                totals = {
                    "total_without_vat": float(total_without_vat),
                    "total_vat": float(total_vat),
                    "total_with_vat": float(total_with_vat)
                }
                break
        else:
            # Вычисляем итоги самостоятельно
            totals = {
                "total_without_vat": sum(item["total_without_vat"] for item in table_items),
                "total_vat": sum(item["vat_amount"] for item in table_items),
                "total_with_vat": sum(item["total_with_vat"] for item in table_items)
            }
    
    # Определяем общую ставку НДС
    vat_rate = "Без НДС"
    if table_items:
        vat_rates = {}
        for item in table_items:
            rate = item.get("vat_rate", "Без НДС")
            if rate and rate != "Без НДС":
                vat_rates[rate] = vat_rates.get(rate, 0) + 1
        
        if vat_rates:
            if "18%" in vat_rates:
                vat_rate = "18%"
            else:
                vat_rate = max(vat_rates.items(), key=lambda x: x[1])[0]
    
    # Валидация
    line_numbering_ok = True
    if table_items:
        expected_numbers = list(range(1, len(table_items) + 1))
        actual_numbers = [item["line_number"] for item in table_items]
        if expected_numbers != actual_numbers:
            line_numbering_ok = False
    
    # Арифметическая проверка
    arithmetic_check = _validate_arithmetic_checks(table_items)
    
    result = {
        "vat_rate": vat_rate,
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