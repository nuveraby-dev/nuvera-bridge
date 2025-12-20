import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- НАСТРОЙКИ ---
TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
GROUP_ID = "-1002360877840" 
API_URL = f"https://api.telegram.org/bot{TOKEN}"

# Словари для связи (после деплоя на Vercel они будут жить до перезагрузки сервера)
db_threads = {} 
db_clients = {}

def create_topic(name):
    """Создает новую ветку (Topic) в Telegram для каждого клиента"""
    res = requests.post(f"{API_URL}/createForumTopic", data={
        "chat_id": GROUP_ID,
        "name": f"КЛИЕНТ: {name}"
    }).json()
    return res.get("result", {}).get("message_thread_id")

@app.route('/api/ai_chat', methods=['POST'])
def from_site():
    """Принимает сообщение с Tilda и отправляет в нужную ветку Telegram"""
    data = request.form
    chat_id = data.get("chat_id")
    name = data.get("name", "Новый клиент")
    message = data.get("message", "Без текста")
    admin_link = data.get("admin_link", "")

    # Создаем топик, если его еще нет
    if chat_id not in db_threads:
        thread_id = create_topic(name)
        db_threads[chat_id] = thread_id
        db_clients[thread_id] = chat_id
    
    thread_id = db_threads[chat_id]
    
    # Текст сообщения в Telegram
    text = f"👤 {name}\n💬 {message}\n\n🔗 Вход в чат: {admin_link}"
    
    requests.post(f"{API_URL}/sendMessage", data={
        "chat_id": GROUP_ID,
        "message_thread_id": thread_id,
        "text": text
    })

    # Если клиент прикрепил файлы на сайте — пересылаем их в топик
    files = request.files.getlist("files[]")
    for f in files:
        requests.post(f"{API_URL}/sendDocument", 
                      params={"chat_id": GROUP_ID, "message_thread_id": thread_id},
                      files={"document": (f.filename, f.read())})
    
    return jsonify({"status": "ok"})

@app.route('/api/telegram_webhook', methods=['POST'])
def from_telegram():
    """Эндпоинт для приема твоих ответов из Telegram (Webhook)"""
    data = request.json
    return "ok"

if __name__ == '__main__':
    app.run(debug=True)
