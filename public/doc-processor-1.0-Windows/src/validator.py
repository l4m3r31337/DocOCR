from decimal import Decimal, ROUND_HALF_UP, DecimalException
import re
from typing import Dict, List, Any

def _validate_arithmetic_checks(table_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Универсальная арифметическая проверка данных таблицы для всех типов документов"""
    validation_errors = []
    tolerance = Decimal('0.01')  # Допуск в 1 копейку
    
    for idx, item in enumerate(table_items, 1):
        try:
            # Преобразуем все значения в Decimal для точных вычислений
            quantity = Decimal(str(item["quantity"]))
            price = Decimal(str(item["price"]))
            
            total_without_vat = Decimal(str(item["total_without_vat"]))
            field_name = "total_without_vat"
            
            vat_amount = Decimal(str(item["vat_amount"]))
            total_with_vat = Decimal(str(item["total_with_vat"]))
            vat_rate_str = item.get("vat_rate", "Без НДС")
            
            # Проверка 1: total_with_vat = total_without_vat + vat_amount
            if total_with_vat > 0:
                calculated_total = (total_without_vat + vat_amount).quantize(tolerance, rounding=ROUND_HALF_UP)
                actual_total = total_with_vat.quantize(tolerance, rounding=ROUND_HALF_UP)
                
                if abs(calculated_total - actual_total) > tolerance:
                    validation_errors.append(
                        f"Строка {idx}: Итоговая сумма с НДС не соответствует сумме. "
                        f"Расчет: {total_without_vat} + {vat_amount} = {calculated_total}, в таблице: {actual_total}"
                    )
            
            # Проверка 2: Проверка ставки НДС (только для товаров с НДС)
            if vat_rate_str != "Без НДС" and total_without_vat > 0 and vat_amount > 0:
                # Извлекаем ожидаемую ставку НДС (поддерживает дробные проценты)
                rate_match = re.search(r'(\d+(?:\.\d+)?)%', vat_rate_str)
                if rate_match:
                    expected_rate_percent = Decimal(rate_match.group(1))
                    
                    # Рассчитываем фактическую ставку: (vat_amount / total_without_vat) * 100
                    calculated_rate_percent = (vat_amount / total_without_vat) * Decimal('100')
                    
                    # Проверяем соответствие с учетом допуска (1%)
                    if abs(calculated_rate_percent - expected_rate_percent) > Decimal('1'):
                        validation_errors.append(
                            f"Строка {idx}: Ставка НДС не соответствует расчетной. "
                            f"Ожидалось: {expected_rate_percent}%, расчет: {calculated_rate_percent:.2f}%"
                        )
            
            # Проверка 3: Цена через total_without_vat / quantity
            if total_without_vat > 0 and quantity > 0:
                calculated_price = (total_without_vat / quantity).quantize(tolerance, rounding=ROUND_HALF_UP)
                actual_price = price.quantize(tolerance, rounding=ROUND_HALF_UP)
                
                if abs(calculated_price - actual_price) > tolerance:
                    validation_errors.append(
                        f"Строка {idx}: Цена не соответствует {field_name} / quantity. "
                        f"Расчет: {total_without_vat} / {quantity} = {calculated_price}, в таблице: {actual_price}"
                    )
            
            # Проверка 4: Для товаров без НДС vat_amount должен быть 0
            if vat_rate_str == "Без НДС" and vat_amount != 0:
                validation_errors.append(
                    f"Строка {idx}: Указан НДС для товара без НДС"
                )
            
            # Проверка 5: Для товаров без НДС total_with_vat должен равняться total_without_vat
            if vat_rate_str == "Без НДС" and total_with_vat != total_without_vat:
                validation_errors.append(
                    f"Строка {idx}: Для товара без НДС итоговая сумма должна равняться сумме без НДС. "
                    f"В таблице: total_with_vat={total_with_vat}, {field_name}={total_without_vat}"
                )
            
        except (DecimalException, ZeroDivisionError, KeyError) as e:
            validation_errors.append(f"Строка {idx}: Ошибка при проверке - {str(e)}")
    
    return {
        "is_valid": len(validation_errors) == 0,
        "errors": validation_errors,
        "checked_items": len(table_items)
    }