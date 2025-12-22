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

        # Определяем ID топика
        if tid and tid != "undefined" and tid != "null":
            target_tid = int(tid)
        else:
            topic = bot.create_forum_topic(CHAT_ID, f"Заявка: {name}")
            target_tid = topic.message_thread_id
            header = f"🚀 Новая заявка!\n👤 Имя: {name}\n📞 Контакт: {contact}"
            bot.send_message(CHAT_ID, header, message_thread_id=target_tid)

        # Отправка текста
        if message:
            bot.send_message(CHAT_ID, message, message_thread_id=target_tid)

        # Отправка файлов
        for file in files:
            bot.send_document(CHAT_ID, (file.filename, file.read()), message_thread_id=target_tid)

        return jsonify({"status": "ok", "tid": target_tid})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Заглушка, чтобы фронтенд не получал 500 ошибку при опросе
@app.route('/get_messages', methods=['GET'])
def get_messages():
    return jsonify({"messages": []})

if __name__ == '__main__':
    app.run(port=5000)
