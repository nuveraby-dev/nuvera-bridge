from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
CHAT_ID = "-1003265048579"

def send_to_tg(method, data=None, files=None):
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    r = requests.post(url, data=data, files=files, json=data if not files else None)
    print(f"TG Response ({method}): {r.status_code} - {r.text}") # Логи для отладки
    return r

@app.route('/ai_chat', methods=['POST'])
def ai_chat():
    try:
        name = request.form.get('name', 'Не указано')
        contact = request.form.get('contact', 'Не указано')
        message = request.form.get('message', '')
        files = request.files.getlist('files[]')
        
        caption = f"🚀 <b>Новая заявка!</b>\n👤 Имя: {name}\n📞 Контакт: {contact}\n💬 Сообщение: {message}"
        send_to_tg("sendMessage", data={"chat_id": CHAT_ID, "text": caption, "parse_mode": "HTML"})
        
        if files:
            for f in files:
                f.seek(0)
                send_to_tg("sendDocument", data={"chat_id": CHAT_ID}, files={"document": (f.filename, f.read())})
        
        tid = "chat_" + str(abs(hash(contact)))
        return jsonify({"status": "ok", "tid": tid}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/send_message', methods=['POST'])
def send_message():
    try:
        tid = request.form.get('tid', 'Unknown')
        message = request.form.get('message', '')
        files = request.files.getlist('files[]')
        
        if message:
            text = f"💬 Сообщение ({tid}):\n{message}"
            send_to_tg("sendMessage", data={"chat_id": CHAT_ID, "text": text})
        
        if files:
            for f in files:
                f.seek(0)
                send_to_tg("sendDocument", data={"chat_id": CHAT_ID}, files={"document": (f.filename, f.read())})
        return jsonify({"status": "sent"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return "SERVER IS RUNNING", 200
