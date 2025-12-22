import os
import telebot
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}) # Разрешаем запросы со всех доменов

TOKEN = "7709282362:AAG84Y2Y2Dsc067e7E_B18eHhFmY-fG2880"
CHAT_ID = "-1002345686001"
bot = telebot.TeleBot(TOKEN)

@app.route('/ai_chat', methods=['POST', 'OPTIONS'])
def ai_chat():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
        
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
                # Важно: передаем (имя_файла, контент) для стабильности
                bot.send_document(CHAT_ID, (f.filename, f.read()), message_thread_id=target_tid)

        return _corsify_actual_response(jsonify({"status": "ok", "tid": target_tid}))
    except Exception as e:
        return _corsify_actual_response(jsonify({"status": "error", "message": str(e)}), 500)

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def _corsify_actual_response(response, status=200):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response, status

@app.route('/get_messages', methods=['GET'])
def get_messages():
    # Заглушка, чтобы опрос сообщений не выдавал 500 ошибку в консоль
    return _corsify_actual_response(jsonify({"messages": []}))
