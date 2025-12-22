import os
import telebot
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS

app = Flask(__name__)
# Принудительная настройка CORS для всех маршрутов
CORS(app, resources={r"/*": {"origins": "*"}})

TOKEN = "7709282362:AAG84Y2Y2Dsc067e7E_B18eHhFmY-fG2880"
CHAT_ID = "-1002345686001"
bot = telebot.TeleBot(TOKEN)

# Вспомогательная функция для добавления CORS заголовков в каждый ответ
def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response

@app.route('/ai_chat', methods=['POST', 'OPTIONS'])
def ai_chat():
    # Обработка предварительного запроса браузера (Preflight)
    if request.method == 'OPTIONS':
        return _corsify_actual_response(make_response())

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

        for f in files:
            if f.filename:
                # Передаем файл как (имя, данные) для предотвращения 500 ошибки
                bot.send_document(CHAT_ID, (f.filename, f.read()), message_thread_id=target_tid)

        res = jsonify({"status": "ok", "tid": target_tid})
        return _corsify_actual_response(res)
    except Exception as e:
        print(f"Server Error: {str(e)}")
        res = jsonify({"status": "error", "message": str(e)})
        return _corsify_actual_response(make_response(res, 500))

@app.route('/get_messages', methods=['GET'])
def get_messages():
    # Заглушка для опросника, чтобы не было 500 ошибки в логах
    return _corsify_actual_response(jsonify({"messages": []}))
