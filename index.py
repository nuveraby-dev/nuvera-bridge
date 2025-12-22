import os
import telebot
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- ВАШИ ДАННЫЕ ---
TOKEN = "7709282362:AAG84Y2Y2Dsc067e7E_B18eHhFmY-fG2880"
CHAT_ID = "-1002345686001" # ID вашей группы (обязательно с -100)
# ------------------

bot = telebot.TeleBot(TOKEN)

@app.route('/ai_chat', methods=['POST'])
def ai_chat():
    try:
        # Получаем данные из FormData
        tid = request.form.get('tid') 
        name = request.form.get('name', 'Гость')
        contact = request.form.get('contact', '-')
        message = request.form.get('message', '')
        files = request.files.getlist('files[]')

        # Если TID пришел — пишем в старый топик
        if tid:
            target_tid = int(tid)
            if message:
                bot.send_message(CHAT_ID, f"💬 {message}", message_thread_id=target_tid)
        
        # Если TID нет — создаем новый топик (новую ветку)
        else:
            # Создаем топик в группе
            topic = bot.create_forum_topic(CHAT_ID, f"Заявка: {name}")
            target_tid = topic.message_thread_id
            
            # Отправляем карточку клиента первым сообщением в топик
            welcome_text = f"🚀 **Новая заявка!**\n👤 Имя: {name}\n📞 Контакт: {contact}\n\n📝 Сообщение: {message}"
            bot.send_message(CHAT_ID, welcome_text, message_thread_id=target_tid, parse_mode="Markdown")

        # Если к сообщению прикреплены файлы
        for file in files:
            file_content = file.read()
            if file_content:
                bot.send_document(
                    CHAT_ID, 
                    file_content, 
                    visible_file_name=file.filename, 
                    message_thread_id=target_tid
                )

        # Возвращаем TID фронтенду, чтобы он его сохранил в localStorage
        return jsonify({"status": "ok", "tid": target_tid})

    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Для локальной отладки
if __name__ == '__main__':
    app.run(port=5000)
