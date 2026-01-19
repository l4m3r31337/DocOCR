#!/bin/bash

echo "Проверка наличия Python 3.11..."

# Проверяем разные варианты python
for cmd in python3.11 python3; do
    if command -v $cmd &> /dev/null; then
        version=$($cmd --version 2>&1 | awk '{print $2}')
        major=$(echo $version | cut -d. -f1)
        minor=$(echo $version | cut -d. -f2)
        
        if [ $major -eq 3 ] && [ $minor -ge 11 ]; then
            echo "[OK] Найден $cmd версии $version"
            exit 0
        fi
    fi
done

echo "[INFO] Python 3.11+ не найден"
exit 1