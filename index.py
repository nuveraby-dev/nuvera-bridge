import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Разрешаем доступ со всех доменов, чтобы Tilda не блокировала запросы
CORS(app, resources={r"/*": {"origins": "*"}})

TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
GROUP_ID = "-1003265048579"
TG_API = f"https://api.telegram.org/bot{TOKEN}"

@app.route('/ai_chat', methods=['POST', 'OPTIONS'])
def ai_chat():
    if request.method == 'OPTIONS': return jsonify({}), 200
    try:
        name = request.form.get("name", "Клиент")
        # 1. Создаем тему в Telegram
        topic = requests.post(f"{TG_API}/createForumTopic", data={"chat_id": GROUP_ID, "name": f"КЛИЕНТ: {name}"}).json()
        tid = topic.get("result", {}).get("message_thread_id")
        
        if tid:
            # 2. Формируем текст сообщения
            admin_url = f"{request.form.get('admin_link')}?tid={tid}"
            msg_text = f"👤 Имя: {name}\n📞 Контакт: {request.form.get('contact')}\n💬 Сообщение: {request.form.get('message')}\n\n🔗 Ссылка для ответа: {admin_url}"
            requests.post(f"{TG_API}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": tid, "text": msg_text})
            
            # 3. Отправляем все прикрепленные файлы
            files = request.files.getlist("files[]")
            for f in files:
                if f.filename:
                    requests.post(f"{TG_API}/sendDocument", params={"chat_id": GROUP_ID, "message_thread_id": tid}, files={"document": (f.filename, f.read())})
            
            return jsonify({"status": "ok", "tid": tid})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    return jsonify({"status": "error"}), 400

@app.route('/send_message', methods=['POST'])
def send_message():
    tid = request.form.get("tid")
    if tid:
        msg = request.form.get("message")
        if msg: requests.post(f"{TG_API}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": tid, "text": msg})
        
        files = request.files.getlist("files[]")
        for f in files:
            if f.filename:
                requests.post(f"{TG_API}/sendDocument", params={"chat_id": GROUP_ID, "message_thread_id": tid}, files={"document": (f.filename, f.read())})
    return jsonify({"status": "ok"})
