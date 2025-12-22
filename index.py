from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
CHAT_ID = "-1002361665448"

@app.route('/', methods=['GET'])
def home():
    try:
        # Проверяем, видит ли сервер твоего бота
        res = requests.get(f"https://api.telegram.org/bot{TOKEN}/getMe").json()
        if res.get('ok'):
            return f"✅ СЕРВЕР РАБОТАЕТ. БОТ {res['result']['username']} НА СВЯЗИ!", 200
        return "❌ ОШИБКА ТОКЕНА БОТА", 200
    except Exception as e:
        return f"❌ ОШИБКА СЕТИ: {str(e)}", 200

@app.route('/ai_chat', methods=['POST'])
def ai_chat():
    try:
        name = request.form.get('name', 'Не указано')
        contact = request.form.get('contact', 'Не указано')
        message = request.form.get('message', '')
        files = request.files.getlist('files[]')
        
        caption = f"🚀 <b>Новая заявка!</b>\n👤 Имя: {name}\n📞 Контакт: {contact}\n💬 Сообщение: {message}"
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      json={"chat_id": CHAT_ID, "text": caption, "parse_mode": "HTML"})
        
        if files:
            for f in files:
                f.seek(0)
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendDocument", 
                              data={"chat_id": CHAT_ID}, 
                              files={"document": (f.filename, f.read())})
        
        return jsonify({"status": "ok", "tid": "chat_" + str(abs(hash(contact)))}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
