from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
# ID группы (супергруппы), где включены темы
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

        # 1. Создаем новую тему для клиента
        topic_res = tg_api("createForumTopic", {"chat_id": CHAT_ID, "name": f"{name} | {contact}"}).json()
        
        if not topic_res.get("ok"):
            return jsonify({"error": "Failed to create topic"}), 500
            
        thread_id = topic_res["result"]["message_thread_id"]
        caption = f"🚀 **Новая заявка!**\n👤 Имя: {name}\n📞 Контакт: {contact}\n💬 {message}"

        # 2. Отправляем контент в созданную тему
        send_to_thread(thread_id, caption, files)

        return jsonify({"status": "ok", "tid": thread_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/send_message', methods=['POST'])
def send_message():
    try:
        thread_id = request.form.get('tid') # Получаем ID топика из localStorage клиента
        message = request.form.get('message', '')
        files = request.files.getlist('files[]')

        if thread_id:
            send_to_thread(thread_id, message, files)
            return jsonify({"status": "sent"}), 200
        return jsonify({"error": "No thread ID"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def send_to_thread(thread_id, text, files):
    if not files:
        if text:
            tg_api("sendMessage", {"chat_id": CHAT_ID, "message_thread_id": thread_id, "text": text, "parse_mode": "Markdown"})
    else:
        media = []
        files_dict = {}
        for i, f in enumerate(files):
            f_key = f"f{i}"
            f.seek(0)
            files_dict[f_key] = (f.filename, f.read())
            item = {"type": "document", "media": f"attach://{f_key}"}
            if i == 0 and text: item["caption"] = text
            media.append(item)
        
        tg_api("sendMediaGroup", {
            "chat_id": CHAT_ID, 
            "message_thread_id": thread_id, 
            "media": json.dumps(media)
        }, files=files_dict)
