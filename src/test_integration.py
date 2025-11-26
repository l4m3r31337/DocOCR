import sys
import os
import json

# Добавляем папку src в путь для импорта
sys.path.append('src')

from ocr_engine import extract_text
from document_classifier import classify_document
from data_parser import parse_document_data, save_to_json


def test_classifier():
    print("=" * 60)

    tests_dir = "../tests"
    if not os.path.exists(tests_dir):
        print(f"Папка не найдена: {tests_dir}")
        return

    pdf_files = [os.path.join(tests_dir, f) for f in os.listdir(tests_dir) if f.endswith('.pdf')]

    if not pdf_files:
        print("PDF файлы не найдены")
        return

    print(f"Файлов для обработки: {len(pdf_files)}")

    # Создаем папку для результатов
    os.makedirs("../output", exist_ok=True)

    for file_path in pdf_files:
        if not os.path.exists(file_path):
            print(f"Файл не найден: {file_path}")
            continue

        try:
            filename = os.path.basename(file_path)
            print(f"\nОбрабатываем: {filename}")

            
            print("текст OCR...")
            extracted_text = extract_text(file_path)

            if not extracted_text:
                print("OCR не смог извлечь текст")
                continue


            
            doc_type = classify_document(extracted_text)
            print(f"Тип документа: {doc_type}")

            
            parsed_data = parse_document_data(extracted_text, doc_type)

            output_filename = f"../output/{filename}_parsed.json"
            save_to_json(parsed_data, output_filename)

            print("РЕЗУЛЬТАТЫ ПАРСИНГА:")
            print(f"   • Тип документа: {parsed_data['document_type']}")
            print(f"   • Номер документа: {parsed_data['header'].get('doc_number', 'не найден')}")
            print(f"   • Дата: {parsed_data['header'].get('doc_date', 'не найдена')}")

            if 'seller' in parsed_data['header']:
                print(f"   • Продавец: {parsed_data['header']['seller']}")
            if 'supplier' in parsed_data['header']:
                print(f"   • Поставщик: {parsed_data['header']['supplier']}")

            print(f"   • Найдено позиций: {len(parsed_data['table_data'])}")

            # Покажем пример товара
            if parsed_data['table_data']:
                first_item = parsed_data['table_data'][0]
                print(f"   • Пример товара: {first_item.get('product_name', 'не найден')}")

            # 6. Покажем краткое содержимое JSON
            print("Краткое содержимое JSON:")
            print("-" * 40)
            json_preview = json.dumps(parsed_data, ensure_ascii=False, indent=2)
            # Покажем только первые 400 символов чтобы не засорять вывод
            if len(json_preview) > 400:
                print(json_preview[:400] + "...")
            else:
                print(json_preview)
            print("-" * 40)

        except Exception as e:
            print(f"Ошибка при обработке {file_path}: {e}")

    print(f"\nОБРАБОТКА ЗАВЕРШЕНА!")
    print(f"Результаты сохранены в папку: ../output/")
    print(f"Обработано файлов: {len([f for f in os.listdir('../output') if f.endswith('.json')])}")


if __name__ == "__main__":
    test_classifier()