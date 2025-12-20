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
        # Создаем тему в Telegram
        res = requests.post(f"{URL}/createForumTopic", data={"chat_id": GROUP_ID, "name": f"заказ: {name}"}).json()
        tid = res.get("result", {}).get("message_thread_id")
        
        if tid:
            # Формируем прямую ссылку для входа администратора
            # Ссылка будет иметь вид: https://nuvera-print.by/?tid=123
            admin_url = f"{d.get('admin_link')}?tid={tid}"
            
            msg_text = (
                f"🆕 **новый запрос**\n\n"
                f"👤 имя: {name}\n"
                f"📞 контакт: {d.get('contact')}\n\n"
                f"🔗 **открыть чат с клиентом:**\n{admin_url}"
            )
            
            requests.post(f"{URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": tid, "text": msg_text, "parse_mode": "Markdown"})
            
            # Обработка вложений
            if 'files[]' in request.files:
                for f in request.files.getlist('files[]'):
                    if f.filename:
                        requests.post(f"{URL}/sendDocument", params={"chat_id": GROUP_ID, "message_thread_id": tid}, files={"document": (f.filename, f.read())})
            
            return jsonify({"status": "ok", "tid": tid})
    except Exception as e:
        return jsonify({"status": "error", "m": str(e)}), 500
    return jsonify({"status": "error"}), 400

@app.route('/send_message', methods=['POST'])
def send_message():
    tid = request.form.get("tid")
    msg = request.form.get("message")
    if tid and msg:
        requests.post(f"{URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": tid, "text": msg})
    return jsonify({"status": "ok"})
