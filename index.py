import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
GROUP_ID = "-1003265048579"
URL = f"https://api.telegram.org/bot{TOKEN}"

def send_to_tg(tid, files):
    """Универсальная функция отправки любых файлов в TG"""
    for f in files:
        if f.filename:
            requests.post(f"{URL}/sendDocument", params={"chat_id": GROUP_ID, "message_thread_id": tid}, files={"document": (f.filename, f.read())})

@app.route('/ai_chat', methods=['POST'])
def ai_chat():
    try:
        d = request.form
        name = d.get('name', 'клиент')
        res = requests.post(f"{URL}/createForumTopic", data={"chat_id": GROUP_ID, "name": f"заказ: {name}"}).json()
        tid = res.get("result", {}).get("message_thread_id")
        
        if tid:
            # Ссылка теперь всегда ведет на главную с параметром tid
            admin_url = f"{d.get('admin_link')}?tid={tid}"
            text = f"🆕 **новый заказ**\n\n👤 имя: {name}\n📞 связь: {d.get('contact')}\n\n🔗 **ответить клиенту:**\n{admin_url}"
            
            requests.post(f"{URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": tid, "text": text, "parse_mode": "Markdown"})
            
            if 'files[]' in request.files:
                send_to_tg(tid, request.files.getlist('files[]'))
            
            return jsonify({"status": "ok", "tid": tid})
    except Exception as e:
        return jsonify({"status": "error", "m": str(e)}), 500
    return jsonify({"status": "error"}), 400

@app.route('/send_message', methods=['POST'])
def send_message():
    tid = request.form.get("tid")
    msg = request.form.get("message")
    if tid:
        if msg: requests.post(f"{URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": tid, "text": msg})
        if 'files[]' in request.files:
            send_to_tg(tid, request.files.getlist('files[]'))
    return jsonify({"status": "ok"})
