import re
from typing import List, Dict, Optional


class TableExtractor:
    def extract_table(self, text: str, doc_type: str) -> List[Dict]:
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        rows = []
        row_num = 1

        for line in lines:
            if self._is_trash(line):
                continue

            parsed = self._parse_line(line)
            if not parsed:
                continue

            parsed["row_number"] = row_num
            rows.append(parsed)
            row_num += 1

        return rows

    def _is_trash(self, line: str) -> bool:
        bad_words = [
            "счет", "фактура", "итого", "всего", "поставщик",
            "покупатель", "инн", "кпп", "банк", "бик",
            "адрес", "р/с", "к/с", "окуд", "форма",
            "подпись", "утверждена", "дата"
        ]

        l = line.lower()

        if len(l) < 8:
            return True

        if any(w in l for w in bad_words):
            return True

        if not re.search(r"\d", l):
            return True

        return False

    def _parse_line(self, line: str) -> Optional[Dict]:
        clean = re.sub(r"[^\w\s.,]", " ", line)
        clean = re.sub(r"\s+", " ", clean)

        nums = re.findall(r"\d+[.,]?\d*", clean)

        if len(nums) < 2:
            return None

        try:
            qty = float(nums[-2].replace(",", "."))
            price = float(nums[-1].replace(",", "."))

            # защита от мусора
            if qty <= 0 or price <= 0:
                return None
            if qty > 100000 or price > 1000000:
                return None

            name = re.sub(r"\d.*$", "", clean).strip()
            if len(name) < 4:
                return None

            return {
                "product_name": name,
                "quantity": round(qty, 3),
                "price": round(price, 2),
                "total": round(qty * price, 2)
            }

        except:
            return None


table_extractor = TableExtractor()


def extract_table_data(text: str, doc_type: str):
    return table_extractor.extract_table(text, doc_type)
