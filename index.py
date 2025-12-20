import os
import requests
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
GROUP_ID = "-1003265048579"
API_URL = f"https://api.telegram.org/bot{TOKEN}"

# Временная база данных в памяти
db_threads, db_clients, messages_store, chat_timestamps = {}, {}, {}, {}

def process_files(chat_id, thread_id, files):
    if not files: return
    if chat_id not in messages_store: messages_store[chat_id] = []
    for f in files:
        f_name = f.filename
        content = f.read()
        # Отправляем файл в Telegram
        requests.post(f"{API_URL}/sendDocument", 
                      params={"chat_id": GROUP_ID, "message_thread_id": thread_id}, 
                      files={"document": (f_name, content)})
        # В чат на сайте пишем просто текст без эмодзи
        messages_store[chat_id].append({"text": f"FILE: {f_name}", "is_admin": False})

@app.route('/api/ai_chat', methods=['POST'])
def ai_chat():
    data = request.form
    chat_id, name, contact = data.get("chat_id"), data.get("name"), data.get("contact")
    admin_link = f"{data.get('admin_link')}?id={chat_id}"

    if chat_id not in db_threads:
        res = requests.post(f"{API_URL}/createForumTopic", data={"chat_id": GROUP_ID, "name": f"CLIENT: {name}"}).json()
        thread_id = res.get("result", {}).get("message_thread_id")
        if thread_id:
            db_threads[chat_id], db_clients[thread_id] = thread_id, chat_id
            chat_timestamps[chat_id] = time.time()
    
    thread_id = db_threads.get(chat_id)
    # Используем простые символы для стабильности
    text = f"USER: {name}\nTEL: {contact}\nMSG: {data.get('message', '---')}\n\nLINK: {admin_link}"
    requests.post(f"{API_URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": thread_id, "text": text})
    process_files(chat_id, thread_id, request.files.getlist("files[]"))
    return jsonify({"status": "ok"})

@app.route('/api/send_message', methods=['POST'])
def send_message():
    chat_id, text = request.form.get("chat_id"), request.form.get("message")
    thread_id = db_threads.get(chat_id)
    if thread_id:
        if text: requests.post(f"{API_URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": thread_id, "text": text})
        process_files(chat_id, thread_id, request.files.getlist("files[]"))
    return jsonify({"status": "ok"})

@app.route('/api/get_messages', methods=['GET'])
def get_messages():
    chat_id = request.args.get("chat_id")
    msgs = messages_store.get(chat_id, [])
    messages_store[chat_id] = []
    return jsonify({"new_messages": msgs})

@app.route('/api/webhook', methods=['POST'])
def webhook():
    data = request.json
    if "message" in data:
        msg = data["message"]
        client_id = db_clients.get(msg.get("message_thread_id"))
        if client_id and "text" in msg:
            if client_id not in messages_store: messages_store[client_id] = []
            messages_store[client_id].append({"text": msg["text"], "is_admin": True})
    return "ok"
