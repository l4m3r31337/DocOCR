#!/bin/bash
# Упрощенный установщик с поддержкой requirements.txt

set -e

echo "=== Установка DocOCR ==="

# Обновление
apt-get update
apt-get upgrade -y

# Только необходимые пакеты (без libgl1-mesa-glx)
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    tesseract-ocr \
    tesseract-ocr-rus \
    tesseract-ocr-eng \
    poppler-utils \
    libsm6 \
    libxext6 \
    libglib2.0-0

# Виртуальное окружение
mkdir -p /opt/dococr
python3 -m venv /opt/dococr/venv
source /opt/dococr/venv/bin/activate

# Обновление pip
pip install --upgrade pip

# Установка Python пакетов из requirements.txt или стандартных
if [ -f "requirements.txt" ]; then
    echo "Установка зависимостей из requirements.txt..."
    pip install -r requirements.txt
else
    echo "requirements.txt не найден, устанавливаю стандартные пакеты..."
    pip install pytesseract pdf2image Pillow PyPDF2 opencv-python-headless
fi

# Копируем программу
cp doc-processor /opt/dococr/
chmod +x /opt/dococr/doc-processor
ln -sf /opt/dococr/doc-processor /usr/local/bin/doc-processor

# Копируем src если есть
if [ -d "src" ]; then
    cp -r src /opt/dococr/
    echo "Папка src скопирована"
fi

# Копируем requirements.txt если есть
if [ -f "requirements.txt" ]; then
    cp requirements.txt /opt/dococr/
    echo "requirements.txt скопирован"
fi

echo "Готово! Используйте: doc-processor --help"