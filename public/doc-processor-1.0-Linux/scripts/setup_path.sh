#!/bin/bash

INSTALL_DIR=$1

echo "Настройка переменных окружения..."

# Создаем системный скрипт для окружения
ENV_FILE="/etc/profile.d/doc-processor.sh"

cat > "$ENV_FILE" << EOF
#!/bin/bash
# Настройка окружения для Doc-Processor

export DOC_PROCESSOR_HOME="$INSTALL_DIR"
export PATH="\$PATH:$INSTALL_DIR/utils"

# Настройка Tesseract (если не в PATH)
if [ -f "$INSTALL_DIR/tesseract_path.txt" ]; then
    TESSERACT_CMD=\$(cat "$INSTALL_DIR/tesseract_path.txt")
    export TESSERACT_CMD
fi

# Настройка Poppler
if [ -d "$INSTALL_DIR/poppler" ]; then
    export POPPLER_PATH="$INSTALL_DIR/poppler"
fi

# Настройка Ghostscript
if [ -f "$INSTALL_DIR/ghostscript_path.txt" ]; then
    export GS_CMD=\$(cat "$INSTALL_DIR/ghostscript_path.txt")
fi
EOF

chmod +x "$ENV_FILE"

# Создаем симлинк в /usr/local/bin для удобства
ln -sf "$INSTALL_DIR/utils/doc-processor" /usr/local/bin/doc-processor

# Применяем изменения в текущей сессии
source "$ENV_FILE"

export DOC_PROCESSOR_HOME="$INSTALL_DIR"
# Пути будут в tesseract_path.txt и poppler_path.txt

echo "[OK] Настройка окружения завершена"
echo "Файл окружения: $ENV_FILE"