import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
GROUP_ID = "-1003265048579"
API_URL = f"https://api.telegram.org/bot{TOKEN}"

@app.route('/api/ai_chat', methods=['POST'])
def ai_chat():
    try:
        data = request.form
        chat_id, name, contact = data.get("chat_id"), data.get("name"), data.get("contact")
        
        # 1. Создаем тему
        res = requests.post(f"{API_URL}/createForumTopic", data={"chat_id": GROUP_ID, "name": f"КЛИЕНТ: {name}"}).json()
        tid = res.get("result", {}).get("message_thread_id")
        
        if tid:
            link = f"{data.get('admin_link')}?id={chat_id}&tid={tid}"
            text = f"👤 {name}\n📞 {contact}\n💬 {data.get('message')}\n\n🔗 Вход: {link}"
            requests.post(f"{API_URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": tid, "text": text})
            
            # 2. Сразу отправляем файлы, если они есть
            files = request.files.getlist("files[]")
            for f in files:
                requests.post(f"{API_URL}/sendDocument", params={"chat_id": GROUP_ID, "message_thread_id": tid}, files={"document": (f.filename, f.read())})
            
            return jsonify({"status": "ok", "tid": tid})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    return jsonify({"status": "error"}), 400

@app.route('/api/send_message', methods=['POST'])
def send_message():
    tid = request.form.get("tid")
    if tid:
        msg = request.form.get("message")
        if msg:
            requests.post(f"{API_URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": tid, "text": msg})
        
        files = request.files.getlist("files[]")
        for f in files:
            requests.post(f"{API_URL}/sendDocument", params={"chat_id": GROUP_ID, "message_thread_id": tid}, files={"document": (f.filename, f.read())})
    return jsonify({"status": "ok"})
