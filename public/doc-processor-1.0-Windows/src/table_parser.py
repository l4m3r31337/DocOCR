import gc
import json
import time
import camelot
import pandas as pd
from typing import Dict, List, Any
import logging
from parsers import invoice_table_parser, torg_12_table_parser, upd_table_parser

logger = logging.getLogger("DocProcessor")


class TableParser:
    def __init__(self):
        self.parsers = {
            'СЧЕТ_ФАКТУРА': self._parse_invoice_table,
            'УПД': self._parse_upd_table,
            'ТОРГ-12': self._parse_torg12_table
        }
    
    def extract_tables_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Извлекает таблицы из PDF файла с помощью camelot
    
        Returns:
            Список словарей с данными таблиц
        """
        logger.debug(f"Извлечение таблиц из PDF: {pdf_path}")
    
        try:
            tables = camelot.read_pdf(pdf_path, pages='1-end', flavor='lattice')

            time.sleep(0.1)
        
            if tables.n == 0:
                logger.warning("Таблицы не найдены в документе")
                return []
        
            logger.debug(f"Найдено таблиц: {tables.n}")
        
            # Создаем DataFrame с правильными именами колонок
            if tables.n == 1:
                df = tables[0].df
            else:
                df_list = [tables[i].df for i in range(tables.n)]
                df = pd.concat(df_list, ignore_index=True)
        
            # Переименовываем колонки в строковые индексы "0", "1", "2"...
            df.columns = [str(i) for i in range(len(df.columns))]
        
            # Преобразуем в список словарей
            data = df.to_dict(orient='records')
        
            logger.debug(f"Извлечено записей: {len(data)}")
        
            # Отладка
            if data:
                logger.debug(f"Пример строки данных: {data[0]}")
                logger.debug(f"Ключи в строке: {list(data[0].keys())}")
        
            return data
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении таблиц из PDF: {e}")
            raise

        finally:
            gc.collect()
    
    def parse(self, document_type: str, table_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Основной метод парсинга табличной части документа
        
        Args:
            document_type: Тип документа
            table_data: Данные таблицы, извлеченные из PDF
            
        Returns:
            Словарь с распарсенными данными из таблицы
        """
        logger.debug(f"Парсим таблицу документа типа: {document_type}")
        
        if document_type not in self.parsers:
            logger.error(f"Неизвестный тип документа для парсинга таблицы: {document_type}")
            raise ValueError(f"Парсер таблиц для типа {document_type} не реализован")
        
        return self.parsers[document_type](table_data)
    
    def _parse_invoice_table(self, table_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Парсинг таблицы счёта-фактуры"""
        return invoice_table_parser._parse_invoice_table(self, table_data)
    
    def _parse_upd_table(self, table_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Парсинг таблицы УПД"""
        return upd_table_parser._parse_upd_table(self, table_data)
    
    def _parse_torg12_table(self, table_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Парсинг таблицы ТОРГ-12"""
        return torg_12_table_parser._parse_torg_12_table(self, table_data)
    
    def save_to_json(self, data: Dict[str, Any], filename: str) -> None:
        """Сохранение результата в JSON файл"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug(f"Данные таблицы сохранены в файл: {filename}")
        except Exception as e:
            logger.error(f"Ошибка сохранения таблицы в файл {filename}: {e}")
            raise


# Функция для использования в пайплайне
def parse_table(document_type: str, table_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Основная функция парсинга табличной части документа
    
    Args:
        document_type: Тип документа от классификатора
        table_data: Данные таблицы
        
    Returns:
        Словарь с распарсенными данными из таблицы
    """
    parser = TableParser()
    return parser.parse(document_type, table_data)


def extract_and_parse_table(pdf_path: str, document_type: str) -> Dict[str, Any]:
    """
    Комбинированная функция: извлекает и парсит таблицу из PDF
    
    Args:
        pdf_path: Путь к PDF файлу
        document_type: Тип документа
        
    Returns:
        Словарь с распарсенными данными из таблицы
    """
    parser = TableParser()
    
    # Извлекаем таблицы из PDF
    table_data = parser.extract_tables_from_pdf(pdf_path)
    
    if not table_data:
        return {
            "error": "Таблицы не найдены в документе",
            "table_items": [],
            "totals": {"total_without_vat": 0.0, "total_vat": 0.0, "total_with_vat": 0.0},
            "validation_results": {
                "line_numbering_check": {"status": "FAILED", "message": "Таблицы не найдены"},
                "arithmetic_check": {"status": "FAILED", "message": "Нет данных для проверки"}
            }
        }
    
    # Парсим таблицу
    result = parser.parse(document_type, table_data)

    return result