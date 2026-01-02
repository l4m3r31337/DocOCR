from typing import Dict, List


class DocumentValidator:
    def validate(self, data: Dict) -> Dict:
        errors = []
        warnings = []

        table = data.get("table_data", [])
        totals = data.get("totals", {})

        # --- Проверка таблицы ---
        if not table:
            errors.append("Табличная часть отсутствует")
            return self._result(errors, warnings)

        # --- Проверка нумерации ---
        expected = 1
        for row in table:
            if row.get("row_number") != expected:
                warnings.append(
                    f"Нарушена нумерация строк (ожидалась {expected})"
                )
                break
            expected += 1

        # --- Проверка арифметики ---
        calc_sum = 0.0

        for row in table:
            name = row.get("product_name", "")
            qty = row.get("quantity", 0)
            price = row.get("price", 0)
            total = row.get("total", 0)

            if qty <= 0 or price <= 0:
                warnings.append(f"Некорректные значения в строке: {name}")
                continue

            calc = round(qty * price, 2)

            if abs(calc - total) > 0.05:
                warnings.append(
                    f"Ошибка расчета строки '{name}': {calc} ≠ {total}"
                )

            calc_sum += calc

        # --- Проверка итога ---
        total_doc = totals.get("total_amount")

        if total_doc:
            if abs(calc_sum - total_doc) > 1:
                warnings.append(
                    f"Итог не совпадает: расчет {calc_sum}, документ {total_doc}"
                )
        else:
            warnings.append("Итоговая сумма не найдена")

        return self._result(errors, warnings)

    def _result(self, errors: List[str], warnings: List[str]) -> Dict:
        return {
            "errors": errors,
            "warnings": warnings,
            "is_valid": len(errors) == 0
        }


validator = DocumentValidator()
