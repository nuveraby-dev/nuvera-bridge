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
    
    # Создаем топик
    topic = tg_api("createForumTopic", {"chat_id": CHAT_ID, "name": f"{name} | {contact}"})
    tid = topic["result"]["message_thread_id"] if topic.get("ok") else None
    
    caption = f"🚀 Новая заявка!\n👤 {name}\n📞 {contact}\n💬 {message}"
    send_to_thread(tid, caption, files)
    return jsonify({"status": "ok", "tid": tid}), 200

@app.route('/send_message', methods=['POST'])
def send_message():
    tid = request.form.get('tid')
    # Защита от пустых или некорректных ID
    valid_tid = tid if tid and tid not in ["None", "null", "undefined"] else None
    msg = request.form.get('message', '')
    files = request.files.getlist('files[]')
    
    send_to_thread(valid_tid, msg, files)
    return jsonify({"status": "sent"}), 200

def send_to_thread(tid, text, files):
    params = {"chat_id": CHAT_ID}
    if tid: params["message_thread_id"] = tid
    
    if not files:
        params["text"] = text
        return tg_api("sendMessage", params)
    else:
        media = []
        f_dict = {}
        for i, f in enumerate(files):
            key = f"f{i}"
            # Сохраняем оригинальное имя файла (решает проблему с ????)
            f_dict[key] = (f.filename, f.read())
            item = {"type": "document", "media": f"attach://{key}"}
            if i == 0 and text: item["caption"] = text
            media.append(item)
        params["media"] = json.dumps(media)
        return tg_api("sendMediaGroup", params, files=f_dict)

# Для работы на Vercel
if __name__ == "__main__":
    app.run()
