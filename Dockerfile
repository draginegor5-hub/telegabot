FROM python:3.11-slim

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем пакеты
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код приложения (кроме .venv!)
COPY . .

# Открываем порт
EXPOSE 8000

# Запускаем основной файл
CMD ["python", "main.py"]