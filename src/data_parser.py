import re
import json
from datetime import datetime

try:
    from table_extractor import extract_table_data
    from validator import validator
except:
    from .table_extractor import extract_table_data
    from .validator import validator


MONTHS = {
    "января": "01",
    "февраля": "02",
    "марта": "03",
    "апреля": "04",
    "мая": "05",
    "июня": "06",
    "июля": "07",
    "августа": "08",
    "сентября": "09",
    "октября": "10",
    "ноября": "11",
    "декабря": "12",
}


class DataParser:
    def parse_document(self, text: str, doc_type: str):
        table = extract_table_data(text, doc_type)
        totals = self._parse_totals(text, table)

        return {
            "document_type": doc_type,
            "header": self._parse_header(text),
            "table_data": table,
            "totals": totals,
            "validation": validator.validate({
                "table_data": table,
                "totals": totals
            }),
            "metadata": {
                "parsed_at": datetime.now().isoformat()
            }
        }

    # ---------------- HEADER ---------------- #

    def _parse_header(self, text: str):
        header = {}

        # ---------- НОМЕР ДОКУМЕНТА ----------
        header["doc_number"] = self._extract_doc_number(text)

        # ---------- ДАТА ----------
        header["doc_date"] = self._extract_date(text)

        # ---------- ПРОДАВЕЦ ----------
        m = re.search(r"(Продавец|Поставщик)\s*[:\-]?\s*(.+)", text)
        if m:
            header["seller"] = m.group(2).split("\n")[0].strip()

        # ---------- ПОКУПАТЕЛЬ ----------
        m = re.search(r"(Покупатель|Грузополучатель)\s*[:\-]?\s*(.+)", text)
        if m:
            header["buyer"] = m.group(2).split("\n")[0].strip()

        return header

    # ---------------- НОМЕР ДОКУМЕНТА ---------------- #

    def _extract_doc_number(self, text: str):
        # № 12345
        m = re.search(r"№\s*(\d+)", text)
        if m:
            return m.group(1)

        # ТОВАРНАЯ НАКЛАДНАЯ  39883
        m = re.search(
            r"(ТОВАРНАЯ\s+НАКЛАДНАЯ|СЧЕТ[-\s]?ФАКТУРА|УПД)\s+(\d{2,})",
            text,
            re.IGNORECASE
        )
        if m:
            return m.group(2)

        # номер 123 от ...
        m = re.search(r"номер\s+(\d+)", text, re.IGNORECASE)
        if m:
            return m.group(1)

        return None

    # ---------------- ДАТА ---------------- #

    def _extract_date(self, text: str):
        # 10.01.2015
        m = re.search(r"(\d{1,2}\.\d{1,2}\.\d{4})", text)
        if m:
            return m.group(1)

        # 10 декабря 2016
        m = re.search(
            r"(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+(\d{4})",
            text,
            re.IGNORECASE
        )
        if m:
            return f"{m.group(1).zfill(2)}.{MONTHS[m.group(2).lower()]}.{m.group(3)}"

        return None

    # ---------------- TOTALS ---------------- #

    def _parse_totals(self, text: str, table):
        m = re.search(r"Всего.*?([\d\s,.]+)", text, re.IGNORECASE)
        if m:
            try:
                return {
                    "total_amount": float(
                        m.group(1).replace(" ", "").replace(",", ".")
                    )
                }
            except:
                pass

        return {
            "total_amount": round(sum(r["total"] for r in table), 2)
        }


# ---------------- API ---------------- #

data_parser = DataParser()


def parse_document_data(text: str, doc_type: str):
    return data_parser.parse_document(text, doc_type)


def save_to_json(data, filename: str):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False
