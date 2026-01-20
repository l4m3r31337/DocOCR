import re
from typing import Any, Dict
import logging

logger = logging.getLogger("DocProcessor")

def _parse_upd_header(self, text: str) -> Dict[str, Any]:
    """Парсинг шапки УПД"""
    logger.debug("Запущен парсер шапки УПД")

    result = {
        "document_type": "УПД",
        "seller": {"name": "", "inn": "", "kpp": "", "address": ""},
        "buyer": {"name": "", "inn": "", "kpp": "", "address": ""},
        "shipper": {"name": "", "address": ""},
        "consignee": {"name": ""},
        "document_info": {"number": "", "date": ""},
        "basis": {"number": "", "date": ""},
        "extraction_status": "success"
        }

    try:
        # Номер документа
        doc_num_match = re.search(
            r'Универсальный.*?Счет-фактура\s*[№N]?\s*(\d+)', text, re.IGNORECASE)
        if not doc_num_match:
            doc_num_match = re.search(
                r'УПД\s*[№N]?\s*(\d+)', text, re.IGNORECASE)
        if doc_num_match:
            result["document_info"]["number"] = doc_num_match.group(1)

        # Дата
        date_match = re.search(
            r'от\s*(\d{1,2}[\.\s]\d{1,2}[\.\s]\d{4})', text, re.IGNORECASE)
        if date_match:
            date_str = date_match.group(1)
            date_str = re.sub(r'\s+', '.', date_str.strip())
            result["document_info"]["date"] = date_str

        # Продавец
        seller_match = re.search(
            r'Продавец[:\s]+(.+?)(?:\(2\)|\n|$)', text, re.IGNORECASE)
        if seller_match:
            result["seller"]["name"] = self._clean_text(
                seller_match.group(1))

        # Продавец - ИНН/КПП
        seller_inn_kpp = self._extract_inn_kpp(text, "продавца")
        result["seller"]["inn"] = seller_inn_kpp["inn"]
        result["seller"]["kpp"] = seller_inn_kpp["kpp"]
        
        # Продавец - адрес
        seller_address_match = re.search(
            r'Адрес.*?:(.+?)(?:\(2а\)|\n|$)', text, re.IGNORECASE)
        if seller_address_match:
            result["seller"]["address"] = self._clean_text(
            seller_address_match.group(1))

        # Покупатель
        buyer_match = re.search(
            r'Покупатель[:\s]+(.+?)(?:\(6\)|\n|$)', text, re.IGNORECASE)
        if buyer_match:
            result["buyer"]["name"] = self._clean_text(
                buyer_match.group(1))

        # Покупатель - ИНН/КПП
        buyer_inn_kpp = self._extract_inn_kpp(text, "покупателя")
        result["buyer"]["inn"] = buyer_inn_kpp["inn"]
        result["buyer"]["kpp"] = buyer_inn_kpp["kpp"]

        # Покупатель - адрес
        # 1. Находим начало секции покупателя
        buyer_start = re.search(r'Покупатель:', text, re.IGNORECASE)
        if buyer_start:
            # 2. Берем текст после "Покупатель:"
            text_after_buyer = text[buyer_start.end():]

            # 3. Находим адрес в этом тексте
            # Сначала ищем "Адрес:" и захватываем следующую строку
            address_match = re.search(r'Адрес:\s*([^\n]+?)(?=\s*ИНН/КПП|\n|$)', text_after_buyer, re.IGNORECASE)
            if address_match:
                result["buyer"]["address"] = self._clean_text(
                    address_match.group(1))
            else:
                # Если не нашли с новой строкой, пробуем найти в той же строке
                address_match = re.search(
                    r'Адрес:\s*([^\n]+)', text_after_buyer, re.IGNORECASE)
                if address_match:
                    result["buyer"]["address"] = self._clean_text(
                        address_match.group(1))

        # Грузоотправитель (в УПД часто "он же" - тот же продавец)
        shipper_match = re.search(
            r'Грузоотправитель.*?:(.+?)(?:\(3\)|\n|$)', text, re.IGNORECASE)
        if shipper_match:
            shipper_name = self._clean_text(shipper_match.group(1))
            result["shipper"]["name"] = shipper_name
            if "он же" in shipper_name.lower() or "онже" in shipper_name.lower():
                result["shipper"]["name"] = result["seller"]["name"]
                result["shipper"]["address"] = result["seller"]["address"]

        # Грузополучатель
        consignee_match = re.search(
            r'Грузополучатель.*?:(.+?)(?:\(4\)|\n|$)', text, re.IGNORECASE)
        if consignee_match:
            full_text = consignee_match.group(1).strip()
    
            # Способ 1: Разделяем по индексу (6 цифр)
            index_match = re.search(r'(\d{6})', full_text)
            if index_match:
                idx_pos = index_match.start()
        
                # Имя - всё до индекса
                consignee_name = full_text[:idx_pos].rstrip(', ')
        
                # Адрес - начиная с индекса
                consignee_address = full_text[idx_pos:].strip()
        
                result["consignee"]["name"] = self._clean_text(consignee_name)
                result["consignee"]["address"] = self._clean_text(consignee_address)
            else:
                # Если индекс не найден, используем всю строку как имя
                result["consignee"]["name"] = self._clean_text(full_text)
                result["consignee"]["address"] = ""


        # Основание (в УПД обычно есть)
        basis_match = re.search(
            r'Основание[^:]*?([\w\d/]+[^\s]*?)\s*от\s*(\d{2}\.\d{2}\.\d{4})', text, re.IGNORECASE)
        if basis_match:
            result["basis"]["number"] = basis_match.group(1)
            result["basis"]["date"] =  basis_match.group(2)

    except Exception as e:
        logger.error(f"Ошибка при парсинге шапки УПД: {e}")
        result["extraction_status"] = f"error: {str(e)}"

    return result
