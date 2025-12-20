import os
import requests
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- ТВОИ НАСТРОЙКИ ---
TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
GROUP_ID = "-1003265048579" 
API_URL = f"https://api.telegram.org/bot{TOKEN}"

# Хранилища данных
db_threads = {} 
db_clients = {}
messages_store = {} 
chat_timestamps = {} # Храним время создания чата

def cleanup_old_chats():
    """Удаляет данные чатов, которые старше 24 часов"""
    now = time.time()
    one_day = 86400 # 24 часа в секундах
    
    # Собираем ID для удаления
    to_delete = [cid for cid, t in chat_timestamps.items() if now - t > one_day]
    
    for cid in to_delete:
        thread_id = db_threads.get(cid)
        if thread_id:
            db_clients.pop(thread_id, None)
        db_threads.pop(cid, None)
        messages_store.pop(cid, None)
        chat_timestamps.pop(cid, None)
        print(f"Чат {cid} удален по истечении 1 дня")

def create_topic(name):
    url = f"{API_URL}/createForumTopic"
    try:
        res = requests.post(url, data={"chat_id": GROUP_ID, "name": f"КЛИЕНТ: {name}"}).json()
        return res.get("result", {}).get("message_thread_id")
    except: return None

@app.route('/api/ai_chat', methods=['POST'])
def from_site():
    cleanup_old_chats() # Запуск очистки перед новым чатом
    
    data = request.form
    chat_id = data.get("chat_id")
    name = data.get("name")
    contact = data.get("contact")
    message = data.get("message") or "Начат новый диалог"
    base_link = data.get("admin_link")
    admin_link = f"{base_link}?id={chat_id}"

    if chat_id not in db_threads:
        thread_id = create_topic(name)
        if thread_id:
            db_threads[chat_id] = thread_id
            db_clients[thread_id] = chat_id
            chat_timestamps[chat_id] = time.time() # Записываем время создания
    
    thread_id = db_threads.get(chat_id)
    text = f"👤 Имя: {name}\n📞 Контакт: {contact}\n💬 Сообщение: {message}\n\n🔗 Вход в диалог: {admin_link}"
    
    requests.post(f"{API_URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": thread_id, "text": text})

    files = request.files.getlist("files[]")
    for f in files:
        requests.post(f"{API_URL}/sendDocument", params={"chat_id": GROUP_ID, "message_thread_id": thread_id}, files={"document": (f.filename, f.read())})
    
    return jsonify({"status": "ok"})

@app.route('/api/send_message', methods=['POST'])
def send_message():
    cleanup_old_chats() # Очистка при отправке сообщения
    data = request.form
    chat_id = data.get("chat_id")
    text = data.get("message")
    thread_id = db_threads.get(chat_id)
    if thread_id:
        requests.post(f"{API_URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": thread_id, "text": text})
    return jsonify({"status": "ok"})

@app.route('/api/get_messages', methods=['GET'])
def get_messages():
    chat_id = request.args.get("chat_id")
    msgs = messages_store.get(chat_id, [])
    messages_store[chat_id] = [] 
    return jsonify({"new_messages": msgs})

@app.route('/api/telegram_webhook', methods=['POST'])
def from_telegram():
    data = request.json
    if "message" in data:
        msg = data["message"]
        thread_id = msg.get("message_thread_id")
        client_id = db_clients.get(thread_id)
        if client_id and "text" in msg:
            if client_id not in messages_store: messages_store[client_id] = []
            messages_store[client_id].append({"text": msg["text"], "is_admin": True})
    return "ok"

if __name__ == '__main__':
    app.run(debug=True)
