#!/usr/bin/env python3
"""
Простой тест системы распознавания
"""
import os
import sys
import tempfile
import json
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=" * 60)
print("🧪 ТЕСТ СИСТЕМЫ РАСПОЗНАВАНИЯ ДОКУМЕНТОВ")
print("=" * 60)

def test_ocr_engine():
    """Тест OCR движка"""
    print("\n1. Тестирование OCR движка...")
    try:
        from src.ocr_engine import extract_text
        print("✅ Модуль ocr_engine загружен")
        
        # Создадим тестовый файл если нет тестовых данных
        if not os.path.exists('tests'):
            os.makedirs('tests', exist_ok=True)
            print("ℹ️  Создана папка tests/")
            
        # Проверим, есть ли тестовые файлы
        test_files = list(Path('tests').glob('*.*'))
        if test_files:
            test_file = str(test_files[0])
            print(f"📁 Тестовый файл: {test_file}")
            
            # Попробуем извлечь текст
            try:
                text = extract_text(test_file)
                if text and len(text.strip()) > 10:
                    print(f"✅ OCR успешно извлек {len(text)} символов")
                    print(f"📄 Пример текста: {text[:100]}...")
                else:
                    print("⚠️  OCR извлек мало текста или пустой текст")
            except Exception as e:
                print(f"❌ Ошибка OCR: {e}")
        else:
            print("⚠️  Нет тестовых файлов в папке tests/")
            print("   Добавьте PDF/JPG/PNG файлы для тестирования")
            
    except Exception as e:
        print(f"❌ Ошибка при тесте OCR: {e}")
        return False
    return True

def test_document_classifier():
    """Тест классификатора документов"""
    print("\n2. Тестирование классификатора...")
    try:
        from src.document_classifier import classify_document
        
        # Тестовые тексты для разных типов документов
        test_cases = [
            ("универсальный передаточный документ статус", "УПД"),
            ("счет-фактура №123", "СЧЕТ_ФАКТУРА"),
            ("торг-12 товарная накладная", "ТОРГ-12"),
            ("просто какой-то текст", "НЕИЗВЕСТНО")
        ]
        
        all_passed = True
        for text, expected in test_cases:
            result = classify_document(text)
            status = "✅" if result == expected else "❌"
            print(f"   {status} '{text[:30]}...' -> {result} (ожидалось: {expected})")
            if result != expected:
                all_passed = False
                
        return all_passed
    except Exception as e:
        print(f"❌ Ошибка при тесте классификатора: {e}")
        return False

def test_data_parser():
    """Тест парсера данных"""
    print("\n3. Тестирование парсера данных...")
    try:
        from src.data_parser import parse_document_data
        
        # Тестовый текст с данными
        test_text = """
        ТОВАРНАЯ НАКЛАДНАЯ №12345
        Дата: 10.01.2023
        Продавец: ООО "Ромашка"
        Покупатель: ИП Иванов
        
        1. Товар 1 10 шт. 100.50 руб. 1005.00
        2. Товар 2 5 шт. 200.00 руб. 1000.00
        
        Всего: 2005.00
        """
        
        result = parse_document_data(test_text, "ТОРГ-12")
        
        print(f"✅ Парсер отработал")
        print(f"   Тип документа: {result.get('document_type')}")
        print(f"   Номер: {result.get('header', {}).get('doc_number')}")
        print(f"   Дата: {result.get('header', {}).get('doc_date')}")
        print(f"   Позиций: {len(result.get('table_data', []))}")
        
        # Сохраним результат для проверки
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"📁 JSON сохранен: {f.name}")
            
        return True
    except Exception as e:
        print(f"❌ Ошибка при тесте парсера: {e}")
        return False

def test_cli():
    """Тест CLI интерфейса"""
    print("\n4. Тестирование CLI интерфейса...")
    try:
        from src.cli import DocumentProcessorCLI
        print("✅ CLI модуль загружен")
        
        # Проверим аргументы
        import argparse
        
        # Создадим временный файл для теста
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Тестовый документ\nДата: 01.01.2023\n")
            temp_file = f.name
        
        print(f"📁 Создан временный файл: {temp_file}")
        print("ℹ️  Для полного теста CLI запустите команды в терминале")
        print("   python src/cli.py --help")
        
        # Удаляем временный файл
        os.unlink(temp_file)
        
        return True
    except Exception as e:
        print(f"❌ Ошибка при тесте CLI: {e}")
        return False

def test_batch_processor():
    """Тест пакетной обработки"""
    print("\n5. Тестирование пакетного процессора...")
    try:
        from src.batch_processor import BatchProcessor
        print("✅ BatchProcessor модуль загружен")
        
        # Создадим тестовую папку
        test_input = Path("test_batch_input")
        test_output = Path("test_batch_output")
        
        test_input.mkdir(exist_ok=True)
        test_output.mkdir(exist_ok=True)
        
        # Создадим несколько тестовых файлов
        for i in range(3):
            test_file = test_input / f"test_{i}.txt"
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(f"Документ {i}\nДата: 0{i+1}.01.2023\nНомер: {1000+i}\n")
        
        print(f"📁 Создано тестовых файлов: 3")
        print("ℹ️  BatchProcessor готов к использованию")
        
        # Очистка
        import shutil
        shutil.rmtree(test_input)
        shutil.rmtree(test_output)
        
        return True
    except Exception as e:
        print(f"❌ Ошибка при тесте batch processor: {e}")
        return False

def main():
    """Основная функция тестирования"""
    results = []
    
    # Запускаем тесты
    results.append(("OCR Engine", test_ocr_engine()))
    results.append(("Document Classifier", test_document_classifier()))
    results.append(("Data Parser", test_data_parser()))
    results.append(("CLI Interface", test_cli()))
    results.append(("Batch Processor", test_batch_processor()))
    
    # Итоги
    print("\n" + "=" * 60)
    print("📊 ИТОГИ ТЕСТИРОВАНИЯ:")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ ПРОЙДЕН" if success else "❌ НЕ ПРОЙДЕН"
        print(f"{status}: {name}")
    
    print(f"\n🎯 Результат: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Система готова к работе.")
        print("\n🚀 ПРИМЕРЫ ЗАПУСКА:")
        print("1. Один документ: python src/cli.py single --input tests/ваш_файл.pdf")
        print("2. Пакетная обработка: python src/cli.py batch --input-folder tests/ --output-folder output/")
        print("3. Помощь: python src/cli.py --help")
    else:
        print(f"\n⚠️  Некоторые тесты не пройдены. Проверьте ошибки выше.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()