from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
# Разрешаем запросы со всех доменов, чтобы Tilda не блокировала ответ
CORS(app)

TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
CHAT_ID = "-1002361665448"

# Главная страница для проверки работоспособности
@app.route('/', methods=['GET'])
def home():
    return "SERVER OK. NUVERA BRIDGE IS ACTIVE.", 200

@app.route('/ai_chat', methods=['POST'])
def ai_chat():
    try:
        name = request.form.get('name', 'Не указано')
        contact = request.form.get('contact', 'Не указано')
        message = request.form.get('message', '')
        files = request.files.getlist('files[]')
        
        caption = f"🚀 <b>Новая заявка!</b>\n👤 Имя: {name}\n📞 Контакт: {contact}\n💬 Сообщение: {message}"
        
        # 1. Отправляем текст в Telegram
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      json={"chat_id": CHAT_ID, "text": caption, "parse_mode": "HTML"})
        
        # 2. Отправляем файлы, если они есть
        if files:
            for f in files:
                f.seek(0)
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendDocument", 
                              data={"chat_id": CHAT_ID}, 
                              files={"document": (f.filename, f.read())})
        
        return jsonify({"status": "ok", "tid": "chat_" + str(abs(hash(contact)))}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/send_message', methods=['POST'])
def send_message():
    try:
        tid = request.form.get('tid', 'Unknown')
        message = request.form.get('message', '')
        files = request.files.getlist('files[]')
        
        text = f"💬 Сообщение ({tid}):\n{message}"
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      json={"chat_id": CHAT_ID, "text": text})
        
        if files:
            for f in files:
                f.seek(0)
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendDocument", 
                              data={"chat_id": CHAT_ID}, 
                              files={"document": (f.filename, f.read())})
        return jsonify({"status": "sent"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
