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

db_threads = {} 
db_clients = {}
messages_store = {} 
chat_timestamps = {} 

def process_files(chat_id, thread_id, files):
    """Отправка документов в TG и запись в историю чата без ????"""
    if not files: return
    if chat_id not in messages_store: messages_store[chat_id] = []
    
    for f in files:
        f_name = f.filename
        content = f.read()
        # Отправляем как документ
        requests.post(f"{API_URL}/sendDocument", 
                      params={"chat_id": GROUP_ID, "message_thread_id": thread_id}, 
                      files={"document": (f_name, content)})
        # Сохраняем в историю с префиксом FILE: вместо эмодзи
        messages_store[chat_id].append({"text": f"FILE: {f_name}", "is_admin": False})

@app.route('/api/ai_chat', methods=['POST'])
def handle_initial_chat():
    data = request.form
    chat_id = data.get("chat_id")
    name = data.get("name")
    contact = data.get("contact")
    message = data.get("message") or "Заявка с сайта"
    # Ссылка для менеджера
    admin_link = f"{data.get('admin_link')}?id={chat_id}"

    if chat_id not in db_threads:
        res = requests.post(f"{API_URL}/createForumTopic", 
                            data={"chat_id": GROUP_ID, "name": f"КЛИЕНТ: {name}"}).json()
        thread_id = res.get("result", {}).get("message_thread_id")
        if thread_id:
            db_threads[chat_id] = thread_id
            db_clients[thread_id] = chat_id
            chat_timestamps[chat_id] = time.time()
    
    thread_id = db_threads.get(chat_id)
    text = f"👤 {name}\n📞 {contact}\n💬 {message}\n\n🔗 Вход: {admin_link}"
    requests.post(f"{API_URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": thread_id, "text": text})

    process_files(chat_id, thread_id, request.files.getlist("files[]"))
    return jsonify({"status": "ok"})

@app.route('/api/send_message', methods=['POST'])
def handle_send_message():
    data = request.form
    chat_id = data.get("chat_id")
    text = data.get("message")
    thread_id = db_threads.get(chat_id)
    
    if thread_id:
        if text:
            requests.post(f"{API_URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": thread_id, "text": text})
        process_files(chat_id, thread_id, request.files.getlist("files[]"))
    return jsonify({"status": "ok"})

@app.route('/api/get_messages', methods=['GET'])
def handle_get_messages():
    chat_id = request.args.get("chat_id")
    msgs = messages_store.get(chat_id, [])
    messages_store[chat_id] = [] 
    return jsonify({"new_messages": msgs})

@app.route('/api/telegram_webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    if "message" in data:
        msg = data["message"]
        client_id = db_clients.get(msg.get("message_thread_id"))
        if client_id and "text" in msg:
            if client_id not in messages_store: messages_store[client_id] = []
            messages_store[client_id].append({"text": msg["text"], "is_admin": True})
    return "ok"

if __name__ == '__main__':
    app.run()
