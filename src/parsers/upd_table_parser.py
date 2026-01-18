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


def _parse_upd_table(self, table_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Парсинг табличной части УПД"""
    logger.info("Запущен парсер таблицы УПД")
    
    table_items = []
    line_counter = 1
    
    for row in table_data:
        # Получаем значения из нужных колонок для УПД
        col1 = row.get("1", "")
        col2 = row.get("2", "")
        col3 = row.get("3", "")
        col4 = row.get("4", "")
        col5 = row.get("5", "")
        col6 = row.get("6", "")
        col7 = row.get("7", "")
        col8 = row.get("8", "")
        col9 = row.get("9", "")
        col10 = row.get("10", "")
        col11 = row.get("11", "")
        col12 = row.get("12", "")
        col13 = row.get("13", "")
        col14 = row.get("14", "")
        
        # Пропускаем строки без названия товара
        if not col2 or col2 == "":
            continue
        
        # Пропускаем заголовки таблицы
        if (isinstance(col2, str) and 
            any(keyword in col2.lower() for keyword in ["наименование", "товара", "описание"])):
            continue
        
        # Пропускаем строки с номерами колонок
        if col2 in ["1", "2", "3", "А", "Б", "код"]:
            continue
        
        # Пропускаем итоговые строки
        if isinstance(col2, str) and ("итого" in col2.lower() or "всего" in col2.lower()):
            continue
        
        # Извлекаем название товара
        product_name = str(col2).strip().replace('\n', ' ').replace('\r', ' ').strip()
        
        # Извлекаем данные
        quantity = parse_number(col5)
        price = parse_number(col6)
        
        # Обрабатываем стоимость без налога
        total_without_vat = Decimal('0')
        if col7 and str(col7).strip():
            price_str = str(col7).replace("без", "").strip()
            total_without_vat = parse_number(price_str)
        
        # Обрабатываем сумму налога
        vat_amount = parse_number(col10)
        
        # Обрабатываем ставку НДС
        vat_rate = "Без НДС"
        if col9 and str(col9).strip():
            vat_rate_str = str(col9).strip()
            if "%" in vat_rate_str:
                vat_rate = vat_rate_str
        
        # Обрабатываем стоимость с налогом
        total_with_vat = Decimal('0')
        if col11 and str(col11).strip():
            total_str = str(col11).replace("--", "").strip()
            total_with_vat = parse_number(total_str)
        
        # Вычисляем недостающие значения
        if total_with_vat == 0 and total_without_vat > 0 and vat_amount > 0:
            total_with_vat = total_without_vat + vat_amount
        
        if vat_amount == 0 and vat_rate != "Без НДС" and total_without_vat > 0:
            try:
                rate_percent = Decimal(vat_rate.replace("%", "")) / Decimal('100')
                vat_amount = total_without_vat * rate_percent
                total_with_vat = total_without_vat + vat_amount
            except:
                pass
        
        if total_without_vat == 0 and total_with_vat > 0 and vat_amount > 0:
            total_without_vat = total_with_vat - vat_amount
        
        # Округляем значения
        def round_decimal(value: Decimal) -> Decimal:
            return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        unit = str(col4).strip() if col4 and str(col4).strip() != "nan" else "шт"
        if not unit or unit == "":
            unit = "шт"
        
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
            col2 = row.get("2", "")
            
            if isinstance(col2, str) and "всего к оплате" in col2.lower():
                totals = {
                    "total_without_vat": float(parse_number(row.get("7", "0"))),
                    "total_vat": float(parse_number(row.get("10", "0"))),
                    "total_with_vat": float(parse_number(row.get("11", "0")))
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