#!/bin/bash

echo "========================================"
echo "  Doc-Processor Installer v1.0"
echo "========================================"

# Проверка прав root
if [[ $EUID -ne 0 ]]; then
   echo "[ОШИБКА] Требуются права root!"
   echo "Запустите: sudo ./install.sh"
   exit 1
fi

INSTALL_DIR="/opt/doc-processor"
LOG_DIR="/var/log/doc-processor"
TEMP_DIR="/tmp/doc-processor-install"

echo "Установка в: $INSTALL_DIR"
echo "Логи в: $LOG_DIR"
echo "Временные файлы: $TEMP_DIR"

# Создание директорий
mkdir -p "$INSTALL_DIR"
mkdir -p "$LOG_DIR"
mkdir -p "$TEMP_DIR"
mkdir -p "$INSTALL_DIR/src"
mkdir -p "$INSTALL_DIR/utils"

# Логирование
LOG_FILE="$LOG_DIR/install.log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo ""
echo "[1/7] Проверка Python 3.11..."
if ! ./scripts/check_python.sh; then
    echo "Установка Python 3.11..."
    ./scripts/install_python.sh "$TEMP_DIR"
else
    echo "Python 3.11+ уже установлен."
fi

echo ""
echo "[2/7] Установка Tesseract OCR с русским языком..."
./scripts/install_tesseract.sh "$TEMP_DIR" "$INSTALL_DIR"

echo ""
echo "[3/7] Установка Poppler..."
./scripts/install_poppler.sh "$TEMP_DIR" "$INSTALL_DIR"

echo ""
echo "[4/7] Установка Ghostscript..."
./scripts/install_ghostscript.sh "$TEMP_DIR" "$INSTALL_DIR"

echo ""
echo "[5/7] Настройка переменных окружения..."
./scripts/setup_path.sh "$INSTALL_DIR"

echo ""
echo "[6/7] Копирование файлов программы..."
cp -r src/* "$INSTALL_DIR/src/"
cp run.py requirements.txt "$INSTALL_DIR/"
cp -r utils/* "$INSTALL_DIR/utils/"
chmod +x "$INSTALL_DIR/utils/doc-processor"
chmod +x "$INSTALL_DIR/utils/uninstall.sh"

echo ""
echo "[7/7] Установка Python-зависимостей..."
cd "$INSTALL_DIR"

# Определяем версию Python
PY_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Версия Python: $PY_VERSION"

# Устанавливаем venv для конкретной версии
echo "Установка python3-venv..."
if apt-cache show "python${PY_VERSION}-venv" &> /dev/null; then
    apt-get install -y "python${PY_VERSION}-venv"
else
    apt-get install -y python3-venv
fi

# Создаем venv
echo "Создание виртуального окружения..."
python3 -m venv venv

# Проверяем что venv создался
if [ ! -f "venv/bin/python3" ]; then
    echo "ОШИБКА: Не удалось создать venv. Используем альтернативный метод..."
    # Альтернатива: установка пакетов через apt
    apt-get install -y python3-pil python3-pytesseract python3-pdf2image python3-magic
else
    echo "Использование виртуального окружения..."
    # Используем абсолютные пути
    VENV_PYTHON="$INSTALL_DIR/venv/bin/python3"
    VENV_PIP="$INSTALL_DIR/venv/bin/pip"
    
    echo "Обновление pip..."
    "$VENV_PIP" install --upgrade pip
    
    echo "Установка зависимостей..."
    if [ -f "requirements.txt" ]; then
        "$VENV_PIP" install -r requirements.txt
    else
        "$VENV_PIP" install pillow pytesseract pdf2image python-magic
    fi
    
    # Обновляем run.py
    echo "Настройка run.py..."
    if [ -f "run.py" ]; then
        # Сохраняем оригинал
        cp run.py run.py.backup
        # Добавляем shebang
        echo "#!/opt/doc-processor/venv/bin/python3" > run.py
        cat run.py.backup >> run.py
        rm -f run.py.backup
        chmod 755 run.py  # ВАЖНО: права на выполнение
    fi
fi

# Обновляем утилиту doc-processor
echo "Настройка команды doc-processor..."
cat > utils/doc-processor << 'EOF'
#!/bin/bash
/opt/doc-processor/venv/bin/python3 /opt/doc-processor/run.py "$@"
EOF
chmod 755 utils/doc-processor  # ВАЖНО: права на выполнение

# Создаем ссылку в /usr/local/bin
echo "Создание глобальной команды..."
ln -sf /opt/doc-processor/utils/doc-processor /usr/local/bin/doc-processor
chmod 755 /usr/local/bin/doc-processor 2>/dev/null || true

# НАСТРОЙКА ПРАВ ДОСТУПА ДЛЯ ВСЕХ ПОЛЬЗОВАТЕЛЕЙ
echo "Настройка прав доступа для многопользовательского режима..."
chmod -R 755 "$INSTALL_DIR" 2>/dev/null || true
chmod -R a+r "$INSTALL_DIR" 2>/dev/null || true
find "$INSTALL_DIR" -type f -name "*.py" -exec chmod 644 {} \; 2>/dev/null || true
find "$INSTALL_DIR" -type f -name "*.sh" -exec chmod 755 {} \; 2>/dev/null || true

# Даем права на логи
chmod 777 "$LOG_DIR" 2>/dev/null || true
chmod 666 "$LOG_FILE" 2>/dev/null || true

echo "Права доступа настроены. Программа доступна всем пользователям."

echo ""
echo "========================================"
echo "  УСТАНОВКА ЗАВЕРШЕНА!"
echo "========================================"
echo ""
echo "Программа установлена в: $INSTALL_DIR"
echo ""
echo "Доступные команды:"
echo "  doc-processor --help"
echo "  doc-processor single --input /путь/к/файлу.pdf"
echo "  doc-processor batch --input-folder /папка --output-folder /папка"
echo ""
echo "Для удаления программы запустите:"
echo "  $INSTALL_DIR/utils/uninstall.sh"
echo ""
echo "Логи установки: $LOG_FILE"