import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Замени на свои данные или добавь их в Environment Variables на Vercel
TOKEN = os.environ.get('TELEGRAM_TOKEN', 'ТВОЙ_ТОКЕН_БОТА')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', 'ТВОЙ_ID_ЧАТА')

def send_to_tg(text, files=None):
    # Отправка текста
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})
    
    # Отправка файлов, если они есть
    if files:
        url_file = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
        for f in files:
            f.seek(0)
            requests.post(url_file, data={"chat_id": CHAT_ID}, files={"document": (f.filename, f.read())})

@app.route('/ai_chat', methods=['POST', 'OPTIONS'])
def ai_chat():
    if request.method == 'OPTIONS': return jsonify({}), 200
    
    name = request.form.get('name', 'Не указано')
    contact = request.form.get('contact', 'Не указано')
    message = request.form.get('message', '')
    files = request.files.getlist('files[]')
    
    tg_text = f"<b>🚀 Новая заявка</b>\n\n<b>Имя:</b> {name}\n<b>Контакт:</b> {contact}\n<b>Сообщение:</b> {message}"
    
    try:
        send_to_tg(tg_text, files)
        # Генерируем ID темы/чата (в данном примере просто случайный)
        tid = str(abs(hash(contact))) 
        return jsonify({"status": "success", "tid": tid}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/send_message', methods=['POST', 'OPTIONS'])
def send_message():
    if request.method == 'OPTIONS': return jsonify({}), 200
    
    tid = request.form.get('tid')
    message = request.form.get('message', '')
    files = request.files.getlist('files[]')
    
    tg_text = f"<b>💬 Сообщение из чата (ID: {tid})</b>\n\n{message}"
    
    try:
        send_to_tg(tg_text, files)
        return jsonify({"status": "sent"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_updates', methods=['GET'])
def get_updates():
    # Заглушка, чтобы фронтенд не выдавал ошибку при опросе
    return jsonify({"messages": []}), 200

# Это важно для Vercel
app.debug = True
