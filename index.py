import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
GROUP_ID = "-1003265048579"
API_URL = f"https://api.telegram.org/bot{TOKEN}"

def send_to_tg(method, data, files=None):
    return requests.post(f"{API_URL}/{method}", data=data, files=files)

@app.route('/api/ai_chat', methods=['POST'])
def ai_chat():
    data = request.form
    chat_id = data.get("chat_id")
    name = data.get("name")
    
    # Создаем новую тему
    topic = send_to_tg("createForumTopic", {"chat_id": GROUP_ID, "name": f"КЛИЕНТ: {name}"}).json()
    thread_id = topic.get("result", {}).get("message_thread_id")
    
    if thread_id:
        admin_link = f"{data.get('admin_link')}?id={chat_id}&tid={thread_id}"
        text = f"👤 {name}\n📞 {data.get('contact')}\n💬 {data.get('message')}\n\n🔗 Вход: {admin_link}"
        send_to_tg("sendMessage", {"chat_id": GROUP_ID, "message_thread_id": thread_id, "text": text})
        
        # Отправка файлов
        for f in request.files.getlist("files[]"):
            send_to_tg("sendDocument", {"chat_id": GROUP_ID, "message_thread_id": thread_id}, {"document": (f.filename, f.read())})
            
    return jsonify({"status": "ok", "thread_id": thread_id})

@app.route('/api/send_message', methods=['POST'])
def send_message():
    data = request.form
    tid = data.get("tid") # Получаем ID темы напрямую из Tilda
    if tid:
        if data.get("message"):
            send_to_tg("sendMessage", {"chat_id": GROUP_ID, "message_thread_id": tid, "text": data.get("message")})
        for f in request.files.getlist("files[]"):
            send_to_tg("sendDocument", {"chat_id": GROUP_ID, "message_thread_id": tid}, {"document": (f.filename, f.read())})
    return jsonify({"status": "ok"})

@app.route('/api/get_messages', methods=['GET'])
def get_messages():
    # Для бесплатного Vercel без БД сообщения от админа лучше ловить через Long Polling или Webhook
    # В этой версии мы возвращаем пустой список, если нет базы данных
    return jsonify({"new_messages": []})
