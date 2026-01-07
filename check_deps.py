# check_deps.py - простой скрипт проверки
import sys
import os

print("=" * 60)
print("🔍 ПРОВЕРКА СИСТЕМЫ")
print("=" * 60)

# 1. Проверка Python
print("\n1. Проверка Python версии...")
print(f"Python {sys.version}")
if sys.version_info < (3, 7):
    print("❌ Требуется Python 3.7+")
    sys.exit(1)
else:
    print("✅ Версия Python OK")

# 2. Проверка модулей
print("\n2. Проверка Python модулей...")
modules = [
    'pytesseract', 'pdf2image', 'PIL', 'argparse', 
    'concurrent.futures', 'logging', 'json', 're', 'datetime'
]

for module in modules:
    try:
        __import__(module)
        print(f"✅ {module}")
    except ImportError:
        print(f"❌ {module} - не установлен")

# 3. Проверка структуры проекта
print("\n3. Проверка структуры проекта...")
required_files = [
    'src/ocr_engine.py',
    'src/document_classifier.py',
    'src/data_parser.py',
    'src/table_extractor.py',
    'src/validator.py'
]

new_files = [
    'src/cli.py',
    'src/batch_processor.py',
    'src/logger_config.py'
]

all_ok = True
for file in required_files + new_files:
    if os.path.exists(file):
        print(f"✅ {file}")
    else:
        print(f"❌ {file} - не найден")
        all_ok = False

# 4. Проверка тестовых документов
print("\n4. Проверка тестовых документов...")
if os.path.exists('tests'):
    test_files = os.listdir('tests')
    if test_files:
        print(f"✅ Найдено {len(test_files)} тестовых файлов в tests/")
        for file in test_files[:5]:  # покажем первые 5
            print(f"  - {file}")
        if len(test_files) > 5:
            print(f"  ... и ещё {len(test_files)-5}")
    else:
        print("⚠️  Папка tests/ пуста")
else:
    print("ℹ️  Папка tests/ не найдена. Создайте её и добавьте документы.")

print("\n" + "=" * 60)
print("📝 РЕКОМЕНДАЦИИ:")
print("1. Запустите: pip install -r requirements.txt")
print("2. Установите Tesseract и Poppler (см. инструкцию)")
print("3. Запустите тест: python run_test.py")
print("=" * 60)