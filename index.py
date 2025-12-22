from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
CHAT_ID = "-1003265048579" 

def tg_api(method, data, files=None):
    return requests.post(f"https://api.telegram.org/bot{TOKEN}/{method}", data=data, files=files)

@app.route('/ai_chat', methods=['POST'])
def ai_chat():
    try:
        name = request.form.get('name', 'Гость')
        contact = request.form.get('contact', '-')
        message = request.form.get('message', '')
        files = request.files.getlist('files[]')
        
        # Создаем топик в Telegram
        topic = tg_api("createForumTopic", {"chat_id": CHAT_ID, "name": f"{name} | {contact}"}).json()
        if not topic.get("ok"): return jsonify({"error": topic}), 500
            
        tid = topic["result"]["message_thread_id"]
        caption = f"🚀 Новая заявка!\n👤 {name}\n📞 {contact}\n💬 {message}"
        send_to_thread(tid, caption, files)
        
        return jsonify({"status": "ok", "tid": tid}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/send_message', methods=['POST'])
def send_message():
    try:
        tid = request.form.get('tid')
        msg = request.form.get('message', '')
        files = request.files.getlist('files[]')
        if tid:
            send_to_thread(tid, msg, files)
            return jsonify({"status": "sent"}), 200
        return jsonify({"error": "no_tid"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def send_to_thread(tid, text, files):
    if not files:
        if text: tg_api("sendMessage", {"chat_id": CHAT_ID, "message_thread_id": tid, "text": text})
    else:
        media = []
        f_dict = {}
        for i, f in enumerate(files):
            key = f"f{i}"
            f_dict[key] = (f.filename, f.read())
            item = {"type": "document", "media": f"attach://{key}"}
            if i == 0 and text: item["caption"] = text
            media.append(item)
        # Отправка альбомом
        tg_api("sendMediaGroup", {"chat_id": CHAT_ID, "message_thread_id": tid, "media": json.dumps(media)}, files=f_dict)
