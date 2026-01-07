@echo off
chcp 65001 >nul
title Удаление DocOCR
setlocal enabledelayedexpansion

echo ================================================
echo    ПОЛНОЕ УДАЛЕНИЕ DOCOCR
echo ================================================
echo.

REM Проверка прав администратора
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if errorlevel 1 (
    echo   ТРЕБУЮТСЯ ПРАВА АДМИНИСТРАТОРА!
    echo Запустите от имени Администратора
    pause
    exit /b 1
)

echo  Запущено от имени администратора
echo.

REM --- 1. УДАЛЕНИЕ ФАЙЛОВ И ПРОГРАММ ---
echo [1/3] Удаление файлов и программ...

set "INSTALL_DIR=C:\Program Files\DocOCR"
set "POPPLER_DIR=C:\poppler"
set "TESSERACT_DIR=C:\Program Files\Tesseract-OCR"

echo    Удаляю DocOCR...
if exist "!INSTALL_DIR!" (
    rmdir /s /q "!INSTALL_DIR!"
    echo  Папка программы удалена: !INSTALL_DIR!
) else (
    echo  DocOCR не найден
)

echo    Удаляю Poppler...
if exist "!POPPLER_DIR!" (
    rmdir /s /q "!POPPLER_DIR!"
    echo  Poppler удален: !POPPLER_DIR!
) else (
    echo  Poppler не найден
)

echo    Удаляю Tesseract...
if exist "!TESSERACT_DIR!" (
    echo  Удаляю Tesseract OCR...
    rmdir /s /q "!TESSERACT_DIR!"
    echo  Tesseract удален: !TESSERACT_DIR!
) else (
    echo  Tesseract не найден
)

REM --- 2. УДАЛЕНИЕ ИЗ ПРОГРАММ И КОМПОНЕНТОВ WINDOWS ---
echo.
echo [2/3] Удаление из программ Windows...

echo    Удаляю Tesseract из программ...
wmic product where "name like '%%Tesseract%%'" call uninstall /nointeractive 2>nul

REM Удаляем записи из реестра
echo    Очищаю реестр...
reg delete "HKLM\SOFTWARE\Tesseract-OCR" /f 2>nul
reg delete "HKCU\SOFTWARE\Tesseract-OCR" /f 2>nul
reg delete "HKLM\SOFTWARE\DocOCR" /f 2>nul
reg delete "HKCU\SOFTWARE\DocOCR" /f 2>nul

REM --- 3. ОЧИСТКА ПЕРЕМЕННЫХ СРЕДЫ ---
echo.
echo [3/3] Очистка переменных среды...

echo    Очищаю системный PATH...
for /F "skip=2 tokens=1,2*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do set "CURRENT_PATH=%%C"

if defined CURRENT_PATH (
    echo    Удаляю пути...
    
    set "NEW_PATH=!CURRENT_PATH!"
    
    REM Удаляем все вхождения путей
    :remove_loop
    set "OLD_PATH=!NEW_PATH!"
    
    REM Удаляем DocOCR
    set "NEW_PATH=!NEW_PATH:;C:\Program Files\DocOCR=!"
    set "NEW_PATH=!NEW_PATH:C:\Program Files\DocOCR;=!"
    set "NEW_PATH=!NEW_PATH:C:\Program Files\DocOCR=!"
    
    REM Удаляем Poppler
    set "NEW_PATH=!NEW_PATH:;C:\poppler\Library\bin=!"
    set "NEW_PATH=!NEW_PATH:C:\poppler\Library\bin;=!"
    set "NEW_PATH=!NEW_PATH:C:\poppler\Library\bin=!"
    set "NEW_PATH=!NEW_PATH:;C:\poppler=!"
    set "NEW_PATH=!NEW_PATH:C:\poppler;=!"
    set "NEW_PATH=!NEW_PATH:C:\poppler=!"
    
    REM Удаляем Tesseract
    set "NEW_PATH=!NEW_PATH:;C:\Program Files\Tesseract-OCR=!"
    set "NEW_PATH=!NEW_PATH:C:\Program Files\Tesseract-OCR;=!"
    set "NEW_PATH=!NEW_PATH:C:\Program Files\Tesseract-OCR=!"
    
    if not "!OLD_PATH!"=="!NEW_PATH!" goto remove_loop
    
    REM Удаляем двойные точки с запятой
    :clean_semicolons
    set "OLD_PATH=!NEW_PATH!"
    set "NEW_PATH=!NEW_PATH:;;=;!"
    if not "!OLD_PATH!"=="!NEW_PATH!" goto clean_semicolons
    
    REM Удаляем начальную и конечную точку с запятой
    if "!NEW_PATH:~0,1!"==";" set "NEW_PATH=!NEW_PATH:~1!"
    if "!NEW_PATH:~-1!"==";" set "NEW_PATH=!NEW_PATH:~0,-1!"
    
    if not "!NEW_PATH!"=="!CURRENT_PATH!" (
        reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path /t REG_EXPAND_SZ /d "!NEW_PATH!" /f >nul
        echo  PATH очищен
    ) else (
        echo  PATH уже чист
    )
)

echo    Удаляю переменные среды...
reg delete "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v POPPLER_PATH /f 2>nul
reg delete "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v DOC_OCR_PATH /f 2>nul
reg delete "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v POPPLER_BIN /f 2>nul
reg delete "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v TESSERACT_PATH /f 2>nul

echo Переменные среды удалены

REM --- ФИНАЛЬНАЯ ОЧИСТКА ---
echo.
echo Финальная очистка...

REM Очищаем временные файлы
echo    Очищаю временные файлы...
del /q "%TEMP%\*dococr*" 2>nul
del /q "%TEMP%\*tesseract*" 2>nul
del /q "%TEMP%\*poppler*" 2>nul

echo.
echo ================================================
echo    УДАЛЕНИЕ ЗАВЕРШЕНО
echo ================================================
echo.
echo УДАЛЕНО:
echo   - DocOCR программа
echo   - Poppler
echo   - Tesseract OCR
echo   - Пути из переменной PATH
echo   - Переменные среды
echo.
echo.
echo    ПЕРЕЗАГРУЗИТЕ КОМПЬЮТЕР для полной очистки!
echo.
pause