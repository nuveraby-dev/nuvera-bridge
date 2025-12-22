import os
import telebot
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TOKEN = "7709282362:AAG84Y2Y2Dsc067e7E_B18eHhFmY-fG2880"
CHAT_ID = "-1002345686001"
bot = telebot.TeleBot(TOKEN)

# Временное хранилище для ответов оператора (в идеале использовать Redis)
operator_replies = {}

@app.route('/ai_chat', methods=['POST'])
def ai_chat():
    try:
        tid = request.form.get('tid')
        name = request.form.get('name', 'Гость')
        contact = request.form.get('contact', '-')
        message = request.form.get('message', '')
        files = request.files.getlist('files[]')

        if tid and tid != "null":
            target_tid = int(tid)
            if message:
                bot.send_message(CHAT_ID, f"{message}", message_thread_id=target_tid)
        else:
            topic = bot.create_forum_topic(CHAT_ID, f"Заявка: {name}")
            target_tid = topic.message_thread_id
            header = f"🚀 Новая заявка!\n👤 Имя: {name}\n📞 Контакт: {contact}\n\n💬 {message}"
            bot.send_message(CHAT_ID, header, message_thread_id=target_tid)

        for file in files:
            bot.send_document(CHAT_ID, file.read(), visible_file_name=file.filename, message_thread_id=target_tid)

        return jsonify({"status": "ok", "tid": target_tid})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Эндпоинт для получения ответов из ТГ на сайт
@app.route('/get_messages', methods=['GET'])
def get_messages():
    tid = request.args.get('tid')
    if tid in operator_replies:
        msgs = operator_replies[tid]
        operator_replies[tid] = [] # Очищаем после получения
        return jsonify({"messages": msgs})
    return jsonify({"messages": []})

# Вебхук или обработчик ответов (для работы на Vercel лучше использовать Polling в отдельном процессе или Webhook)
@bot.message_handler(func=lambda m: m.reply_to_message is not None)
def handle_reply(message):
    t_id = str(message.message_thread_id)
    if t_id not in operator_replies:
        operator_replies[t_id] = []
    operator_replies[t_id].append(message.text)

if __name__ == '__main__':
    app.run(port=5000)
