from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
# Максимально разрешаем запросы с любого источника (CORS)
CORS(app, resources={r"/*": {"origins": "*"}})

TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
CHAT_ID = "-1003265048579"

# 1. Убираем 404 ошибки для системных запросов
@app.route('/')
@app.route('/favicon.ico')
@app.route('/favicon.png')
def health_check():
    return "API Active", 200

# Обработка создания топика
@app.route('/ai_chat', methods=['POST'])
def ai_chat():
    name = request.form.get('name', 'Гость')
    contact = request.form.get('contact', '-')
    message = request.form.get('message', '')
    files = request.files.getlist('files[]')
    
    topic = tg_api("createForumTopic", {"chat_id": CHAT_ID, "name": f"{name} | {contact}"})
    tid = topic["result"]["message_thread_id"] if topic.get("ok") else None
    
    caption = f"🚀 Заявка!\n👤 {name}\n📞 {contact}\n💬 {message}"
    send_to_thread(tid, caption, files)
    return jsonify({"status": "ok", "tid": tid}), 200

# 2. Обработка повторных сообщений
@app.route('/send_message', methods=['POST'])
def send_message():
    tid = request.form.get('tid')
    # Очистка ID от строк типа "null"
    v_tid = tid if tid and tid not in ["None", "null", "undefined"] else None
    msg = request.form.get('message', '')
    files = request.files.getlist('files[]')
    
    send_to_thread(v_tid, msg, files)
    return jsonify({"status": "sent"}), 200

def tg_api(method, data, files=None):
    try:
        r = requests.post(f"https://api.telegram.org/bot{TOKEN}/{method}", data=data, files=files, timeout=25)
        return r.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}

def send_to_thread(tid, text, files):
    params = {"chat_id": CHAT_ID}
    if tid: params["message_thread_id"] = tid
    
    if not files:
        params["text"] = text
        return tg_api("sendMessage", params)
    else:
        media = []
        f_dict = {}
        for i, f in enumerate(files):
            key = f"f{i}"
            # 3. ИСПРАВЛЕНИЕ КОДИРОВКИ (убираем ????)
            # Передаем имя файла в правильном формате кортежа
            f_dict[key] = (f.filename, f.read())
            item = {"type": "document", "media": f"attach://{key}"}
            if i == 0 and text: item["caption"] = text
            media.append(item)
        params["media"] = json.dumps(media)
        return tg_api("sendMediaGroup", params, files=f_dict)
