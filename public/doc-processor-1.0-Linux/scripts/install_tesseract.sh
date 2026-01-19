#!/bin/bash

TEMP_DIR=$1
INSTALL_DIR=$2

echo "Установка Tesseract OCR..."

# Установка через apt
apt-get update
apt-get install -y tesseract-ocr tesseract-ocr-rus

# Дополнительные языковые пакеты (опционально)
apt-get install -y tesseract-ocr-eng tesseract-ocr-script-cyrl

# Проверка установки
if command -v tesseract &> /dev/null; then
    TESSERACT_VERSION=$(tesseract --version | head -n1)
    echo "[OK] $TESSERACT_VERSION"
    
    # Проверка русского языка
    if tesseract --list-langs 2>/dev/null | grep -q "rus"; then
        echo "[OK] Русский язык доступен"
    else
        echo "[WARN] Русский язык не найден, устанавливаем..."
        
        # Скачиваем русские языковые файлы
        cd "$TEMP_DIR"
        wget https://github.com/tesseract-ocr/tessdata/raw/main/rus.traineddata
        TESSDATA_DIR=$(tesseract --print-parameters 2>&1 | grep tessdata | head -1 | cut -d: -f2 | xargs)
        
        if [ -n "$TESSDATA_DIR" ] && [ -d "$TESSDATA_DIR" ]; then
            cp rus.traineddata "$TESSDATA_DIR/"
            echo "[OK] Русский язык установлен вручную"
        else
            echo "[ERROR] Не удалось найти tessdata директорию"
        fi
    fi
    
    # Сохраняем путь к tesseract
    TESSERACT_CMD=$(which tesseract)
    echo "$TESSERACT_CMD" > "$INSTALL_DIR/tesseract_path.txt"
    
else
    echo "[ERROR] Не удалось установить Tesseract"
    exit 1
fi