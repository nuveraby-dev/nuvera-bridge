from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

BOT_TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
ADMIN_ID = "1055949397" # Ваш ID

# Хранилище сообщений для сайта и выбранных имен операторов
messages_store = {}
operator_names = {} # Здесь храним, кто сейчас "дежурит"

def send_tg_buttons(chat_id):
    """Отправляет кнопки выбора имени в Telegram"""
    reply_markup = {
        "keyboard": [
            [{"text": "Евгений"}, {"text": "Александр"}, {"text": "Яна"}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                  json={"chat_id": chat_id, "text": "Выберите, от чьего имени будете отвечать:", "reply_markup": reply_markup})

@app.route('/api/ai_chat', methods=['POST'])
def initial():
    chat_id = request.form.get('chat_id')
    name = request.form.get('name', 'Клиент')
    msg = request.form.get('message', '')
    file = request.files.get('file')

    text = f"🚀 НОВЫЙ ЧАТ\n👤 Имя: {name}\n🆔 ID чата: {chat_id}\n💬 Сообщение: {msg}"
    
    # Отправляем уведомление админу
    if file:
        files = {'document': (file.filename, file.read())}
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument", data={'chat_id': ADMIN_ID, 'caption': text}, files=files)
    else:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={'chat_id': ADMIN_ID, 'text': text})
    
    # При первом сообщении предлагаем выбрать имя, если оно еще не выбрано
    if ADMIN_ID not in operator_names:
        send_tg_buttons(ADMIN_ID)
        
    return jsonify({"status": "ok"}), 200

@app.route('/api/telegram_webhook', methods=['POST'])
def webhook():
    data = request.json
    if "message" not in data: return "OK", 200
    
    msg = data["message"]
    user_id = str(msg.get("from", {}).get("id"))
    text = msg.get("text", "")

    # 1. Если нажали на кнопку с именем
    if text in ["Евгений", "Александр", "Яна"]:
        operator_names[user_id] = text
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                      json={"chat_id": user_id, "text": f"✅ Теперь вы отвечаете как: {text}"})
        return "OK", 200

    # 2. Если это ответ на сообщение (Reply)
    if "reply_to_message" in msg:
        reply_text = msg["reply_to_message"].get("text", msg["reply_to_message"].get("caption", ""))
        if "ID чата: " in reply_text:
            cid = reply_text.split("ID чата: ")[1].split("\n")[0].strip()
            
            # Берем выбранное имя или стандартное
            current_name = operator_names.get(user_id, "Менеджер")
            
            if cid not in messages_store: messages_store[cid] = []
            
            # Обработка файлов в ответе
            file_url = ""
            if "document" in msg:
                fid = msg["document"]["file_id"]
                f_info = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={fid}").json()
                file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{f_info['result']['file_path']}"

            messages_store[cid].append({
                "text": text if text else "Файл во вложении",
                "sender": current_name,
                "file_url": file_url
            })
            
    return "OK", 200

@app.route('/api/get_messages', methods=['GET'])
def get():
    cid = request.args.get('chat_id')
    msgs = messages_store.get(cid, [])
    messages_store[cid] = []
    return jsonify({"new_messages": msgs})

@app.route('/api/send_message', methods=['POST'])
def send():
    d = request.json
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                  json={'chat_id': ADMIN_ID, 'text': f"📩 Сообщение (ID чата: {d['chat_id']}):\n{d['message']}"})
    return "OK"
