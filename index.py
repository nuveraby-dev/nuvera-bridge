from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
# Разрешаем CORS для вашего домена
CORS(app, resources={r"/*": {"origins": "*"}})

TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
CHAT_ID = "-1003265048579"

def tg_api(method, data, files=None):
    try:
        r = requests.post(f"https://api.telegram.org/bot{TOKEN}/{method}", data=data, files=files, timeout=20)
        return r.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}

# Заглушка для корня и иконок (убирает 404 в логах)
@app.route('/')
@app.route('/favicon.ico')
@app.route('/favicon.png')
def home():
    return "Bridge is active", 200

@app.route('/ai_chat', methods=['POST', 'OPTIONS'])
def ai_chat():
    if request.method == 'OPTIONS': return _build_cors_preflight_response()
    
    name = request.form.get('name', 'Гость')
    contact = request.form.get('contact', '-')
    message = request.form.get('message', '')
    files = request.files.getlist('files[]')
    
    topic = tg_api("createForumTopic", {"chat_id": CHAT_ID, "name": f"{name} | {contact}"})
    tid = topic["result"]["message_thread_id"] if topic.get("ok") else None
    
    caption = f"👤 {name}\n📞 {contact}\n💬 {message}"
    send_to_thread(tid, caption, files)
    return _corsify_actual_response(jsonify({"status": "ok", "tid": tid}))

@app.route('/send_message', methods=['POST', 'OPTIONS'])
def send_message():
    if request.method == 'OPTIONS': return _build_cors_preflight_response()
    
    tid = request.form.get('tid')
    valid_tid = tid if tid and tid not in ["None", "null", "undefined"] else None
    msg = request.form.get('message', '')
    files = request.files.getlist('files[]')
    
    send_to_thread(valid_tid, msg, files)
    return _corsify_actual_response(jsonify({"status": "sent"}))

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
            # Исправляем кодировку имени файла (убираем ????)
            f_dict[key] = (f.filename.encode('utf-8').decode('latin-1'), f.read())
            item = {"type": "document", "media": f"attach://{key}"}
            if i == 0 and text: item["caption"] = text
            media.append(item)
        params["media"] = json.dumps(media)
        return tg_api("sendMediaGroup", params, files=f_dict)

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response
