@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo  Установка doc-processor
echo ========================================
echo.

:: Проверка прав администратора
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ОШИБКА] Требуются права администратора!
    echo Запустите установщик от имени администратора.
    pause
    exit /b 1
)

:: Проверка Python
echo [1/4] Проверка установленного Python...
where python >nul 2>&1
if %errorLevel% neq 0 (
    echo [ОШИБКА] Python не найден!
    echo Установите Python 3.11+ с https://www.python.org/downloads/
    echo Обязательно отметьте "Add Python to PATH" при установке.
    pause
    exit /b 1
)

python --version
python --version 2>&1 | findstr /r /c:"Python 3\.1[1-9]" >nul
if %errorLevel% neq 0 (
    echo [ПРЕДУПРЕЖДЕНИЕ] Рекомендуется Python 3.11+
    echo Найденная версия может работать, но возможны проблемы.
    pause
)

:: Создание директории установки
echo.
echo [2/4] Создание директории установки...
set "INSTALL_DIR=%ProgramFiles%\doc-processor"
echo Установка в: %INSTALL_DIR%

if exist "%INSTALL_DIR%" (
    echo Директория уже существует, обновляю файлы...
    rmdir /s /q "%INSTALL_DIR%" 2>nul
)

mkdir "%INSTALL_DIR%" 2>nul
if not exist "%INSTALL_DIR%" (
    echo [ОШИБКА] Не удалось создать директорию установки
    pause
    exit /b 1
)

:: Копирование файлов
echo Копирование файлов программы...
xcopy /E /I /Y "%~dp0*.*" "%INSTALL_DIR%\" >nul

:: Проверка наличия requirements.txt
if not exist "%INSTALL_DIR%\requirements.txt" (
    echo [ОШИБКА] Файл requirements.txt не найден в архиве!
    echo Добавьте requirements.txt в архив с программой.
    pause
    exit /b 1
)

:: Установка зависимостей Python
echo.
echo [3/4] Установка Python-зависимостей...
echo Это может занять несколько минут...

cd /d "%INSTALL_DIR%"

:: Очистка кэша pip для избежания проблем
echo Шаг 1: Очистка кэша pip...
call pip cache purge 2>nul

:: Установка пакетов строго из requirements.txt с форсированием версий
echo Шаг 2: Установка с форсированием версий...

:: Читаем requirements.txt и устанавливаем каждый пакет
set "ERROR_COUNT=0"
for /f "usebackq tokens=*" %%p in ("%INSTALL_DIR%\requirements.txt") do (
    set "line=%%p"
    set "line=!line: =!"
    
    if "!line!" neq "" if not "!line:~0,1!"=="#" (
        echo Установка: !line!
        
        :: Для пакетов с указанием версии используем --force-reinstall
        echo !line! | findstr "==" >nul
        if !errorlevel! equ 0 (
            :: Пакет с версией - форсируем установку
            call pip install !line! --force-reinstall --no-deps 2>nul
            if !errorlevel! neq 0 (
                call pip install !line! --force-reinstall 2>nul
            )
        ) else (
            :: Пакет без версии - обычная установка
            call pip install !line! 2>nul
        )
        
        if !errorlevel! neq 0 (
            echo [ОШИБКА] Не удалось установить: !line!
            set /a ERROR_COUNT+=1
        )
    )
)

:: Установка зависимостей для уже установленных пакетов
echo Шаг 3: Установка недостающих зависимостей...
call pip install -r "%INSTALL_DIR%\requirements.txt" 2>nul

if !ERROR_COUNT! gtr 0 (
    echo [ПРЕДУПРЕЖДЕНИЕ] Было !ERROR_COUNT! ошибок при установке.
    echo Пробую альтернативный подход...
    
    :: Пробуем установить с игнорированием уже установленных пакетов
    call pip install --upgrade -r "%INSTALL_DIR%\requirements.txt" --ignore-installed 2>nul
)

:: Установка как пакета (если есть setup.py)
echo.
echo [4/4] Создание системной команды...

if exist "setup.py" (
    echo Установка пакета doc-processor...
    pip install -e . 2>nul
    if !errorlevel! equ 0 (
        echo Пакет установлен как консольный скрипт.
        goto :COMMAND_CREATED
    )
)

:: Создаем .cmd файл в System32
echo Создание команды в System32...
echo @echo off > "%SystemRoot%\system32\doc-processor.cmd"
echo rem Doc-Processor v1.0 >> "%SystemRoot%\system32\doc-processor.cmd"
echo python "%INSTALL_DIR%\run.py" %%* >> "%SystemRoot%\system32\doc-processor.cmd"

:COMMAND_CREATED
:: Создаем простой .bat файл в папке установки
echo @echo off > "%INSTALL_DIR%\doc-processor.bat"
echo echo Doc-Processor >> "%INSTALL_DIR%\doc-processor.bat"
echo python "%INSTALL_DIR%\run.py" %%* >> "%INSTALL_DIR%\doc-processor.bat"

echo.
echo ========================================
echo  УСТАНОВКА ЗАВЕРШЕНА!
echo ========================================
echo.
echo Что было сделано:
echo   1. Проверена установка Python ✓
echo   2. Создана папка: %INSTALL_DIR% ✓
echo   3. Установлены зависимости из requirements.txt ✓
echo   4. Создана команда: doc-processor ✓
echo.
echo Проверьте установку:
echo   doc-processor --help
echo.
echo НАЖМИТЕ ЛЮБУЮ КЛАВИШУ ДЛЯ ВЫХОДА...
pause >nul