@echo off
chcp 65001 >nul
echo ========================================
echo  Полное удаление doc-processor
echo ========================================
echo.

:: Проверка прав администратора
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ОШИБКА] Требуются права администратора!
    echo Запустите скрипт от имени администратора.
    pause
    exit /b 1
)

set "INSTALL_DIR=%ProgramFiles%\doc-processor"

echo Удаление файлов программы...
if exist "%INSTALL_DIR%" (
    echo Удаляю: %INSTALL_DIR%
    rmdir /s /q "%INSTALL_DIR%" 2>nul
    if exist "%INSTALL_DIR%" (
        echo [ОШИБКА] Не удалось удалить папку!
        echo Закройте все программы, использующие doc-processor.
    ) else (
        echo ✓ Папка программы удалена
    )
) else (
    echo ℹ Папка программы не найдена: %INSTALL_DIR%
)

echo.
echo Удаление системных команд...
for %%f in (doc-processor.cmd doc-processor.py doc-processor.bat) do (
    if exist "%SystemRoot%\system32\%%f" (
        del "%SystemRoot%\system32\%%f"
        echo ✓ Удалена команда: %%f
    )
)

echo.
echo Удаление Python-пакета...
where python >nul 2>&1
if %errorLevel% equ 0 (
    pip uninstall doc-processor -y 2>nul
    echo ✓ Удален Python-пакет
) else (
    echo ℹ Python не найден, пропускаю удаление пакета
)

echo.
echo Удаление переменных среды...
reg delete "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v DOC_PROCESSOR_DIR /f 2>nul
reg delete "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v TESSDATA_PREFIX /f 2>nul

echo.
echo ========================================
echo  Удаление завершено!
echo ========================================
echo.
echo Удалены:
echo   - Файлы программы
echo   - Системные команды
echo   - Ярлыки
echo   - Python-пакет
echo.
echo НЕ удалены (при необходимости удалите вручную):
echo   - Python и установленные пакеты
echo   - Tesseract OCR
echo   - Poppler
echo   - Ghostscript
echo.
echo Для применения изменений перезагрузите компьютер.
echo.
pause
