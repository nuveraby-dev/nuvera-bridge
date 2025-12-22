from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
CHAT_ID = "-1003265048579"

@app.route('/ai_chat', methods=['POST'])
def ai_chat():
    return process_request(is_first_chat=True)

@app.route('/send_message', methods=['POST'])
def send_message():
    return process_request(is_first_chat=False)

def process_request(is_first_chat):
    try:
        tid = request.form.get('tid', 'New user')
        name = request.form.get('name', '')
        contact = request.form.get('contact', '')
        message = request.form.get('message', '')
        files = request.files.getlist('files[]')

        # Формируем текст подписи
        if is_first_chat:
            caption = f"🚀 Новая заявка!\n👤 {name}\n📞 {contact}\n💬 {message}"
        else:
            caption = f"💬 ({tid}): {message}"

        if not files:
            # Если файлов нет, просто шлем текст
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                          json={"chat_id": CHAT_ID, "text": caption})
        else:
            # Если файлы есть, группируем их в альбом
            media = []
            files_to_send = {}
            
            for i, f in enumerate(files):
                file_key = f"file{i}"
                f.seek(0)
                files_to_send[file_key] = (f.filename, f.read())
                
                # Первый файл получает подпись (caption)
                media_item = {"type": "document", "media": f"attach://{file_key}"}
                if i == 0:
                    media_item["caption"] = caption
                media.append(media_item)

            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMediaGroup",
                          data={"chat_id": CHAT_ID, "media": json.dumps(media)},
                          files=files_to_send)

        return jsonify({"status": "ok", "tid": tid}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return "SERVER RUNNING", 200
