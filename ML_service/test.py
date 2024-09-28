import requests
import json

# Адрес сервера (локальный IP и порт)
url = 'http://127.0.0.1:8000/predict'

# Текст вопроса
data = {
    "question": "Привет, как твои дела?"
}

# Отправляем POST-запрос
response = requests.post(url, json=data)

# Проверяем статус и выводим ответ
if response.status_code == 200:
    print("Ответ от сервера:", response.json())
else:
    print("Ошибка:", response.status_code, response.text)
