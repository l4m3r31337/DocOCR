#!/bin/bash

TEMP_DIR=$1

echo "Установка Python 3.11..."

# Определяем дистрибутив
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
    VERSION=$VERSION_ID
else
    DISTRO="unknown"
fi

echo "Дистрибутив: $DISTRO $VERSION"

case $DISTRO in
    ubuntu|debian|astra)
        # Для Debian-based систем
        apt-get update
        apt-get install -y software-properties-common
        
        # Добавляем deadsnakes PPA (для свежих версий Python)
        add-apt-repository -y ppa:deadsnakes/ppa
        apt-get update
        apt-get install -y python3.11 python3.11-venv python3.11-dev
        
        # Создаем альтернативы
        update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
        update-alternatives --set python3 /usr/bin/python3.11
        
        # Устанавливаем pip для Python 3.11
        curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11
        
        echo "[OK] Python 3.11 установлен через apt"
        ;;
        
    *)
        # Для других дистрибутивов - сборка из исходников
        echo "Сборка Python 3.11 из исходников..."
        
        cd "$TEMP_DIR"
        wget https://www.python.org/ftp/python/3.11.9/Python-3.11.9.tgz
        tar -xzf Python-3.11.9.tgz
        cd Python-3.11.9
        
        # Устанавливаем зависимости для сборки
        apt-get update
        apt-get install -y build-essential zlib1g-dev libncurses5-dev \
            libgdbm-dev libnss3-dev libssl-dev libreadline-dev \
            libffi-dev libsqlite3-dev wget libbz2-dev
        
        ./configure --enable-optimizations
        make -j$(nproc)
        make altinstall
        
        # Создаем симлинк
        ln -sf /usr/local/bin/python3.11 /usr/local/bin/python3
        
        # Устанавливаем pip
        curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11
        
        echo "[OK] Python 3.11 собран из исходников"
        ;;
esac

# Проверка
python3.11 --version
pip3 --version