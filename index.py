import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
GROUP_ID = "-1003265048579"
URL = f"https://api.telegram.org/bot{TOKEN}"

# Временное хранилище для пересылки ответов из TG на сайт
# В идеале тут нужна БД, но для начала используем словарь в памяти
history = {} 

def upload_to_tg(tid, files):
    for f in files:
        if f.filename:
            requests.post(f"{URL}/sendDocument", 
                          params={"chat_id": GROUP_ID, "message_thread_id": tid}, 
                          files={"document": (f.filename, f.read())})

@app.route('/ai_chat', methods=['POST'])
def ai_chat():
    try:
        d = request.form
        name = d.get('name', 'клиент')
        res = requests.post(f"{URL}/createForumTopic", data={"chat_id": GROUP_ID, "name": f"заказ: {name}"}).json()
        tid = str(res.get("result", {}).get("message_thread_id"))
        
        if tid:
            history[tid] = [] # Инициализируем историю для этого чата
            base_url = d.get('admin_link').split('?')[0].split('#')[0].rstrip('/')
            admin_url = f"{base_url}/#tid={tid}"
            
            text = f"🌟 **Новый чат: {name}**\n📞 {d.get('contact')}\n💬 {d.get('message')}\n\n🔗 {admin_url}"
            requests.post(f"{URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": tid, "text": text, "parse_mode": "Markdown"})
            
            if 'files[]' in request.files:
                upload_to_tg(tid, request.files.getlist('files[]'))
            
            return jsonify({"status": "ok", "tid": tid})
    except Exception as e:
        return jsonify({"status": "error", "m": str(e)}), 500
    return jsonify({"status": "error"}), 400

@app.route('/send_message', methods=['POST'])
def send_message():
    tid = request.form.get("tid")
    msg = request.form.get("message")
    is_admin = request.form.get("is_admin")
    
    if tid:
        if msg and not is_admin:
            requests.post(f"{URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": tid, "text": msg})
        if 'files[]' in request.files:
            upload_to_tg(tid, request.files.getlist('files[]'))
    return jsonify({"status": "ok"})

# НОВЫЙ МАРШРУТ: Сайт запрашивает новые сообщения от админа
@app.route('/get_messages', methods=['GET'])
def get_messages():
    tid = request.args.get("tid")
    # Здесь логика получения обновлений через getUpdates от Telegram
    # Для упрощения: Telegram Webhook должен записывать сюда сообщения
    # Пока возвращаем пустой список, чтобы не вешать сайт, 
    # но технология подразумевает чтение ответов бота.
    return jsonify({"messages": []})
