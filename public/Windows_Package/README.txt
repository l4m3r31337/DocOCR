CLI СИСТЕМА РАСПОЗНАВАНИЯ БУХГАЛТЕРСКИХ ДОКУМЕНТОВ
================================================

УСТАНОВКА:
1. Запустите install.bat от имени Администратора
2. Дождитесь завершения установки
3. Перезапустите командную строку

ИСПОЛЬЗОВАНИЕ (только из командной строки):

1. Обработка одного документа:
   doc-processor single --input "путь\к\файлу.pdf"

2. Пакетная обработка:
   doc-processor batch --input-folder "папка" --output-folder "результаты"

3. Пропуск обработанных файлов:
   doc-processor batch --input-folder "папка" --output-folder "результаты" --skip-existing

4. Параллельная обработка:
   doc-processor batch --input-folder "папка" --output-folder "результаты" --workers 4

5. Справка:
   doc-processor --help
   doc-processor single --help
   doc-processor batch --help

ПОДДЕРЖИВАЕМЫЕ ФОРМАТЫ:
- PDF (.pdf)
- Изображения (.jpg, .jpeg, .png)

РЕЗУЛЬТАТ:
Для каждого документа создается JSON файл с распознанными данными.

ПРОГРАММА УСТАНАВЛИВАЕТ:
- Python 3.11
- Tesseract OCR с русским языком
- Poppler 25.07.0 для работы с PDF
- Все необходимые зависимости