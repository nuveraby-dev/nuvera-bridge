import os
import requests
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- НАСТРОЙКИ ---
TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
GROUP_ID = "-1003265048579" 
API_URL = f"https://api.telegram.org/bot{TOKEN}"

# Хранилища данных в оперативной памяти
db_threads = {} 
db_clients = {}
messages_store = {} 
chat_timestamps = {} 

def cleanup_old_chats():
    """Удаляет данные чатов, которые старше 24 часов"""
    now = time.time()
    one_day = 86400 
    to_delete = [cid for cid, t in chat_timestamps.items() if now - t > one_day]
    
    for cid in to_delete:
        thread_id = db_threads.get(cid)
        if thread_id:
            db_clients.pop(thread_id, None)
        db_threads.pop(cid, None)
        messages_store.pop(cid, None)
        chat_timestamps.pop(cid, None)

def create_topic(name):
    """Создает подпапку в Telegram для каждого клиента"""
    url = f"{API_URL}/createForumTopic"
    try:
        res = requests.post(url, data={"chat_id": GROUP_ID, "name": f"КЛИЕНТ: {name}"}).json()
        return res.get("result", {}).get("message_thread_id")
    except:
        return None

@app.route('/api/ai_chat', methods=['POST'])
def from_site():
    cleanup_old_chats()
    
    data = request.form
    chat_id = data.get("chat_id")
    name = data.get("name")
    contact = data.get("contact")
    message = data.get("message") or "Начат новый чат"
    base_link = data.get("admin_link")
    
    # Ссылка для входа менеджера (теперь работает корректно)
    admin_link = f"{base_link}?id={chat_id}"

    if chat_id not in db_threads:
        thread_id = create_topic(name)
        if thread_id:
            db_threads[chat_id] = thread_id
            db_clients[thread_id] = chat_id
            chat_timestamps[chat_id] = time.time()
    
    thread_id = db_threads.get(chat_id)
    
    # Отправка основной информации менеджеру в Telegram
    text = f"👤 Имя: {name}\n📞 Контакт: {contact}\n💬 Сообщение: {message}\n\n🔗 Вход в диалог: {admin_link}"
    requests.post(f"{API_URL}/sendMessage", data={
        "chat_id": GROUP_ID, 
        "message_thread_id": thread_id, 
        "text": text
    })

    # Обработка мультизагрузки файлов
    files = request.files.getlist("files[]")
    if chat_id not in messages_store:
        messages_store[chat_id] = []
    
    for f in files:
        file_content = f.read()
        # Шлем файл в Telegram
        requests.post(f"{API_URL}/sendDocument", 
                      params={"chat_id": GROUP_ID, "message_thread_id": thread_id}, 
                      files={"document": (f.filename, file_content)})
        # Добавляем инфо о файле в чат клиента на сайте
        messages_store[chat_id].append({"text": f"📎 Файл: {f.filename}", "is_admin": False})
    
    return jsonify({"status": "ok"})

@app.route('/api/send_message', methods=['POST'])
def send_message():
    cleanup_old_chats()
    data = request.form
    chat_id = data.get("chat_id")
    text = data.get("message")
    thread_id = db_threads.get(chat_id)
    
    if thread_id:
        requests.post(f"{API_URL}/sendMessage", data={
            "chat_id": GROUP_ID, 
            "message_thread_id": thread_id, 
            "text": text
        })
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
        
        # Если это ответ от админа в топике клиента
        if client_id and "text" in msg:
            if client_id not in messages_store: 
                messages_store[client_id] = []
            messages_store[client_id].append({"text": msg["text"], "is_admin": True})
            
    return "ok"

if __name__ == '__main__':
    app.run(debug=True)
