# CLI Система распознавания бухгалтерских документов для Linux

## Поддерживаемые дистрибутивы:
- Astra Linux Special Edition
- Debian 10/11/12
- Ubuntu 20.04/22.04
- Linux Mint

## Установка:

1. Скачайте архив `DocOCR_Linux.tar.gz`
2. Распакуйте: `tar -xzf DocOCR_Linux.tar.gz`
3. Перейдите в папку: `cd DocOCR_Linux`
4. Запустите установку: `sudo ./install.sh`

## Использование:

### Базовые команды:
```bash
# Один документ
doc-processor single --input документ.pdf --output результат.json

# Пакетная обработка  
doc-processor batch --input-folder ./документы --output-folder ./результаты

# Пропуск обработанных
doc-processor batch --input-folder ./документы --output-folder ./результаты --skip-existing

# Параллельная обработка
doc-processor batch --input-folder ./документы --output-folder ./результаты --workers 4

# Справка
doc-processor --help