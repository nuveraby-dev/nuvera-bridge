from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
CHAT_ID = "-1003265048579" 

def tg_api(method, data, files=None):
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    try:
        r = requests.post(url, data=data, files=files, timeout=10)
        return r.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.route('/ai_chat', methods=['POST'])
def ai_chat():
    name = request.form.get('name', 'Гость')
    contact = request.form.get('contact', '-')
    message = request.form.get('message', '')
    files = request.files.getlist('files[]')
    
    # Создаем топик
    topic = tg_api("createForumTopic", {"chat_id": CHAT_ID, "name": f"{name} | {contact}"})
    
    if not topic.get("ok"):
        # Если не удалось создать топик, пробуем отправить в общий чат
        tg_api("sendMessage", {"chat_id": CHAT_ID, "text": f"Ошибка топика! Заявка: {name} {contact}\n{message}"})
        return jsonify({"status": "partial_ok", "error": topic.get("description")}), 200
            
    tid = topic["result"]["message_thread_id"]
    caption = f"👤 {name}\n📞 {contact}\n💬 {message}"
    send_to_thread(tid, caption, files)
    
    return jsonify({"status": "ok", "tid": tid}), 200

@app.route('/send_message', methods=['POST'])
def send_message():
    tid = request.form.get('tid')
    msg = request.form.get('message', '')
    files = request.files.getlist('files[]')
    if tid:
        send_to_thread(tid, msg, files)
        return jsonify({"status": "sent"}), 200
    return jsonify({"error": "no_tid"}), 400

def send_to_thread(tid, text, files):
    if not files:
        tg_api("sendMessage", {"chat_id": CHAT_ID, "message_thread_id": tid, "text": text})
    else:
        media = []
        f_dict = {}
        for i, f in enumerate(files):
            key = f"f{i}"
            f_dict[key] = (f.filename, f.read())
            item = {"type": "document", "media": f"attach://{key}"}
            if i == 0 and text: item["caption"] = text
            media.append(item)
        tg_api("sendMediaGroup", {"chat_id": CHAT_ID, "message_thread_id": tid, "media": json.dumps(media)}, files=f_dict)
