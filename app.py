import requests
import re
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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
        # Пытаемся взять данные из формы
        uid = request.form.get('user_id', 'anon')
        user_name = request.form.get('name', 'Не указано')
        msg = request.form.get('message', '')
        file = request.files.get('file')

        caption = f"📩 <b>Новое сообщение!</b>\n👤 Имя: {user_name}\n🆔 ID: <code>[{uid}]</code>\n\n📝 Текст: {msg}"

        if file:
            files = {'document': (file.filename, file.read())}
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendDocument", 
                          data={"chat_id": CHAT_ID, "caption": caption, "parse_mode": "HTML"}, 
                          files=files)
        else:
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                          json={"chat_id": CHAT_ID, "text": caption, "parse_mode": "HTML"})
        
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/get_answer', methods=['GET'])
def get_answer():
    uid = request.args.get('user_id')
    return jsonify({"answer": storage.get(uid)})

@app.route('/')
def home(): return "Bridge is active", 200
