from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
# Разрешаем запросы, чтобы Tilda могла общаться с сервером
CORS(app)

TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
# Твой актуальный ID из логов
CHAT_ID = "-1003265048579"

@app.route('/', methods=['GET'])
def home():
    try:
        tg_check = requests.get(f"https://api.telegram.org/bot{TOKEN}/getMe").json()
        status = "СВЯЗЬ С TG ЕСТЬ ✅" if tg_check.get('ok') else "ОШИБКА ТОКЕНА ❌"
    except:
        status = "СЕРВЕР НЕ МОЖЕТ ДОСТУЧАТЬСЯ ДО TG ❌"
    return f"СЕРВЕР NUVERA РАБОТАЕТ. СТАТУС: {status}", 200

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
        
        # Генерируем уникальный ID чата для фронтенда
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
