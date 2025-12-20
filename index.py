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
        # Создаем новую тему
        res = requests.post(f"{URL}/createForumTopic", data={"chat_id": GROUP_ID, "name": f"Клиент: {d.get('name')}"}).json()
        tid = res.get("result", {}).get("message_thread_id")
        
        if tid:
            link = f"{d.get('admin_link')}?tid={tid}"
            text = f"👤 имя: {d.get('name')}\n📞 связь: {d.get('contact')}\n💬 вопрос: {d.get('message')}\n\n🔗 ответить: {link}"
            requests.post(f"{URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": tid, "text": text})
            
            # Логика отправки файлов
            if 'files[]' in request.files:
                for f in request.files.getlist('files[]'):
                    requests.post(f"{URL}/sendDocument", params={"chat_id": GROUP_ID, "message_thread_id": tid}, files={"document": (f.filename, f.read())})
            
            return jsonify({"status": "ok", "tid": tid})
    except Exception as e:
        return jsonify({"status": "error", "m": str(e)}), 500
    return jsonify({"status": "404"})

@app.route('/send_message', methods=['POST'])
def send_message():
    tid = request.form.get("tid")
    if tid:
        msg = request.form.get("message")
        if msg: requests.post(f"{URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": tid, "text": msg})
        if 'files[]' in request.files:
            for f in request.files.getlist('files[]'):
                requests.post(f"{URL}/sendDocument", params={"chat_id": GROUP_ID, "message_thread_id": tid}, files={"document": (f.filename, f.read())})
    return jsonify({"status": "ok"})
