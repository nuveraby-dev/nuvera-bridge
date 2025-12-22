from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
# Полный доступ для Tilda, чтобы убрать "Provisional headers"
CORS(app, resources={r"/*": {"origins": "*"}})

TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
CHAT_ID = "-1003265048579"

@app.route('/')
@app.route('/favicon.ico')
def health():
    return "API Active", 200

@app.route('/ai_chat', methods=['POST', 'OPTIONS'])
def ai_chat():
    if request.method == 'OPTIONS': return _cors_preflight()
    
    name = request.form.get('name', 'Гость')
    contact = request.form.get('contact', '-')
    message = request.form.get('message', '')
    files = request.files.getlist('files[]')
    
    # Создание топика
    t_res = tg_api("createForumTopic", {"chat_id": CHAT_ID, "name": f"{name} | {contact}"})
    
    if not t_res.get("ok"):
        return _corsify(jsonify({"status": "error", "reason": "TG_TOPIC_FAIL", "details": t_res}), 500)
        
    tid = t_res["result"]["message_thread_id"]
    caption = f"🚀 Новая заявка!\n👤 {name}\n📞 {contact}\n💬 {message}"
    
    tg_send_res = send_to_thread(tid, caption, files)
    return _corsify(jsonify({"status": "ok", "tid": tid, "tg_debug": tg_send_res}))

@app.route('/send_message', methods=['POST', 'OPTIONS'])
def send_message():
    if request.method == 'OPTIONS': return _cors_preflight()
    
    tid = request.form.get('tid')
    msg = request.form.get('message', '')
    files = request.files.getlist('files[]')
    
    res = send_to_thread(tid, msg, files)
    return _corsify(jsonify({"status": "sent", "tg_debug": res}))

def tg_api(method, data, files=None):
    try:
        r = requests.post(f"https://api.telegram.org/bot{TOKEN}/{method}", data=data, files=files, timeout=25)
        return r.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}

def send_to_thread(tid, text, files):
    params = {"chat_id": CHAT_ID, "message_thread_id": tid}
    if not files:
        params["text"] = text
        return tg_api("sendMessage", params)
    else:
        media, f_dict = [], {}
        for i, f in enumerate(files):
            key = f"f{i}"
            # Исправление кодировки для кириллицы (убираем ????)
            f_dict[key] = (f.filename.encode('utf-8').decode('latin-1'), f.read())
            item = {"type": "document", "media": f"attach://{key}"}
            if i == 0 and text: item["caption"] = text
            media.append(item)
        params["media"] = json.dumps(media)
        return tg_api("sendMediaGroup", params, files=f_dict)

def _cors_preflight():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def _corsify(res, status=200):
    res.headers.add("Access-Control-Allow-Origin", "*")
    return res, status
