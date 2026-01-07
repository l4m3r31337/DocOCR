"""
DocOCR - система распознавания документов
"""

__version__ = '1.0.0'
__author__ = 'DocOCR Team'

# Экспортируем основные функции
from .ocr_engine import extract_text
from .document_classifier import classify_document
from .data_parser import parse_document_data, save_to_json
from .table_extractor import extract_table_data
from .validator import validator
from .batch_processor import BatchProcessor, process_batch
from .logger_config import setup_logging
from .cli import main

__all__ = [
    'extract_text',
    'classify_document',
    'parse_document_data',
    'save_to_json',
    'extract_table_data',
    'validator',
    'BatchProcessor',
    'process_batch',
    'setup_logging',
    'main'
]