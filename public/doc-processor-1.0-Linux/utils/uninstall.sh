#!/bin/bash

echo "========================================"
echo "  Удаление Doc-Processor"
echo "========================================"

INSTALL_DIR="/opt/doc-processor"
ENV_FILE="/etc/profile.d/doc-processor.sh"

if [ "$EUID" -ne 0 ]; then 
    echo "Требуются права root. Запустите: sudo $0"
    exit 1
fi

echo "Это удалит программу, но НЕ удалит:"
echo "  - Python 3.11"
echo "  - Tesseract OCR"
echo "  - Poppler"
echo "  - Ghostscript"
echo ""
read -p "Продолжить удаление? (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Удаление отменено."
    exit 0
fi

# Удаление файлов программы
if [ -d "$INSTALL_DIR" ]; then
    echo "Удаление файлов программы..."
    rm -rf "$INSTALL_DIR"
    echo "Файлы программы удалены."
fi

# Удаление файла окружения
if [ -f "$ENV_FILE" ]; then
    echo "Удаление файла окружения..."
    rm -f "$ENV_FILE"
fi

# Удаление симлинка
if [ -L "/usr/local/bin/doc-processor" ]; then
    echo "Удаление симлинка..."
    rm -f "/usr/local/bin/doc-processor"
fi

echo ""
echo "========================================"
echo "  Удаление завершено!"
echo "========================================"
echo ""
echo "Остались установленными:"
echo "  - Python 3.11"
echo "  - Tesseract OCR"
echo "  - Poppler"
echo "  - Ghostscript"
echo ""
echo "Для полного удаления этих программ выполните:"
echo "  sudo apt-get remove python3.11 tesseract-ocr poppler-utils ghostscript"
echo "  sudo apt-get autoremove"