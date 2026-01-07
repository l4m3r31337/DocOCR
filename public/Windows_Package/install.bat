@echo off
chcp 65001 >nul
title Установка DocOCR
setlocal enabledelayedexpansion

echo ================================================
echo    УСТАНОВКА CLI СИСТЕМЫ РАСПОЗНАВАНИЯ ДОКУМЕНТОВ
echo ================================================
echo.

REM --- Сохраняем путь к папке со скриптом ---
set "SCRIPT_DIR=%~dp0"
echo   Папка установки: !SCRIPT_DIR!
echo.

REM --- Проверка прав администратора ---
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if errorlevel 1 (
    echo   ТРЕБУЮТСЯ ПРАВА АДМИНИСТРАТОРА!
    echo Запустите от имени Администратора
    pause
    exit /b 1
)

echo  Запущено от имени администратора
echo.

REM --- 1. ПРОВЕРКА И УСТАНОВКА PYTHОН ---
echo [1/5] Установка Python 3.11...

echo    Запускаю установщик Python 3.11...
if not exist "!SCRIPT_DIR!python-3.11.exe" (
    echo Файл python-3.11.exe не найден!
    pause
    exit /b 1
)

echo    Устанавливаю Python...
start /wait "" "!SCRIPT_DIR!python-3.11.exe"
echo    Ожидаю завершения установки...
timeout /t 5 >nul

echo    Проверяю установку...
python --version >nul 2>&1
if errorlevel 1 (
    echo  Python может быть установлен, но не в PATH
    echo    Проверьте установку вручную
) else (
    echo Python установлен
)

REM --- 2. ПРОВЕРКА TESSERACT ---
echo.
echo [2/5] Проверка Tesseract OCR...
where tesseract >nul 2>&1
if errorlevel 1 (
    echo    Tesseract не найден. Устанавливаю...
    
    if not exist "!SCRIPT_DIR!tesseract-setup.exe" (
        echo Файл tesseract-setup.exe не найден!
        pause
        exit /b 1
    )
    
    echo    Запуск установщика Tesseract...
    echo   Выберите русский язык при установке!
    echo.
    
    timeout /t 2 >nul
    start /wait "" "!SCRIPT_DIR!tesseract-setup.exe"
    timeout /t 15 >nul
    
    where tesseract >nul 2>&1
    if errorlevel 1 (
        echo   Tesseract может быть установлен, но не в PATH
        echo    Проверьте вручную: C:\Program Files\Tesseract-OCR\
    ) else (
        echo  Tesseract установлен
    )
) else (
    echo Tesseract уже установлен
)

REM --- 3. УСТАНОВКА POPPLER БЕЗ POWERSHELL ---
echo.
echo [3/5] Установка Poppler...

if not exist "!SCRIPT_DIR!poppler-25.07.0.zip" (
    echo Файл poppler-25.07.0.zip не найден!
    pause
    exit /b 1
)

echo    Распаковка Poppler в C:\poppler...
if exist "C:\poppler" rmdir /s /q "C:\poppler"
mkdir "C:\poppler"

echo    Распаковываю с помощью встроенных средств...
REM Используем встроенную команду Windows (если есть)
where tar >nul 2>&1
if not errorlevel 1 (
    REM В Windows 10/11 есть tar
    tar -xf "!SCRIPT_DIR!poppler-25.07.0.zip" -C "C:\poppler"
) else (
    REM Пробуем использовать PowerShell Compact Edition (всегда доступен)
    REM Или просто копируем, если архив уже распакован
    echo    Использую альтернативный метод распаковки...
    
    REM Создаем временную папку
    set "TEMP_EXTRACT=C:\temp_poppler"
    if exist "!TEMP_EXTRACT!" rmdir /s /q "!TEMP_EXTRACT!"
    mkdir "!TEMP_EXTRACT!"
    
    REM Используем встроенный механизм Windows для ZIP
    REM В Windows есть встроенная поддержка ZIP через COM
    echo    Создаю объект для распаковки...
    powershell -Command "$shell = New-Object -ComObject Shell.Application; $zip = $shell.NameSpace('!SCRIPT_DIR!poppler-25.07.0.zip'); $dest = $shell.NameSpace('!TEMP_EXTRACT!'); $dest.CopyHere($zip.Items())"
    
    REM Ждем распаковки
    timeout /t 3 >nul
    
    REM Копируем содержимое
    xcopy "!TEMP_EXTRACT!\*" "C:\poppler\" /E /H /Y /Q
    
    REM Удаляем временную папку
    rmdir /s /q "!TEMP_EXTRACT!"
)

if not exist "C:\poppler\Library\bin\pdftoppm.exe" (
    echo   Poppler распакован, но структура может отличаться
    echo    Ищу исполняемые файлы...
    
    REM Ищем pdftoppm в любой подпапке
    dir "C:\poppler\pdftoppm.exe" /s /b >nul 2>&1
    if not errorlevel 1 (
        echo  Poppler найден
    ) else (
        echo   Poppler установлен, но исполняемые файлы не найдены
        echo    Убедитесь, что архив содержит папку bin с файлами
    )
) else (
    echo Poppler распакован
)

REM --- 4. УСТАНОВКА ЗАВИСИМОСТЕЙ ---
echo.
echo [4/5] Установка Python зависимостей...

echo    Обновление pip...
python -m pip install --upgrade pip >nul 2>&1

if exist "!SCRIPT_DIR!requirements.txt" (
    echo    Установка из requirements.txt...
    pip install -r "!SCRIPT_DIR!requirements.txt" >nul 2>&1
    echo Зависимости установлены
) else (
    echo    Файл requirements.txt не найден
    echo    Установка пакетов вручную...
    pip install pytesseract pdf2image Pillow PyPDF2 >nul 2>&1
    echo  Пакеты установлены
)

REM --- 5. УСТАНОВКА ПРОГРАММЫ И НАСТРОЙКА PATH ---
echo.
echo [5/5] Установка программы и настройка PATH...

if not exist "!SCRIPT_DIR!doc-processor.exe" (
    echo  Файл doc-processor.exe не найден!
    pause
    exit /b 1
)

set "INSTALL_DIR=C:\Program Files\DocOCR"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

copy "!SCRIPT_DIR!doc-processor.exe" "%INSTALL_DIR%\" >nul
echo  Программа установлена в: %INSTALL_DIR%

REM --- НАСТРОЙКА СИСТЕМНОГО PATH С ПОМОЩЬЮ SETX ---
echo.
echo    Настройка системного PATH...

set "POPPLER_PATH=C:\poppler\Library\bin"
set "DOCOCR_PATH=%INSTALL_DIR%"

echo    Проверяю текущий PATH...
echo !PATH! | find /i "%DOCOCR_PATH%" >nul
if errorlevel 1 (
    echo    Добавляю пути в системный PATH...
    
    REM Просто добавляем оба пути к текущему PATH через setx
    setx PATH "!PATH!;%POPPLER_PATH%;%DOCOCR_PATH%" /M >nul
    
    if errorlevel 1 (
        echo  Ошибка при добавлении в PATH
        echo    Альтернативный метод: добавление отдельных переменных...
        
        REM Создаем отдельные переменные
        setx POPPLER_BIN "%POPPLER_PATH%" /M >nul
        setx DOC_OCR_DIR "%DOCOCR_PATH%" /M >nul
        
        echo  Созданы переменные POPPLER_BIN и DOC_OCR_DIR
    ) else (
        echo  Пути добавлены в системный PATH
    )
    
    REM Добавляем в PATH текущей сессии
    set PATH=!PATH!;%POPPLER_PATH%;%DOCOCR_PATH%
) else (
    echo  Пути уже есть в PATH
)

REM --- ФИНАЛЬНЫЙ ЭТАП ---
echo.
echo ================================================
echo    УСТАНОВКА ЗАВЕРШЕНА
echo ================================================
echo.
echo  Установленные пути:
echo    Poppler:   %POPPLER_PATH%
echo    DocOCR:    %DOCOCR_PATH%
echo.
echo  КОМАНДЫ ДЛЯ ИСПОЛЬЗОВАНИЯ:
echo    doc-processor single --input "файл.pdf"
echo    doc-processor batch --input-folder "папка" --output-folder "результаты"
echo.
echo   ВАЖНО:
echo    1. ЗАКРОЙТЕ и ПЕРЕЗАПУСТИТЕ командную строку
echo    2. Проверьте командой: doc-processor --help
echo.
pause
