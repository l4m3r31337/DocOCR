# Установка doc-processor

## Требования к системе:
- Windows 10/11 (64-bit)
- Python 3.11 или новее
- Права администратора для установки

## 1. Установите Python:
- Скачайте Python 3.11+ с https://www.python.org/downloads/
- При установке **ОБЯЗАТЕЛЬНО** отметьте:
  - Add Python to PATH
  - Install for all users

## 2. Установите Tesseract OCR (для распознавания текста):
- Скачайте установщик: https://github.com/UB-Mannheim/tesseract/releases
- Запустите установщик, выберите:
  - Additional language data
  - Russian language data

## 3.Установите вспомогательные инструменты:
- **Poppler** (для работы с PDF): 
  Скачайте https://github.com/oschwartz10612/poppler-windows/releases
  Распакуйте в `C:\poppler` и добавьте `C:\poppler\bin` в PATH

- **Ghostscript** (для обработки таблиц):
  Скачайте https://ghostscript.com/releases/gsdnld.html

## 4. Запустите установку программы:
1. Распакуйте архив с doc-processor
2. Запустите `install.bat` от имени администратора
3. Ожидайте, установка не быстрая

## После установки:
- Откройте новую командную строку
- Проверьте: `doc-processor --help`