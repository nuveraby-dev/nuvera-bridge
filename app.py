import requests
import re
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Ваши данные остаются прежними
TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
CHAT_ID = "1055949397"
storage = {}

@app.route('/api/ai_chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        res = make_response("", 200)
        res.headers["Access-Control-Allow-Origin"] = "*"
        res.headers["Access-Control-Allow-Headers"] = "*"
        res.headers["Access-Control-Allow-Methods"] = "*"
        return res
    
    try:
        # Пытаемся взять данные из формы (для файлов) или из JSON
        uid = request.form.get('user_id') or request.json.get('user_id', 'anon')
        user_name = request.form.get('name') or request.json.get('name', 'Не указано')
        msg = request.form.get('message') or request.json.get('message', '')
        file = request.files.get('file')

        caption = f"📩 <b>Новое сообщение!</b>\n👤 Имя: {user_name}\n🆔 ID: <code>[{uid}]</code>\n\n📝 Текст: {msg}"

        if file:
            # Если есть файл, отправляем его методом sendDocument
            files = {'document': (file.filename, file.read())}
            tg_res = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendDocument", 
                                   data={"chat_id": CHAT_ID, "caption": caption, "parse_mode": "HTML"}, 
                                   files=files, timeout=20)
        else:
            # Если файла нет, отправляем обычный текст
            tg_res = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                   json={"chat_id": CHAT_ID, "text": caption, "parse_mode": "HTML"}, timeout=10)
        
        return jsonify({"status": "ok", "tg_status": tg_res.status_code}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/get_answer', methods=['GET'])
def get_answer():
    uid = request.args.get('user_id')
    ans = storage.get(uid)
    if ans: del storage[uid]
    return jsonify({"answer": ans})

@app.route('/api/tg_webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data and "message" in data and "reply_to_message" in data["message"]:
        txt = data["message"].get("text")
        orig = data["message"]["reply_to_message"].get("text", "")
        match = re.search(r"\[(\w+)\]", orig)
        if match and txt: storage[match.group(1)] = txt
    return jsonify({"status": "ok"})

@app.route('/')
def home(): return "Bridge is active", 200
