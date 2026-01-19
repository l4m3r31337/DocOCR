@echo off
setlocal

set INSTALL_DIR=C:\Program Files\DocProcessor

REM Проверка установки
if not exist "%INSTALL_DIR%\run.py" (
    echo Программа Doc-Processor не установлена.
    echo Запустите install.bat для установки.
    pause
    exit /b 1
)

REM Переход в директорию установки
cd /d "%INSTALL_DIR%"

REM Настройка переменных окружения
set POLLER_PATH=%INSTALL_DIR%\poppler
set TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe

REM Проверка зависимостей
if not exist "%TESSERACT_CMD%" (
    echo Ошибка: Tesseract не найден.
    echo Установите Tesseract OCR или проверьте путь.
    exit /b 1
)

REM Запуск программы
python run.py %*

endlocal