#!/bin/bash

TEMP_DIR=$1
INSTALL_DIR=$2

echo "Установка Ghostscript..."

# Устанавливаем через apt
apt-get update
apt-get install -y ghostscript

# Проверка
if command -v gs &> /dev/null; then
    GS_VERSION=$(gs --version)
    echo "[OK] Ghostscript установлен, версия: $GS_VERSION"
    
    # Сохраняем путь
    GS_CMD=$(which gs)
    echo "$GS_CMD" > "$INSTALL_DIR/ghostscript_path.txt"
else
    echo "[ERROR] Не удалось установить Ghostscript"
    exit 1
fi