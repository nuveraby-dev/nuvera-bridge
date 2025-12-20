import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
# Разрешаем запросы с любого домена, чтобы убрать CORS error
CORS(app)

# Твои данные теперь в коде
TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
CHAT_ID = "1055949397"

def send_to_tg(text, files=None):
    # Отправка текстового сообщения
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})
    
    # Если есть прикрепленные файлы, отправляем их по очереди
    if files:
        for f in files:
            f.seek(0)
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendDocument", 
                          data={"chat_id": CHAT_ID}, 
                          files={"document": (f.filename, f.read())})

@app.route('/ai_chat', methods=['POST'])
def ai_chat():
    name = request.form.get('name', 'Не указано')
    contact = request.form.get('contact', 'Не указано')
    message = request.form.get('message', '')
    files = request.files.getlist('files[]')
    
    text = f"🚀 <b>Новая заявка!</b>\n👤 <b>Имя:</b> {name}\n📞 <b>Контакт:</b> {contact}\n💬 <b>Сообщение:</b> {message}"
    
    try:
        send_to_tg(text, files)
        # Генерируем ID чата для фронтенда
        tid = "chat_" + str(abs(hash(contact)))
        return jsonify({"status": "ok", "tid": tid}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/send_message', methods=['POST'])
def send_message():
    # Обработка последующих сообщений в открытом чате
    tid = request.form.get('tid', 'Unknown')
    message = request.form.get('message', '')
    files = request.files.getlist('files[]')
    
    text = f"💬 <b>Новое сообщение</b> (ID: {tid})\n\n{message}"
    
    try:
        send_to_tg(text, files)
        return jsonify({"status": "sent"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_updates', methods=['GET'])
def get_updates():
    # Заглушка для лонг-поллинга
    return jsonify({"messages": []}), 200

# Необходимо для деплоя на Vercel
if __name__ == "__main__":
    app.run()
