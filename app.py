import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
GROUP_ID = "-1003265048579" 
API_URL = f"https://api.telegram.org/bot{TOKEN}"

db_threads = {} 
db_clients = {}
messages_store = {} 

def create_topic(name):
    url = f"{API_URL}/createForumTopic"
    try:
        res = requests.post(url, data={"chat_id": GROUP_ID, "name": f"КЛИЕНТ: {name}"}).json()
        return res.get("result", {}).get("message_thread_id")
    except: return None

@app.route('/api/ai_chat', methods=['POST'])
def from_site():
    data = request.form
    chat_id = data.get("chat_id")
    name = data.get("name") or "Аноним"
    contact = data.get("contact") or "Не указан"
    message = data.get("message") or "Начат новый чат"
    
    # Исправлено: Ссылка теперь ведет на конкретный ID клиента
    admin_link = f"{data.get('admin_link')}?id={chat_id}"

    if chat_id not in db_threads:
        thread_id = create_topic(name)
        if thread_id:
            db_threads[chat_id] = thread_id
            db_clients[thread_id] = chat_id
    
    thread_id = db_threads.get(chat_id)
    text = f"👤 {name}\n📞 {contact}\n💬 {message}\n\n🔗 Вход в диалог: {admin_link}"
    
    requests.post(f"{API_URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": thread_id, "text": text})

    files = request.files.getlist("files[]")
    for f in files:
        requests.post(f"{API_URL}/sendDocument", params={"chat_id": GROUP_ID, "message_thread_id": thread_id}, files={"document": (f.filename, f.read())})
    
    return jsonify({"status": "ok"})

@app.route('/api/send_message', methods=['POST'])
def send_message():
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
