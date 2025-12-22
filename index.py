import os
import telebot
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TOKEN = "7709282362:AAG84Y2Y2Dsc067e7E_B18eHhFmY-fG2880"
CHAT_ID = "-1002345686001"
bot = telebot.TeleBot(TOKEN)

@app.route('/ai_chat', methods=['POST'])
def ai_chat():
    try:
        tid = request.form.get('tid')
        name = request.form.get('name', 'Гость')
        contact = request.form.get('contact', '-')
        message = request.form.get('message', '')
        files = request.files.getlist('files[]')

        # Обработка или создание топика
        if tid and tid not in ["null", "undefined", ""]:
            target_tid = int(tid)
        else:
            topic = bot.create_forum_topic(CHAT_ID, f"Заявка: {name}")
            target_tid = topic.message_thread_id
            bot.send_message(CHAT_ID, f"🚀 **Новая заявка!**\n👤 {name}\n📞 {contact}", 
                             message_thread_id=target_tid, parse_mode="Markdown")

        # Отправка текста сообщения
        if message:
            bot.send_message(CHAT_ID, message, message_thread_id=target_tid)

        # Исправленная отправка файлов
        for f in files:
            if f.filename:
                file_data = f.read()
                bot.send_document(CHAT_ID, (f.filename, file_data), message_thread_id=target_tid)

        return jsonify({"status": "ok", "tid": target_tid})
    except Exception as e:
        print(f"Server Error: {str(e)}")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/get_messages', methods=['GET'])
def get_messages():
    # Заглушка для предотвращения 500 ошибок при Long Polling без БД
    return jsonify({"messages": []})
