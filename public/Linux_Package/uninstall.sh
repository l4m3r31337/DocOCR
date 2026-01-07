#!/bin/bash
# uninstall.sh - Удаление DocOCR

set -e

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN} ${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

echo "========================================"
echo "  Удаление DocOCR"
echo "========================================"
echo ""

if [ "$EUID" -ne 0 ]; then 
    print_error "Требуются права root. Запустите: sudo ./uninstall.sh"
    exit 1
fi

# 1. Удаление программы
echo "[1/4] Удаление программы..."
if [ -d "/opt/dococr" ]; then
    rm -rf /opt/dococr
    print_success "Удалена папка /opt/dococr"
else
    print_success "Папка /opt/dococr не найдена"
fi

# 2. Удаление симлинка
echo "[2/4] Удаление симлинка..."
if [ -L "/usr/local/bin/doc-processor" ]; then
    rm -f /usr/local/bin/doc-processor
    print_success "Удален симлинк /usr/local/bin/doc-processor"
else
    print_success "Симлинк не найден"
fi

# 3. Удаление логов
echo "[3/4] Удаление логов..."
if [ -d "/var/log/dococr" ]; then
    rm -rf /var/log/dococr
    print_success "Удалена папка логов /var/log/dococr"
else
    print_success "Папка логов не найдена"
fi

# 4. Удаление группы
echo "[4/4] Удаление группы..."
if getent group dococr >/dev/null; then
    groupdel dococr
    print_success "Удалена группа dococr"
else
    print_success "Группа dococr не найдена"
fi

echo ""
echo "========================================"
echo "  DocOCR полностью удален!"
echo "========================================"
echo ""
