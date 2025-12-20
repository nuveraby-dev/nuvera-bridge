import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
GROUP_ID = "-1003265048579"
URL = f"https://api.telegram.org/bot{TOKEN}"

# Хранилище для передачи сообщений из ТГ на сайт
live_storage = {}

@app.route('/ai_chat', methods=['POST'])
def ai_chat():
    d = request.form
    res = requests.post(f"{URL}/createForumTopic", data={"chat_id": GROUP_ID, "name": f"заказ: {d.get('name')}"}).json()
    tid = str(res.get("result", {}).get("message_thread_id"))
    if tid:
        live_storage[tid] = []
        admin_url = f"{d.get('admin_link')}#tid={tid}"
        text = f"🌟 **Новый запрос**\n👤 {d.get('name')}\n📞 {d.get('contact')}\n💬 {d.get('message')}\n\n🔗 Ответить на сайте:\n{admin_url}"
        requests.post(f"{URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": tid, "text": text})
        return jsonify({"status": "ok", "tid": tid})
    return jsonify({"status": "error"}), 400

@app.route('/send_message', methods=['POST'])
def send_message():
    tid = str(request.form.get("tid"))
    msg = request.form.get("message")
    is_admin = request.form.get("is_admin") == 'true'
    if tid:
        if not is_admin: # В ТГ шлем только если пишет клиент
            requests.post(f"{URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": tid, "text": msg})
    return jsonify({"status": "ok"})

# ЭТА ЧАСТЬ ОТВЕЧАЕТ ЗА ПРИЕМ СООБЩЕНИЙ ИЗ ТГ
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if "message" in data and "message_thread_id" in data["message"]:
        tid = str(data["message"]["message_thread_id"])
        text = data["message"].get("text")
        if tid in live_storage and text:
            # Записываем ваш ответ из ТГ в память для сайта
            live_storage[tid].append({"text": text, "is_admin": True})
    return jsonify({"status": "ok"})

@app.route('/get_updates', methods=['GET'])
def get_updates():
    tid = str(request.args.get("tid"))
    msgs = live_storage.get(tid, [])
    live_storage[tid] = [] # Очищаем после выдачи
    return jsonify({"messages": msgs})
