#!/bin/bash

TEMP_DIR=$1
INSTALL_DIR=$2

echo "Установка Poppler..."

# Устанавливаем через apt
apt-get update
apt-get install -y poppler-utils

# Проверка
if command -v pdftoppm &> /dev/null; then
    echo "[OK] Poppler установлен"
    
    # Проверяем версию
    POPPLER_VERSION=$(pdftoppm -v 2>&1 | head -n1 | grep -o '[0-9]\+\.[0-9]\+')
    echo "Версия Poppler: $POPPLER_VERSION"
    
    # Сохраняем информацию
    echo "pdftoppm: $(which pdftoppm)" > "$INSTALL_DIR/poppler_info.txt"
else
    echo "[ERROR] Не удалось установить Poppler"
    exit 1
fi