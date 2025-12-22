import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Твой актуальный токен и ID группы
TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
CHAT_ID = "-1002361665448"

def send_to_tg(text, files=None):
    # 1. Отправляем текст
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})
    
    # 2. Отправляем файлы
    if files:
        for f in files:
            try:
                f.seek(0)
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendDocument", 
                              data={"chat_id": CHAT_ID}, 
                              files={"document": (f.filename, f.read())})
            except Exception as e:
                print(f"Ошибка отправки файла: {e}")

@app.route('/ai_chat', methods=['POST'])
def ai_chat():
    try:
        name = request.form.get('name', 'Не указано')
        contact = request.form.get('contact', 'Не указано')
        message = request.form.get('message', '')
        files = request.files.getlist('files[]')
        
        tg_text = f"🚀 <b>Новая заявка!</b>\n👤 <b>Имя:</b> {name}\n📞 <b>Контакт:</b> {contact}\n💬 <b>Сообщение:</b> {message}"
        send_to_tg(tg_text, files)
        
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
        
        send_to_tg(f"💬 <b>Сообщение ({tid}):</b>\n{message}", files)
        return jsonify({"status": "sent"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_updates', methods=['GET'])
def get_updates():
    return jsonify({"messages": []}), 200

if __name__ == "__main__":
    app.run()
