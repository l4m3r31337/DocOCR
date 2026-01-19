"""
Модуль для пакетной обработки документов
"""
import os
import concurrent.futures
from pathlib import Path
from typing import List, Dict
import logging
import sys

# Добавляем путь к модулям
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from logger_config import setup_logging
from ocr_engine import extract_text
from document_classifier import classify_document
from data_parser import parse_document
from table_parser import extract_and_parse_table
from json_builder import save_to_json


class BatchProcessor:
    """Класс для пакетной обработки документов"""
    
    # Поддерживаемые форматы
    SUPPORTED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.tif'}
    
    def __init__(self, input_folder: str, output_folder: str, 
                 num_workers: int = 1, skip_existing: bool = False):
        """
        Инициализация процессора
        
        Args:
            input_folder: Папка с документами
            output_folder: Папка для результатов
            num_workers: Количество параллельных процессов
            skip_existing: Пропускать уже обработанные файлы
        """
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        self.num_workers = max(1, min(num_workers, os.cpu_count() or 4))
        self.skip_existing = skip_existing
        
        self.logger = logging.getLogger("DocProcessor")
        
        # Создаем папку для результатов, если её нет
        self.output_folder.mkdir(parents=True, exist_ok=True)
        
        # Счетчики статистики
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }
    
    def _get_files_to_process(self) -> List[Path]:
        """Получить список файлов для обработки (исправленная версия)"""
        files = []
    
        # Проходим по всем файлам в папке один раз
        for item in self.input_folder.iterdir():
            if item.is_file():
                ext = item.suffix.lower()  # всегда в нижнем регистре
                if ext in self.SUPPORTED_EXTENSIONS:
                    files.append(item)
    
        # Убираем возможные дубликаты (на всякий случай)
        unique_files = []
        seen = set()
    
        for file_path in files:
            # Используем абсолютный путь для сравнения
            abs_path = str(file_path.absolute())
            if abs_path not in seen:
                seen.add(abs_path)
                unique_files.append(file_path)
    
        # Сортируем по имени для удобства
        unique_files.sort(key=lambda x: x.name)
    
        self.logger.debug(f"Найдено уникальных файлов: {len(unique_files)}")
        for f in unique_files:
            self.logger.debug(f"  - {f.name}")
    
        return unique_files
    
    def _process_single_file(self, file_path: Path) -> Dict:
        """
        Обработка одного файла
        Возвращает словарь с результатами
        """
        result = {
            'file': str(file_path),
            'filename': file_path.name,
            'success': False,
            'error': None,
            'output_path': None
        }
        
        try:
            # Проверяем, не обработан ли уже файл
            output_file = self.output_folder / f"{file_path.stem}.json"
            if self.skip_existing and output_file.exists():
                self.logger.info(f"Пропускаем (уже обработан): {file_path.name}")
                result['skipped'] = True
                return result
            
            self.logger.info(f"Начинаю обработку: {file_path.name}")
            
            # 1. OCR
            text = extract_text(str(file_path))
            
            if not text or len(text.strip()) < 10:
                error_msg = f"Не удалось извлечь текст (получено {len(text) if text else 0} символов)"
                self.logger.warning(f"{error_msg}: {file_path.name}")
                result['error'] = error_msg
                return result
            
            # 2. Классификация
            doc_type = classify_document(text)
            self.logger.debug(f"Тип документа {file_path.name}: {doc_type}")
            
            # 3. Парсинг
            parsed_data = parse_document(doc_type, text)
            parsed_table = extract_and_parse_table(file_path, doc_type)
            json_data = {**parsed_data, **parsed_table}
            
            # 4. Сохранение
            success = save_to_json(json_data, str(output_file))
            
            if success:
                self.logger.info(f"Успешно обработан: {file_path.name}")
                result['success'] = True
                result['output_path'] = str(output_file)
                result['doc_type'] = doc_type
                result['items_count'] = len(parsed_data.get('table_data', []))
            else:
                error_msg = "Ошибка при сохранении JSON"
                self.logger.error(f"{error_msg}: {file_path.name}")
                result['error'] = error_msg
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"  Ошибка при обработке {file_path.name}: {error_msg}", 
                            exc_info=self.logger.level == logging.DEBUG)
            result['error'] = error_msg
        
        return result
    
    def process_all(self) -> bool:
        """Обработка всех файлов в папке"""
        files = self._get_files_to_process()
        
        if not files:
            self.logger.warning(f"В папке {self.input_folder} не найдено поддерживаемых файлов")
            self.logger.info(f"Поддерживаемые форматы: {', '.join(self.SUPPORTED_EXTENSIONS)}")
            return False
        
        self.stats['total'] = len(files)
        self.logger.info(f"Найдено файлов для обработки: {len(files)}")
        self.logger.info(f"Использую {self.num_workers} параллельных процесса(ов)")
        
        # Обработка файлов
        results = []
        
        if self.num_workers > 1:
            # Многопоточная обработка
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_workers) as executor:
                future_to_file = {
                    executor.submit(self._process_single_file, file): file 
                    for file in files
                }
                
                for future in concurrent.futures.as_completed(future_to_file):
                    file = future_to_file[future]
                    try:
                        result = future.result()
                        results.append(result)
                        
                        # Обновляем статистику
                        if result.get('skipped'):
                            self.stats['skipped'] += 1
                        elif result['success']:
                            self.stats['success'] += 1
                        else:
                            self.stats['failed'] += 1
                            
                    except Exception as e:
                        self.logger.error(f"Неожиданная ошибка при обработке {file.name}: {e}")
                        self.stats['failed'] += 1
        else:
            # Последовательная обработка
            for file in files:
                result = self._process_single_file(file)
                results.append(result)
                
                # Обновляем статистику
                if result.get('skipped'):
                    self.stats['skipped'] += 1
                elif result['success']:
                    self.stats['success'] += 1
                else:
                    self.stats['failed'] += 1
        
        # Выводим итоговую статистику
        self._print_statistics(results)
        
        return self.stats['success'] > 0
    
    def _print_statistics(self, results: List[Dict]):
        """Вывод статистики обработки"""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("ИТОГОВАЯ СТАТИСТИКА:")
        self.logger.info("=" * 60)
        
        self.logger.info(f"Всего файлов: {self.stats['total']}")
        self.logger.info(f"Успешно обработано: {self.stats['success']}")
        self.logger.info(f"Пропущено (уже обработаны): {self.stats['skipped']}")
        self.logger.info(f"С ошибками: {self.stats['failed']}")
        
        # Детали по ошибкам
        if self.stats['failed'] > 0:
            self.logger.info("\n  Детали ошибок:")
            for result in results:
                if not result.get('success') and not result.get('skipped'):
                    self.logger.info(f"{result['filename']}: {result.get('error', 'Неизвестная ошибка')}")
        
        self.logger.info(f"Результаты сохранены в: {self.output_folder}")
        self.logger.info("=" * 60)


def process_batch(input_folder: str, output_folder: str, 
                  num_workers: int = 2, skip_existing: bool = False) -> bool:
    """
    Функция для вызова пакетной обработки из других модулей
    
    Returns:
        True если хотя бы один файл успешно обработан
    """
    processor = BatchProcessor(input_folder, output_folder, num_workers, skip_existing)
    return processor.process_all()