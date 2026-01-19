Doc-Processor v1.0 - Система распознавания бухгалтерских документов
====================================================================

ТРЕБОВАНИЯ:
- Astra Linux (Debian/Ubuntu based)
- Права root (sudo)
- Интернет-соединение
- ~1 ГБ свободного места

УСТАНОВКА:
1. Распакуйте архив:
   tar -xzf doc-processor-1.0-Linux.tar.gz
   cd doc-processor-1.0-Linux

2. Запустите установщик с правами root:
   sudo ./install.sh

3. Следуйте инструкциям на экране

ПРОВЕРКА УСТАНОВКИ:
   doc-processor --help

ИСПОЛЬЗОВАНИЕ:
Обработка одного документа:
   doc-processor single --input "/путь/к/документу.pdf"

Пакетная обработка:
   doc-processor batch --input-folder "/входная/папка" --output-folder "/выходная/папка"

Для подробной справки:
   doc-processor --help

ПУТИ УСТАНОВКИ:
- Программа: /opt/doc-processor
- Логи установки: /var/log/doc-processor/install.log
- Файл окружения: /etc/profile.d/doc-processor.sh

УДАЛЕНИЕ:
   sudo /opt/doc-processor/utils/uninstall.sh

ПОДДЕРЖКА:
При проблемах проверьте:
1. Запущен ли install.sh с sudo
2. Есть ли интернет-соединение
3. Проверьте логи: cat /var/log/doc-processor/install.log

УСТАНОВЛЕННЫЕ ЗАВИСИМОСТИ:
- Python 3.11
- Tesseract OCR с русским языком
- Poppler-utils
- Ghostscript
- Все Python-пакеты из requirements.txt