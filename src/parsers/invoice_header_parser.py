import re
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)

def _parse_invoice_header(self, text: str) -> Dict[str, Any]:
        """Парсинг шапки счёта-фактуры"""
        logger.info("Запущен парсер шапки счёта-фактуры")

        result = {
            "document_type": "СЧЕТ_ФАКТУРА",
            "seller": {"name": "", "inn": "", "kpp": "", "address": ""},
            "buyer": {"name": "", "inn": "", "kpp": "", "address": ""},
            "shipper": {"name": "", "address": ""},
            "consignee": {"name": ""},
            "document_info": {"number": "", "date": ""},
            "basis": "",
            "extraction_status": "success"
        }

        try:
            # Извлекаем номер документа
            doc_num_match = re.search(
                r'Счет-фактура\s*[№N]?\s*(\d+)', text, re.IGNORECASE)
            if doc_num_match:
                result["document_info"]["number"] = doc_num_match.group(1)

            # Извлекаем дату документа
            # Извлекаем дату документа (поддерживает русские даты)
            # Ищем дату после номера счета-фактуры
            date_match = re.search(
                r'Счет-фактура №.*?от\s*(\d{1,2}\s+[а-я]+\s+\d{4}\s*г\.)', text, re.IGNORECASE)
            if date_match:
                date_str = date_match.group(1).replace('г.', '').strip()
                # Конвертируем русскую дату в формат ДД.ММ.ГГГГ
                months = {
                    'января': '01', 'февраля': '02', 'марта': '03',
                    'апреля': '04', 'мая': '05', 'июня': '06',
                    'июля': '07', 'августа': '08', 'сентября': '09',
                    'октября': '10', 'ноября': '11', 'декабря': '12'
                }
                for month_ru, month_num in months.items():
                    if month_ru in date_str.lower():
                        parts = date_str.split()
                        if len(parts) >= 3:
                            day = parts[0].zfill(2)
                            year = parts[2]
                            result["document_info"]["date"] = f"{day}.{month_num}.{year}"
                        break
            else:
                # Если не нашли дату в текстовом формате, ищем цифровой формат
                date_match = re.search(
                    r'Счет-фактура №.*?от\s*(\d{1,2}[\.\s]\d{1,2}[\.\s]\d{4})', text, re.IGNORECASE)
                if date_match:
                    date_str = date_match.group(1)
                    date_str = re.sub(r'\s+', '.', date_str.strip())
                    result["document_info"]["date"] = date_str

            # Продавец - имя
            seller_match = re.search(
                r'Продавец[:\s]+(.+?)(?:\n|$)', text, re.IGNORECASE)
            if seller_match:
                result["seller"]["name"] = self._clean_text(
                    seller_match.group(1))

            # Продавец - ИНН/КПП
            seller_inn_kpp = self._extract_inn_kpp(text, "продавца")
            result["seller"]["inn"] = seller_inn_kpp["inn"]
            result["seller"]["kpp"] = seller_inn_kpp["kpp"]

            # Продавец - адрес
            seller_address_match = re.search(
                r'Адрес[:\s]+(.+?)(?=\s*ИНН/КПП|\n|$)', text, re.IGNORECASE)
            if seller_address_match:
                result["seller"]["address"] = self._clean_text(
                    seller_address_match.group(1))

            # Покупатель - имя
            buyer_match = re.search(
                r'Покупатель[:\s]+(.+?)(?:\n|$)', text, re.IGNORECASE)
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
                address_match = re.search(
                    r'Адрес:\s*([^\n]+?)(?=\s*ИНН/КПП|\n|$)', text_after_buyer, re.IGNORECASE)
                if address_match:
                    result["buyer"]["address"] = self._clean_text(address_match.group(1))
                else:
                    # Если не нашли с новой строкой, пробуем найти в той же строке
                    address_match = re.search(
                        r'Адрес:\s*([^\n]+)', text_after_buyer, re.IGNORECASE)
                    if address_match:
                        result["buyer"]["address"] = self._clean_text(
                            address_match.group(1))
                        
            # Грузоотправитель
            shipper_match = re.search(
                r'Грузоотправитель и его адрес[:\s]+(.+?)(?:\n|$)', text, re.IGNORECASE)
            if shipper_match:
                shipper_name = self._clean_text(shipper_match.group(1))
                result["shipper"]["name"] = shipper_name
                # Если "он же", копируем данные продавца
                if "он же" in shipper_name.lower() or "онже" in shipper_name.lower():
                    result["shipper"]["name"] = result["seller"]["name"]
                    result["shipper"]["address"] = result["seller"]["address"]
                else:
                    # В СФ адрес часто совпадает с именем
                    result["shipper"]["address"] = shipper_name
                        

            # Грузополучатель
            consignee_match = re.search(
                r'Грузополучатель и его адрес[:\s]+([^\n]+)', text, re.IGNORECASE)
            if consignee_match:
                consignee_name = consignee_match.group(1).strip()
                result["consignee"]["name"] = consignee_name

            # Основание (обычно в УПД, но может быть и в счете-фактуре)
            basis_match = re.search(
                r'Основание.*?:(.+?)(?:\n|$)', text, re.IGNORECASE)
            if basis_match:
                result["basis"] = self._clean_text(basis_match.group(1))

        except Exception as e:
            logger.error(f"Ошибка при парсинге шапки счёта-фактуры: {e}")
            result["extraction_status"] = f"error: {str(e)}"

        return result