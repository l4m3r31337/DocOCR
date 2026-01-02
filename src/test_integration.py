import sys
import os
import json
import logging

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Добавляем папку src в путь для импорта
sys.path.append('src')

from ocr_engine import extract_text
from document_classifier import classify_document
from data_parser import parse_document_data, save_to_json


def test_improved_parser():
    print("\n" + "=" * 70)
    print("🧪 ТЕСТИРОВАНИЕ УЛУЧШЕННОГО ПАРСЕРА")
    print("=" * 70)

    # Ищем все PDF файлы в tests
    tests_dir = "../tests"
    if not os.path.exists(tests_dir):
        print(f"❌ Папка tests не найдена: {tests_dir}")
        return

    pdf_files = [os.path.join(tests_dir, f) for f in os.listdir(tests_dir) if f.endswith('.pdf')]
    pdf_files.sort()

    if not pdf_files:
        print("❌ PDF файлы не найдены в папке tests")
        return

    print(f"📁 Найдено файлов для обработки: {len(pdf_files)}")

    # Создаем папку для результатов
    os.makedirs("../output", exist_ok=True)

    results_summary = []

    for file_path in pdf_files:
        if not os.path.exists(file_path):
            print(f"❌ Файл не найден: {file_path}")
            continue

        try:
            filename = os.path.basename(file_path)
            print(f"\n{'=' * 50}")
            print(f"📁 ФАЙЛ: {filename}")
            print('=' * 50)

            # 1. OCR извлекает текст
            print("🔍 Извлекаем текст OCR...")
            extracted_text = extract_text(file_path)

            if not extracted_text:
                print("❌ OCR не смог извлечь текст")
                results_summary.append((filename, "OCR_ERROR", "Не удалось извлечь текст"))
                continue

            text_length = len(extracted_text)
            print(f"📄 Извлечено символов: {text_length}")

            # Сохраняем извлеченный текст для отладки (только JSON, не txt)
            # text_filename = f"../output/{filename}_text.txt"  # Убрали сохранение txt

            # 2. Классификатор определяет тип
            print("🎯 Классифицируем документ...")
            doc_type = classify_document(extracted_text)
            print(f"📊 Тип документа: {doc_type}")

            # 3. Парсим данные улучшенным парсером
            print("🔧 Парсим структурированные данные (улучшенный парсер)...")
            parsed_data = parse_document_data(extracted_text, doc_type)

            # 4. Сохраняем в JSON
            output_filename = f"../output/{filename}_parsed.json"
            save_success = save_to_json(parsed_data, output_filename)

            if not save_success:
                print("❌ Не удалось сохранить JSON")
                continue

            # 5. Выводим результаты
            print("📋 РЕЗУЛЬТАТЫ ПАРСИНГА:")
            print(f"   • Тип документа: {parsed_data['document_type']}")

            header = parsed_data['header']
            print(f"   • Номер документа: {header.get('doc_number', 'не найден')}")
            print(f"   • Дата: {header.get('doc_date', 'не найдена')}")

            if 'seller' in header:
                seller = header['seller']
                if len(seller) > 50:
                    seller = seller[:47] + "..."
                print(f"   • Продавец: {seller}")
            if 'supplier' in header:
                supplier = header['supplier']
                if len(supplier) > 50:
                    supplier = supplier[:47] + "..."
                print(f"   • Поставщик: {supplier}")
            if 'buyer' in header:
                buyer = header['buyer']
                if len(buyer) > 50:
                    buyer = buyer[:47] + "..."
                print(f"   • Покупатель: {buyer}")
            if 'receiver' in header:
                receiver = header['receiver']
                if len(receiver) > 50:
                    receiver = receiver[:47] + "..."
                print(f"   • Грузополучатель: {receiver}")
            if 'status' in header:
                print(f"   • Статус УПД: {header['status']}")
                if 'status_description' in header:
                    print(f"     ({header['status_description']})")

            table_data = parsed_data['table_data']
            print(f"   • Найдено позиций: {len(table_data)}")

            # Показываем товары с правильными данными
            if table_data:
                print(f"   • Товары:")
                for i, item in enumerate(table_data[:5]):  # Покажем первые 5
                    product_name = item.get('product_name', 'не найден')
                    quantity = item.get('quantity', 0)
                    price = item.get('price', 0)
                    total = item.get('total', 0)

                    # Ограничиваем длину названия
                    if len(product_name) > 40:
                        product_name = product_name[:37] + "..."

                    # Показываем только если есть реальные данные
                    if quantity > 0 and price > 0:
                        print(f"     {i + 1:2d}. {product_name:40s} | {quantity:8.3f} x {price:8.2f} = {total:10.2f}")
                    else:
                        print(f"     {i + 1:2d}. {product_name:40s} | [неполные данные]")

                if len(table_data) > 5:
                    print(f"     ... и еще {len(table_data) - 5} позиций")

            # Итоги
            totals = parsed_data['totals']
            if totals and 'total_amount' in totals:
                print(f"   • Общая сумма: {totals['total_amount']:.2f}")

            # 6. Краткий JSON для отладки
            print("\n📄 КРАТКИЙ JSON (первые 600 символов):")
            print("-" * 50)

            # Создаем сокращенную версию для отображения
            preview_data = {
                "document_type": parsed_data["document_type"],
                "header": parsed_data["header"],
                "table_data_count": len(parsed_data["table_data"]),
                "totals": parsed_data["totals"]
            }

            # Добавляем первые 3 товара для примера
            if parsed_data["table_data"]:
                preview_data["table_data_sample"] = parsed_data["table_data"][:3]

            json_preview = json.dumps(preview_data, ensure_ascii=False, indent=2)

            # Показываем только первые 600 символов
            if len(json_preview) > 600:
                print(json_preview[:600] + "...")
            else:
                print(json_preview)

            print("-" * 50)

            # 7. Проверяем качество парсинга
            success = True
            issues = []

            if not header.get('doc_number'):
                issues.append("Номер документа не найден")
                success = False

            if not header.get('doc_date'):
                issues.append("Дата документа не найдена")
                success = False

            if not table_data:
                issues.append("Табличные данные не найдены")
                success = False
            else:
                # Проверяем, что есть товары с реальными данными
                valid_items = sum(1 for item in table_data if item.get('quantity', 0) > 0 and item.get('price', 0) > 0)
                if valid_items == 0:
                    issues.append("Товары без числовых данных")
                    success = False

            if success:
                print("✅ Парсинг успешен!")
                results_summary.append((filename, "SUCCESS", f"Найдено {len(table_data)} позиций"))
            else:
                print(f"⚠️  Проблемы с парсингом: {', '.join(issues)}")
                results_summary.append((filename, "PARTIAL", f"Проблемы: {', '.join(issues)}"))

        except Exception as e:
            print(f"❌ КРИТИЧЕСКАЯ ОШИБКА при обработке {file_path}: {e}")
            import traceback
            traceback.print_exc()
            results_summary.append((filename, "ERROR", str(e)))

    # Итоговая сводка
    print("\n" + "=" * 70)
    print("📊 ИТОГОВАЯ СВОДКА:")
    print("=" * 70)

    success_count = sum(1 for _, status, _ in results_summary if status == "SUCCESS")
    partial_count = sum(1 for _, status, _ in results_summary if status == "PARTIAL")
    error_count = sum(1 for _, status, _ in results_summary if status in ["ERROR", "OCR_ERROR"])

    print(f"✅ Успешно обработано: {success_count}")
    print(f"⚠️  Частично обработано: {partial_count}")
    print(f"❌ С ошибками: {error_count}")
    print(f"📂 Всего файлов: {len(results_summary)}")

    print("\n📋 Детали по файлам:")
    for filename, status, message in results_summary:
        status_icon = "✅" if status == "SUCCESS" else "⚠️ " if status == "PARTIAL" else "❌"
        print(f"  {status_icon} {filename:30s} - {status:10s} - {message}")


if __name__ == "__main__":
    test_improved_parser()