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

db_threads, db_clients, messages_store, chat_timestamps = {}, {}, {}, {}

def cleanup_old_chats():
    now = time.time()
    to_delete = [cid for cid, t in chat_timestamps.items() if now - t > 86400]
    for cid in to_delete:
        thread_id = db_threads.get(cid)
        if thread_id: db_clients.pop(thread_id, None)
        for d in [db_threads, messages_store, chat_timestamps]: d.pop(cid, None)

def create_topic(name):
    url = f"{API_URL}/createForumTopic"
    try:
        res = requests.post(url, data={"chat_id": GROUP_ID, "name": f"КЛИЕНТ: {name}"}).json()
        return res.get("result", {}).get("message_thread_id")
    except: return None

@app.route('/api/ai_chat', methods=['POST'])
def from_site():
    cleanup_old_chats()
    data = request.form
    chat_id, name, contact = data.get("chat_id"), data.get("name"), data.get("contact")
    # Ссылка формируется чисто, без лишних редиректов
    admin_link = f"{data.get('admin_link')}?id={chat_id}"

    if chat_id not in db_threads:
        thread_id = create_topic(name)
        if thread_id:
            db_threads[chat_id], db_clients[thread_id] = thread_id, chat_id
            chat_timestamps[chat_id] = time.time()
    
    thread_id = db_threads.get(chat_id)
    text = f"👤 {name}\n📞 {contact}\n💬 {data.get('message', 'Начат чат')}\n\n🔗 Вход в чат: {admin_link}"
    requests.post(f"{API_URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": thread_id, "text": text})

    handle_files(chat_id, thread_id, request.files.getlist("files[]"))
    return jsonify({"status": "ok"})

@app.route('/api/send_message', methods=['POST'])
def send_message():
    data = request.form
    chat_id, text = data.get("chat_id"), data.get("message")
    thread_id = db_threads.get(chat_id)
    if thread_id:
        if text: requests.post(f"{API_URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": thread_id, "text": text})
        handle_files(chat_id, thread_id, request.files.getlist("files[]"))
    return jsonify({"status": "ok"})

def handle_files(chat_id, thread_id, files):
    if not files: return
    if chat_id not in messages_store: messages_store[chat_id] = []
    for f in files:
        content = f.read()
        # Отправка как документа в Telegram
        requests.post(f"{API_URL}/sendDocument", params={"chat_id": GROUP_ID, "message_thread_id": thread_id}, files={"document": (f.filename, content)})
        # Отображение в стиле мессенджера
        messages_store[chat_id].append({"text": f"📎 {f.filename}", "is_admin": False})

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
        client_id = db_clients.get(msg.get("message_thread_id"))
        if client_id and "text" in msg:
            if client_id not in messages_store: messages_store[client_id] = []
            messages_store[client_id].append({"text": msg["text"], "is_admin": True})
    return "ok"
