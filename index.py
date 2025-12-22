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
        r = requests.post(url, data=data, files=files, timeout=15)
        return r.json()
    except Exception as e:
        return {"ok": False, "description": str(e)}

@app.route('/ai_chat', methods=['POST'])
def ai_chat():
    name = request.form.get('name', 'Гость')
    contact = request.form.get('contact', '-')
    message = request.form.get('message', '')
    files = request.files.getlist('files[]')
    
    # 1. Пробуем создать топик
    topic = tg_api("createForumTopic", {"chat_id": CHAT_ID, "name": f"{name} | {contact}"})
    
    # 2. Если топик не создался (группа не поддерживает или нет прав), шлем в корень
    if not topic.get("ok"):
        fallback_text = f"👤 {name}\n📞 {contact}\n💬 {message}"
        res = send_to_thread(None, fallback_text, files)
        return jsonify({"status": "sent_to_main", "details": res}), 200
            
    tid = topic["result"]["message_thread_id"]
    caption = f"🚀 Новая заявка!\n👤 {name}\n📞 {contact}\n💬 {message}"
    send_to_thread(tid, caption, files)
    return jsonify({"status": "ok", "tid": tid}), 200

@app.route('/send_message', methods=['POST'])
def send_message():
    tid = request.form.get('tid')
    msg = request.form.get('message', '')
    files = request.files.getlist('files[]')
    # Если tid пустой, сообщение уйдет в корень чата
    send_to_thread(tid if tid else None, msg, files)
    return jsonify({"status": "sent"}), 200

def send_to_thread(tid, text, files):
    data = {"chat_id": CHAT_ID}
    if tid: data["message_thread_id"] = tid
    
    if not files:
        data["text"] = text
        return tg_api("sendMessage", data)
    else:
        media = []
        f_dict = {}
        for i, f in enumerate(files):
            key = f"f{i}"
            # Сохраняем имя файла корректно
            f_dict[key] = (f.filename, f.read())
            item = {"type": "document", "media": f"attach://{key}"}
            if i == 0 and text: item["caption"] = text
            media.append(item)
        data["media"] = json.dumps(media)
        return tg_api("sendMediaGroup", data, files=f_dict)
