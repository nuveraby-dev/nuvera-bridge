import os
import telebot
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS

app = Flask(__name__)
# Разрешаем запросы конкретно с вашего домена
CORS(app, resources={r"/*": {"origins": "*"}})

TOKEN = "7709282362:AAG84Y2Y2Dsc067e7E_B18eHhFmY-fG2880"
CHAT_ID = "-1002345686001"
bot = telebot.TeleBot(TOKEN)

def _cors_res(data, status=200):
    response = make_response(jsonify(data), status)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

@app.route('/ai_chat', methods=['POST', 'OPTIONS'])
def ai_chat():
    if request.method == 'OPTIONS':
        return _cors_res({"status": "ok"})
        
    try:
        tid = request.form.get('tid')
        name = request.form.get('name', 'Гость')
        contact = request.form.get('contact', '-')
        message = request.form.get('message', '')
        files = request.files.getlist('files[]')

        if tid and tid not in ["null", "undefined", ""]:
            target_tid = int(tid)
        else:
            topic = bot.create_forum_topic(CHAT_ID, f"Заявка: {name}")
            target_tid = topic.message_thread_id
            bot.send_message(CHAT_ID, f"🚀 **Новая заявка!**\n👤 {name}\n📞 {contact}", 
                             message_thread_id=target_tid, parse_mode="Markdown")

        if message:
            bot.send_message(CHAT_ID, message, message_thread_id=target_tid)

        # Исправленный блок отправки файлов (убирает 500 ошибку)
        for f in files:
            if f.filename:
                file_content = f.read()
                bot.send_document(CHAT_ID, (f.filename, file_content), message_thread_id=target_tid)

        return _cors_res({"status": "ok", "tid": target_tid})
    except Exception as e:
        return _cors_res({"status": "error", "message": str(e)}, 500)

@app.route('/get_messages', methods=['GET'])
def get_messages():
    return _cors_res({"messages": []})
