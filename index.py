import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
GROUP_ID = "-1003265048579"
URL = f"https://api.telegram.org/bot{TOKEN}"

# Временное хранилище ответов для сайта
live_storage = {}

@app.route('/ai_chat', methods=['POST'])
def ai_chat():
    d = request.form
    name = d.get('name', 'Клиент')
    # Создаем новую тему в группе
    res = requests.post(f"{URL}/createForumTopic", data={"chat_id": GROUP_ID, "name": f"Заказ: {name}"}).json()
    tid = str(res.get("result", {}).get("message_thread_id"))
    
    if tid:
        live_storage[tid] = [] # Инициализируем очередь сообщений
        text = f"🌟 **Новый запрос**\n👤 Имя: {name}\n📞 Контакт: {d.get('contact')}\n💬 Сообщение: {d.get('message')}"
        requests.post(f"{URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": tid, "text": text, "parse_mode": "Markdown"})
        
        # Отправка файлов в ту же тему
        if 'files[]' in request.files:
            for f in request.files.getlist('files[]'):
                requests.post(f"{URL}/sendDocument", params={"chat_id": GROUP_ID, "message_thread_id": tid}, files={"document": (f.filename, f.read())})
        
        return jsonify({"status": "ok", "tid": tid})
    return jsonify({"status": "error"}), 400

@app.route('/send_message', methods=['POST'])
def send_from_site():
    tid = request.form.get("tid")
    msg = request.form.get("message")
    if tid and msg:
        requests.post(f"{URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": tid, "text": msg})
    return jsonify({"status": "ok"})

# WEBHOOK: Сюда Telegram шлет ваши ответы из группы
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if "message" in data and "message_thread_id" in data["message"]:
        tid = str(data["message"]["message_thread_id"])
        text = data["message"].get("text")
        # Сохраняем сообщение, только если оно не от бота
        if text and not data["message"].get("from", {}).get("is_bot"):
            if tid not in live_storage: live_storage[tid] = []
            live_storage[tid].append({"text": text, "is_admin": True})
    return jsonify({"status": "ok"})

# ПОЛЛИНГ: Сайт забирает ваши ответы отсюда
@app.route('/get_updates', methods=['GET'])
def get_updates():
    tid = request.args.get("tid")
    msgs = live_storage.get(tid, [])
    live_storage[tid] = [] # Очищаем после выдачи, чтобы не дублировать
    return jsonify({"messages": msgs})
