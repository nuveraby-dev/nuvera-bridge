import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- ТВОИ НАСТРОЙКИ ---
TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
GROUP_ID = "-1003265048579" 
API_URL = f"https://api.telegram.org/bot{TOKEN}"

# Временное хранилище связей (Для постоянной работы рекомендуется Vercel KV)
db_threads = {} 
db_clients = {}

def create_topic(name):
    """Создает новую подпапку (Topic) в твоей группе Telegram"""
    url = f"{API_URL}/createForumTopic"
    payload = {
        "chat_id": GROUP_ID,
        "name": f"КЛИЕНТ: {name}"
    }
    try:
        res = requests.post(url, data=payload).json()
        return res.get("result", {}).get("message_thread_id")
    except Exception as e:
        print(f"Ошибка создания топика: {e}")
        return None

@app.route('/api/ai_chat', methods=['POST'])
def from_site():
    """Принимает данные с Tilda и отправляет в нужную ветку Telegram"""
    data = request.form
    chat_id = data.get("chat_id")
    name = data.get("name", "Новый клиент")
    message = data.get("message", "Без текста")
    admin_link = data.get("admin_link", "")

    # Проверяем, существует ли уже топик для этого клиента
    if chat_id not in db_threads:
        thread_id = create_topic(name)
        if thread_id:
            db_threads[chat_id] = thread_id
            db_clients[thread_id] = chat_id
    
    thread_id = db_threads.get(chat_id)
    
    # Формируем текст сообщения
    text = f"👤 {name}\n💬 {message}\n\n🔗 Вход в чат для ответа: {admin_link}"
    
    # Отправляем текст в конкретный топик
    requests.post(f"{API_URL}/sendMessage", data={
        "chat_id": GROUP_ID,
        "message_thread_id": thread_id,
        "text": text
    })

    # Пересылка файлов (поддержка мультизагрузки)
    files = request.files.getlist("files[]")
    for f in files:
        requests.post(f"{API_URL}/sendDocument", 
                      params={"chat_id": GROUP_ID, "message_thread_id": thread_id},
                      files={"document": (f.filename, f.read())})
    
    return jsonify({"status": "ok", "thread_id": thread_id})

@app.route('/api/telegram_webhook', methods=['POST'])
def from_telegram():
    """Эндпоинт для приема твоих ответов из Telegram"""
    return "ok"

if __name__ == '__main__':
    app.run(debug=True)
