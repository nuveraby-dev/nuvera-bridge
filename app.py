from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# --- ВАШИ ДАННЫЕ ---
BOT_TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
ADMIN_ID = "1055949397"

# Хранилище сообщений в памяти (для ответов админа)
messages_store = {} 

@app.route('/api/ai_chat', methods=['POST'])
def initial_contact():
    data = request.form
    chat_id = data.get('chat_id', 'unknown')
    name = data.get('name', 'Аноним')
    contact = data.get('contact', 'Не указан')
    msg = data.get('message', '')

    # Формируем сообщение для вас в Telegram
    # ВАЖНО: Не меняйте формат "ID чата: ...", по нему сервер понимает кому отвечать
    text = f"🚀 Новый клиент на сайте!\n\n👤 Имя: {name}\n📞 Контакт: {contact}\n🆔 ID чата: {chat_id}\n\n💬 Вопрос: {msg}\n\n—————\nЧтобы ответить клиенту, просто сделайте REPLY (ответить) на это сообщение."
    
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                  json={"chat_id": ADMIN_ID, "text": text})
    
    return jsonify({"status": "ok"}), 200

@app.route('/api/send_message', methods=['POST'])
def send_msg():
    data = request.json
    chat_id = data.get('chat_id')
    text = data.get('message')
    
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                  json={"chat_id": ADMIN_ID, "text": f"📩 Новое сообщение (ID чата: {chat_id}):\n{text}"})
    return jsonify({"status": "sent"}), 200

@app.route('/api/get_messages', methods=['GET'])
def get_msgs():
    chat_id = request.args.get('chat_id')
    if chat_id in messages_store and messages_store[chat_id]:
        # Отдаем накопленные ответы админа клиенту
        new_msgs = [{"text": m, "side": "admin"} for m in messages_store[chat_id]]
        messages_store[chat_id] = [] # Очищаем после выдачи
        return jsonify({"new_messages": new_msgs}), 200
    return jsonify({"new_messages": []}), 200

@app.route('/api/telegram_webhook', methods=['POST'])
def webhook():
    data = request.json
    if "message" in data and "reply_to_message" in data["message"]:
        reply_text = data["message"]["reply_to_message"]["text"]
        
        # Ищем ID чата в тексте сообщения, на которое вы ответили
        if "ID чата: " in reply_text:
            try:
                cid = reply_text.split("ID чата: ")[1].split("\n")[0].strip()
                admin_answer = data["message"].get("text", "")
                
                if cid not in messages_store:
                    messages_store[cid] = []
                messages_store[cid].append(admin_answer)
            except Exception as e:
                print(f"Ошибка парсинга ID: {e}")
        
    return "OK", 200

@app.route('/')
def home():
    return "Nuvera Bridge API is running!"
