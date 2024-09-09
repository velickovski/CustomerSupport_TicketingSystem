# Пример за Python апликација
FROM python:3.12.3-slim

WORKDIR /app

# Копирање на датотеката requirements.txt во Docker контејнерот
COPY requirements.txt .

# Инсталирање на зависностите
RUN pip install --no-cache-dir -r requirements.txt

# Копирање на сите датотеки и фолдери од тековниот директориум во контејнерот
COPY . .

# Стартување на апликацијата
CMD ["python", "main.py"]
