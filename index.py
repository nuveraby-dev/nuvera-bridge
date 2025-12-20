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
        # 1. Создаем отдельную тему для клиента
        res = requests.post(f"{URL}/createForumTopic", data={"chat_id": GROUP_ID, "name": f"заказ: {name}"}).json()
        tid = res.get("result", {}).get("message_thread_id")
        
        if tid:
            # 2. Формируем ссылку, которая откроет чат именно с этим tid
            admin_url = f"{d.get('admin_link')}?tid={tid}"
            
            text = (
                f"🆕 **новый заказ**\n\n"
                f"👤 имя: {name}\n"
                f"📞 связь: {d.get('contact')}\n"
                f"💬 сообщение: {d.get('message')}\n\n"
                f"🔗 **ответить клиенту в чате:**\n{admin_url}"
            )
            
            # Отправляем уведомление в тему
            requests.post(f"{URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": tid, "text": text, "parse_mode": "Markdown"})
            
            # Отправляем файлы, если они есть
            if 'files[]' in request.files:
                for f in request.files.getlist('files[]'):
                    if f.filename:
                        requests.post(f"{URL}/sendDocument", params={"chat_id": GROUP_ID, "message_thread_id": tid}, files={"document": (f.filename, f.read())})
            
            return jsonify({"status": "ok", "tid": tid})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500
    return jsonify({"status": "error"}), 400

@app.route('/send_message', methods=['POST'])
def send_message():
    tid = request.form.get("tid")
    msg = request.form.get("message")
    if tid and msg:
        requests.post(f"{URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": tid, "text": msg})
    return jsonify({"status": "ok"})
