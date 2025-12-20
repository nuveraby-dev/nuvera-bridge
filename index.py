import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
GROUP_ID = "-1003265048579"
URL = f"https://api.telegram.org/bot{TOKEN}"

@app.route('/ai_chat', methods=['POST'])
def ai_chat():
    try:
        d = request.form
        name = d.get('name', 'клиент')
        res = requests.post(f"{URL}/createForumTopic", data={"chat_id": GROUP_ID, "name": f"заказ: {name}"}).json()
        tid = res.get("result", {}).get("message_thread_id")
        
        if tid:
            base_url = d.get('admin_link').split('?')[0].split('#')[0].rstrip('/')
            admin_url = f"{base_url}/#tid={tid}"
            
            text = f"🌟 **nuvera live: новый заказ**\n👤 клиент: {name}\n📞 связь: {d.get('contact')}\n\n🔗 ответить на сайте:\n{admin_url}"
            requests.post(f"{URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": tid, "text": text, "parse_mode": "Markdown"})
            
            if 'files[]' in request.files:
                for f in request.files.getlist('files[]'):
                    requests.post(f"{URL}/sendDocument", params={"chat_id": GROUP_ID, "message_thread_id": tid}, files={"document": (f.filename, f.read())})
            
            return jsonify({"status": "ok", "tid": tid})
    except Exception as e:
        return jsonify({"status": "error", "m": str(e)}), 500
    return jsonify({"status": "error"}), 400

@app.route('/send_message', methods=['POST'])
def send_message():
    tid = request.form.get("tid")
    msg = request.form.get("message")
    is_admin = request.form.get("is_admin") == 'true' # Жесткая проверка флага
    
    if tid and msg:
        # КЛЮЧЕВОЕ: если пишет админ с сайта, в Телеграм бот это НЕ отправляет
        if not is_admin:
            requests.post(f"{URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": tid, "text": msg})
        
    return jsonify({"status": "ok"})
