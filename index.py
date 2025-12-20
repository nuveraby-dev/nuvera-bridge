import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
GROUP_ID = "-1003265048579"
URL = f"https://api.telegram.org/bot{TOKEN}"

@app.route('/ai_chat', methods=['POST'])
def ai_chat():
    try:
        d = request.form
        # Создаем тему
        topic_res = requests.post(f"{URL}/createForumTopic", data={"chat_id": GROUP_ID, "name": f"Клиент: {d.get('name')}"}).json()
        tid = topic_res.get("result", {}).get("message_thread_id")
        
        if tid:
            link = f"{d.get('admin_link')}?tid={tid}"
            text = f"Имя: {d.get('name')}\nСвязь: {d.get('contact')}\nСообщение: {d.get('message')}\n\nСсылка: {link}"
            requests.post(f"{URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": tid, "text": text})
            
            # Обработка файлов
            if 'files[]' in request.files:
                for f in request.files.getlist('files[]'):
                    if f.filename:
                        requests.post(f"{URL}/sendDocument", params={"chat_id": GROUP_ID, "message_thread_id": tid}, files={"document": (f.filename, f.read())})
            
            return jsonify({"status": "ok", "tid": tid})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500
    return jsonify({"status": "error"}), 400

@app.route('/send_message', methods=['POST'])
def send_message():
    tid = request.form.get("tid")
    if tid:
        if request.form.get("message"):
            requests.post(f"{URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": tid, "text": request.form.get("message")})
        
        if 'files[]' in request.files:
            for f in request.files.getlist('files[]'):
                if f.filename:
                    requests.post(f"{URL}/sendDocument", params={"chat_id": GROUP_ID, "message_thread_id": tid}, files={"document": (f.filename, f.read())})
    return jsonify({"status": "ok"})
