from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# ВАШИ ДАННЫЕ
BOT_TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
ADMIN_ID = "1055949397"

messages_store = {}
operator_names = {}

def send_tg_buttons(chat_id):
    """Клавиатура выбора оператора"""
    reply_markup = {
        "keyboard": [[{"text": "Евгений"}, {"text": "Александр"}, {"text": "Яна"}]],
        "resize_keyboard": True
    }
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                  json={"chat_id": chat_id, "text": "Выберите оператора для ответа:", "reply_markup": reply_markup})

@app.route('/api/ai_chat', methods=['POST'])
def initial():
    chat_id = request.form.get('chat_id')
    name = request.form.get('name', '—')
    contact = request.form.get('contact', '—') # ПОЛУЧАЕМ НОМЕР ТЕЛЕФОНА
    msg = request.form.get('message', '')
    file = request.files.get('file')

    # Минималистичный шаблон сообщения для ТГ
    text = (f"🔘 **НОВЫЙ ЗАКАЗ**\n\n"
            f"👤 Клиент: {name}\n"
            f"📞 Телефон: {contact}\n"
            f"💬 Текст: {msg}\n\n"
            f"ID: `{chat_id}`")
    
    if file:
        files = {'document': (file.filename, file.read())}
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument", 
                      data={'chat_id': ADMIN_ID, 'caption': text, 'parse_mode': 'Markdown'}, files=files)
    else:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                      json={'chat_id': ADMIN_ID, 'text': text, 'parse_mode': 'Markdown'})
    
    if str(ADMIN_ID) not in operator_names:
        send_tg_buttons(ADMIN_ID)
        
    return jsonify({"status": "ok"}), 200

@app.route('/api/telegram_webhook', methods=['POST'])
def webhook():
    data = request.json
    if "message" not in data: return "OK", 200
    msg = data["message"]
    user_id = str(msg.get("from", {}).get("id"))
    text = msg.get("text", "")

    if text in ["Евгений", "Александр", "Яна"]:
        operator_names[user_id] = text
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                      json={"chat_id": user_id, "text": f"✅ Вы отвечаете как: {text}"})
        return "OK", 200

    if "reply_to_message" in msg:
        reply_msg = msg["reply_to_message"]
        reply_text = reply_msg.get("text", reply_msg.get("caption", ""))
        if "ID: " in reply_text:
            cid = reply_text.split("ID: ")[1].strip().replace('`','')
            current_name = operator_names.get(user_id, "Менеджер")
            if cid not in messages_store: messages_store[cid] = []
            
            file_url = ""
            if "document" in msg:
                fid = msg["document"]["file_id"]
                f_info = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={fid}").json()
                file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{f_info['result']['file_path']}"

            messages_store[cid].append({"text": text or "📎 Файл", "sender": current_name, "file_url": file_url})
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
                  json={'chat_id': ADMIN_ID, 'text': f"✉️ Сообщение (ID: `{d['chat_id']}`):\n{d['message']}", 'parse_mode': 'Markdown'})
    return "OK"
