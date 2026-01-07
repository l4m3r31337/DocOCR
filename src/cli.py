#!/usr/bin/env python3
"""
CLI интерфейс для системы распознавания бухгалтерских документов
"""
import argparse
import sys
import os
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ocr_engine import extract_text
from document_classifier import classify_document
from data_parser import parse_document_data, save_to_json

# Импортируем наш новый модуль для пакетной обработки
from batch_processor import BatchProcessor
from logger_config import setup_logging


class DocumentProcessorCLI:
    def __init__(self):
        self.logger = setup_logging()
        
    def process_single(self, input_file: str, output_file: str = None) -> bool:
        """Обработка одного документа"""
        try:
            self.logger.info(f"Начинаю обработку файла: {input_file}")
            
            # Проверяем существование файла
            if not os.path.exists(input_file):
                self.logger.error(f"Файл не найден: {input_file}")
                return False
            
            # 1. Извлекаем текст с помощью OCR
            self.logger.debug("Извлечение текста с помощью OCR...")
            text = extract_text(input_file)
            
            if not text or len(text.strip()) < 50:
                self.logger.warning(f"Мало текста извлечено из файла: {len(text) if text else 0} символов")
            
            # 2. Классифицируем документ
            self.logger.debug("Классификация документа...")
            doc_type = classify_document(text)
            self.logger.info(f"Определен тип документа: {doc_type}")
            
            # 3. Парсим данные
            self.logger.debug("Парсинг структурированных данных...")
            parsed_data = parse_document_data(text, doc_type)
            
            # 4. Определяем путь для сохранения
            if not output_file:
                input_path = Path(input_file)
                output_file = input_path.parent / f"{input_path.stem}_parsed.json"
            
            # 5. Сохраняем в JSON
            self.logger.debug(f"Сохранение в JSON: {output_file}")
            success = save_to_json(parsed_data, str(output_file))
            
            if success:
                self.logger.info(f"✅ Успешно обработан: {input_file}")
                self.logger.info(f"📁 Результат сохранен в: {output_file}")
                return True
            else:
                self.logger.error(f"❌ Ошибка при сохранении JSON: {output_file}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка при обработке файла {input_file}: {str(e)}", exc_info=True)
            return False
    
    def run(self):
        """Основной метод запуска CLI"""
        parser = argparse.ArgumentParser(
            description='Система распознавания бухгалтерских документов',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Примеры использования:
  doc-processor single --input документ.pdf --output результат.json
  doc-processor batch --input-folder ./документы/ --output-folder ./результаты/
  doc-processor batch --input-folder ./документы/ --output-folder ./результаты/ --workers 4
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Доступные команды')
        
        # Команда для обработки одного файла
        single_parser = subparsers.add_parser('single', help='Обработка одного документа')
        single_parser.add_argument(
            '--input', '-i',
            required=True,
            help='Путь к входному файлу (PDF, JPG, PNG)'
        )
        single_parser.add_argument(
            '--output', '-o',
            help='Путь для сохранения JSON (по умолчанию: рядом с исходным файлом)'
        )
        
        # Команда для пакетной обработки
        batch_parser = subparsers.add_parser('batch', help='Пакетная обработка документов')
        batch_parser.add_argument(
            '--input-folder', '-if',
            required=True,
            help='Папка с документами для обработки'
        )
        batch_parser.add_argument(
            '--output-folder', '-of',
            required=True,
            help='Папка для сохранения результатов'
        )
        batch_parser.add_argument(
            '--workers', '-w',
            type=int,
            default=2,
            help='Количество параллельных процессов (по умолчанию: 2)'
        )
        batch_parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Пропускать уже обработанные файлы'
        )
        
        # Общие параметры
        parser.add_argument(
            '--log-level',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            default='INFO',
            help='Уровень детализации логов (по умолчанию: INFO)'
        )
        parser.add_argument(
            '--log-file',
            help='Путь к файлу логов (по умолчанию: doc_processor.log)'
        )
        
        # Проверяем, переданы ли аргументы
        if len(sys.argv) == 1:
            parser.print_help()
            sys.exit(1)
        
        args = parser.parse_args()
        
        # Настраиваем логирование с учетом параметров
        self.logger = setup_logging(
            log_level=args.log_level,
            log_file=args.log_file
        )
        
        # Обработка команд
        if args.command == 'single':
            success = self.process_single(args.input, args.output)
            sys.exit(0 if success else 1)
            
        elif args.command == 'batch':
            processor = BatchProcessor(
                input_folder=args.input_folder,
                output_folder=args.output_folder,
                num_workers=args.workers,
                skip_existing=args.skip_existing
            )
            success = processor.process_all()
            sys.exit(0 if success else 1)
            
        else:
            parser.print_help()
            sys.exit(1)


def main():
    """Точка входа для CLI"""
    cli = DocumentProcessorCLI()
    cli.run()


if __name__ == "__main__":
    main()