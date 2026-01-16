import re
from typing import Any, Dict, List
import logging

logger = logging.getLogger("__name__")

def _parse_torg12_header(self, text: str) -> Dict[str, Any]:
    """Парсинг шапки ТОРГ-12"""
    logger.info("Запущен парсер шапки ТОРГ-12")
    
    result = {
        "document_type": "ТОРГ-12",
        "seller": {"name": "", "inn": "", "count": "", "address": ""},
        "buyer": {"name": "", "inn": "", "count": "", "address": ""},
        "shipper": {"name": "", "address": ""},
        "consignee": {"name": "", "address": ""},
        "document_info": {"number": "", "date": ""},
        "basis": {"number": "", "date": ""},
        "extraction_status": "success"
    }
    
    try:
        # 1. ОЧИСТКА ТЕКСТА
        ocr_corrections = {
            'We': 'к/с', 'yn': 'ул', 'Око': 'ОКПО', 'NAO': 'ПАО',
            'ata}': 'дата', '‘': '"', '`': '"', 'по Око ___[ |': 'по ОКПО',
            '!' : 'i'
        }

        for wrong, correct in ocr_corrections.items():
            text = text.replace(wrong, correct)
        
        text = re.sub(r'\n\s*\n+', '\n', text)
        
        organizations = extract_simple_blocks(text)

        # Грузоотправитель
        seller = parse_organization_block(organizations[0])
        result["seller"]["name"] = seller["name"]
        result["seller"]["inn"] = seller["inn"]
        result["seller"]["count"] = seller["count"]
        result["seller"]["address"] = seller["address"]


        #Грузополучатель
        buyer = parse_organization_block(organizations[1])
        result["buyer"]["name"] = buyer["name"]
        result["buyer"]["inn"] = buyer["inn"]
        result["buyer"]["count"] = buyer["count"]
        result["buyer"]["address"] = buyer["address"]

        #Поставщик
        shipper = parse_organization_block(organizations[2])

        result["shipper"]["name"] = shipper["name"]
        result["shipper"]["address"] = shipper["address"]

        #Плательщик
        consignee = parse_organization_block(organizations[3])

        result["consignee"]["name"] = consignee["name"]
        result["consignee"]["address"] = consignee["address"]
        
        
        # Номер и дата документа
        doc_num_match = re.search(r'ТОВАРНАЯ НАКЛАДНАЯ\s+(\d+)', text, re.IGNORECASE)
        if doc_num_match:
            result["document_info"]["number"] = doc_num_match.group(1)
        
        date_match = re.search(r'ТОВАРНАЯ НАКЛАДНАЯ\s+\d+\s+(\d{2}\.\d{2}\.\d{4})', text, re.IGNORECASE)
        if date_match:
            result["document_info"]["date"] = date_match.group(1)
        
        # Основание
        basis_match = re.search(r'Основание\s*([^\n]+)', text, re.IGNORECASE)
        if basis_match:
            basis_text = basis_match.group(1).strip()
            basis_text = re.sub(r'\s*номер\s*$', '', basis_text)
            
            if ' от ' in basis_text:
                parts = basis_text.split(' от ')
                result["basis"]["number"] = self._clean_text(parts[0].strip())
                result["basis"]["date"] = self._clean_text(parts[1].strip())
            elif re.search(r'\d{2}\.\d{2}\.\d{4}', basis_text):
                date_match = re.search(r'(\d{2}\.\d{2}\.\d{4})', basis_text)
                if date_match:
                    result["basis"]["date"] = date_match.group(1)
                    result["basis"]["number"] = self._clean_text(basis_text.replace(result["basis"]["date"], '').strip())
            else:
                result["basis"]["number"] = self._clean_text(basis_text)
        
        
    except Exception as e:
        logger.error(f"Ошибка при парсинге шапки ТОРГ-12: {e}", exc_info=True)
        result["extraction_status"] = f"error: {str(e)}"
    
    return result

def extract_simple_blocks(text: str) -> List[str]:
    """Самая простая функция: ищем 4 вхождения организаций"""
    
    # Очистка
    text = text.replace('yn', 'ул').replace('We', 'к/с').replace('NAO', 'ПАО')
    text = text.replace('OOO', 'ООО')

    blocks = []
    
    # Ищем все позиции, где начинаются организации
    positions = []
    
    # Ищем "ООО"
    pos = text.find('ООО')
    while pos != -1:
        positions.append(('ООО', pos))
        pos = text.find('ООО', pos + 3)
    
    # Ищем "Филиал" (с большой буквы)
    pos = text.find('Филиал')
    while pos != -1:
        positions.append(('Филиал', pos))
        pos = text.find('Филиал', pos + 6)
    
    # Сортируем по позиции
    positions.sort(key=lambda x: x[1])
    
    # Берём первые 4 позиции
    for i, (org_type, start_pos) in enumerate(positions[:4]):
        # Определяем конец блока
        if i + 1 < len(positions) and i + 1 < 4:
            end_pos = positions[i + 1][1]
        else:
            end_pos = start_pos + 400
        
        block = text[start_pos:end_pos].strip()
        
        # Обрезаем до разумного места
        # Ищем конец блока по ключевым фразам
        end_phrases = [
            'организация, адрес',
            'организация-грузоотправитель',
            'по ОКПО',
            '\n\n',
            '\nООО',
            '\nФилиал',
            '\nПоставщик',
            '\nПлательщик',
        ]
        
        for phrase in end_phrases:
            pos_in_block = block.find(phrase)
            if pos_in_block != -1:
                if phrase == 'по ОКПО':
                    block = block[:pos_in_block + 10]
                else:
                    block = block[:pos_in_block]
                break
        
        blocks.append(block)
    
    return blocks

# Улучшенная версия с более точным парсингом
def parse_organization_block(block_text: str) -> Dict[str, str]:
    """
    Улучшенный парсинг блока организации
    """
    
    # Нормализуем текст
    block_text = ' '.join(block_text.split())
    
    result = {
        'name': '',
        'inn': '',
        'address': '',
        'count': ''
    }
    
    # 1. Название (самая важная часть)
    # Ищем от начала строки до первой запятой или ИНН
    name_end = len(block_text)
    
    # Ищем конец названия
    for delimiter in [', ИНН', ',', ' ИНН', ' по ОКПО']:
        pos = block_text.find(delimiter)
        if pos != -1 and pos < name_end:
            name_end = pos
    
    result['name'] = clean_text_selective(block_text[:name_end].strip())
    
    # 2. ИНН
    inn_match = re.search(r'ИНН\s*(\d{10,12})', block_text)
    if inn_match:
        result['inn'] = clean_text_selective(inn_match.group(1))
    
    # 3. Адрес
    # Ищем паттерн: индекс (6 цифр), город, улица
    address_pattern = r'(\d{6}[^,]*,\s*[^,]*г[^,]*,\s*[^,]*(?:ул|пр-кт|проспект|проезд|ш|наб|бульвар)[^,]*,\s*(?:дом|д\.?)\s*[^,]*?(?:\s*(?:№?\s*\d+(?:/\d+)?|\d+)\s*(?:(?:корпус|корп\.|строение|стр\.|с\.|литер)\s*[\dА-Яа-я]*)?)?(?:\s*,\s*(?:корпус|корп\.|строение|стр\.|с\.|литер)\s*[\dА-Яа-я]*)?[^,]*|\d{6}[^,]*,\s*[^,]*г[^,]*,\s*[^,]*(?:ул|пр-кт|проспект|проезд|ш|наб|бульвар)[^,]*|\d{6}[^,]*,\s*[^,]*г[^,]*)'
    
    address_match = re.search(address_pattern, block_text)
    if address_match:
        result['address'] = clean_text_selective(address_match.group(1).strip())
    
    # 4. Детали (всё остальное после адреса)
    if result['address']:
        address_pos = block_text.find(result['address'])
        if address_pos != -1:
            count_start = address_pos + len(result['address'])
            if count_start < len(block_text):
                count = block_text[count_start:].strip()
                if count.startswith(','):
                    count = count[1:].strip()
                
                # Фильтруем детали
                if count and not re.match(r'^[,\s-]*$', count):
                    # Убираем "по ОКПО" и мусор
                    if 'по ОКПО' in count:
                        count = count.split('по ОКПО')[0].strip().rstrip(',')
                    
                    result['count'] = clean_text_selective(count)
    
    return result

def clean_text_selective(text: str) -> str:
    """
    Очищает текст, но сохраняет кавычки и нужные символы
    """
    if not text:
        return ""
    
    # 1. Исправляем только критичные OCR-ошибки
    ocr_corrections = {
        'We': 'к/с',
        'yn': 'ул',
        'Око': 'ОКПО',
        'NAO': 'ПАО',
        'ata}': 'дата',
        'fata}': 'дата',
        'Беларус!': 'Беларуси',
        'Малако Беларус!': 'Малако Беларуси',
        'Петербуржское': 'Петербургское',
        'OOO': 'ООО',
        'З41': '34Г',
        'Грузополучатель' : ''
    }
    
    for wrong, correct in ocr_corrections.items():
        text = text.replace(wrong, correct)
    
    # 2. Убираем только мусорные символы: |, [, ], лишние пробелы
    # Но сохраняем: буквы, цифры, пробелы, запятые, точки, №, /, -, ", кавычки

        # Убираем "Форма по ОКУД" и всё что до следующей запятой или конца
    text = re.sub(r'Форма по ОКУД\s*\|\s*\d+\s*\|', '', text)
    
    # Убираем квадратные скобки и их содержимое
    text = re.sub(r'\[.*?\]', '', text)
    
    # Убираем вертикальные палки и дефисы вокруг них
    text = re.sub(r'\s*\|\s*', ' ', text)
    
    # Убираем "___" и подобное
    text = re.sub(r'_{3,}', '', text)
    
    # Убираем "по ОКПО" и мусор после него, но оставляем если это часть адреса
    # "по ОКПО" в конце строки - убираем
    text = re.sub(r'по ОКПО[^,\w]*$', '', text)
    # "по ОКПО" в середине с мусором
    text = re.sub(r'по ОКПО[^,\w]*,', ',', text)
    
    # Убираем стандартные фразы
    garbage_phrases = [
        r'организация[^,]*,\s*адрес[^,]*,\s*телефон[^,]*,\s*факс[^,]*,\s*банковские реквизиты',
        r'организация-грузоотправитель[^,]*,\s*адрес[^,]*,\s*телефон[^,]*,\s*факс[^,]*,\s*банковские реквизиты',
    ]
    
    for phrase in garbage_phrases:
        text = re.sub(phrase, '', text, flags=re.IGNORECASE)
    
    # 3. Чистим пробелы, но аккуратно
    text = re.sub(r'\s+', ' ', text)  # Множественные пробелы в один
    text = re.sub(r'\n', ' ', text)   # Переносы строк в пробелы
    text = text.strip()
    
    # 4. Чистим запятые
    text = re.sub(r',\s*,', ',', text)  # Двойные запятые
    text = re.sub(r'\s*,\s*', ', ', text)  # Нормальные пробелы вокруг запятых
    text = re.sub(r',\s*$', '', text)  # Запятая в конце
    
    return text