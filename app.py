from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

BOT_TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
ADMIN_ID = "1055949397"
messages_store = {}

@app.route('/api/ai_chat', methods=['POST'])
def initial():
    chat_id = request.form.get('chat_id')
    name = request.form.get('name', 'Клиент')
    msg = request.form.get('message', '')
    file = request.files.get('file')

    text = f"🚀 ЧАТ: {name}\n🆔 ID чата: {chat_id}\n💬: {msg}"
    
    if file:
        files = {'document': (file.filename, file.read())}
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument", data={'chat_id': ADMIN_ID, 'caption': text}, files=files)
    else:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={'chat_id': ADMIN_ID, 'text': text})
    
    return jsonify({"status": "ok"}), 200

@app.route('/api/telegram_webhook', methods=['POST'])
def webhook():
    data = request.json
    msg = data.get("message", {})
    
    if "reply_to_message" in msg:
        reply_text = msg["reply_to_message"].get("text", msg["reply_to_message"].get("caption", ""))
        if "ID чата: " in reply_text:
            cid = reply_text.split("ID чата: ")[1].split("\n")[0].strip()
            
            # Определяем имя отвечающего
            sender_name = msg.get("from", {}).get("first_name", "Менеджер")
            
            if cid not in messages_store: messages_store[cid] = []
            
            # Если прислали файл в ответ
            file_url = ""
            if "document" in msg:
                fid = msg["document"]["file_id"]
                f_info = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={fid}").json()
                file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{f_info['result']['file_path']}"

            messages_store[cid].append({
                "text": msg.get("text", "Файл во вложении"),
                "sender": sender_name,
                "file_url": file_url
            })
            
    return "OK", 200

@app.route('/api/get_messages', methods=['GET'])
def get():
    cid = request.args.get('chat_id')
    msgs = messages_store.get(cid, [])
    messages_store[cid] = []
    return jsonify({"new_messages": msgs})

@app.route('/api/send_message', methods=['POST'])
def send():
    d = request.json
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                  json={'chat_id': ADMIN_ID, 'text': f"📩 Сообщение (ID чата: {d['chat_id']}):\n{d['message']}"})
    return "OK"
