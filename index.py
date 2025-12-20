import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
GROUP_ID = "-1003265048579"
URL = f"https://api.telegram.org/bot{TOKEN}"

# Хранилище сообщений для синхронизации
memory_db = {}

def upload_to_tg(tid, files):
    for f in files:
        if f.filename:
            requests.post(f"{URL}/sendDocument", 
                          params={"chat_id": GROUP_ID, "message_thread_id": tid}, 
                          files={"document": (f.filename, f.read())})

@app.route('/ai_chat', methods=['POST'])
def ai_chat():
    d = request.form
    name = d.get('name', 'клиент')
    res = requests.post(f"{URL}/createForumTopic", data={"chat_id": GROUP_ID, "name": f"заказ: {name}"}).json()
    tid = str(res.get("result", {}).get("message_thread_id"))
    
    if tid:
        memory_db[tid] = [] # Создаем историю чата
        base_url = d.get('admin_link').split('?')[0].split('#')[0].rstrip('/')
        admin_url = f"{base_url}/#tid={tid}"
        
        msg = f"🌟 **Новый заказ: {name}**\n📞 {d.get('contact')}\n💬 {d.get('message')}\n\n🔗 Чат на сайте: {admin_url}"
        requests.post(f"{URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": tid, "text": msg, "parse_mode": "Markdown"})
        
        if 'files[]' in request.files:
            upload_to_tg(tid, request.files.getlist('files[]'))
        
        return jsonify({"status": "ok", "tid": tid})
    return jsonify({"status": "error"}), 400

@app.route('/send_message', methods=['POST'])
def send_message():
    tid = str(request.form.get("tid"))
    msg = request.form.get("message")
    is_admin = request.form.get("is_admin") == 'true'
    
    if tid and tid in memory_db:
        # Сохраняем в историю, чтобы другой участник увидел
        memory_db[tid].append({"text": msg, "is_admin": is_admin})
        
        # Если пишет клиент, дублируем в Telegram
        if not is_admin:
            requests.post(f"{URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": tid, "text": msg})
        
        if 'files[]' in request.files:
            upload_to_tg(tid, request.files.getlist('files[]'))
            
    return jsonify({"status": "ok"})

# НОВЫЙ МАРШРУТ: Синхронизация истории
@app.route('/get_updates', methods=['GET'])
def get_updates():
    tid = str(request.args.get("tid"))
    updates = memory_db.get(tid, [])
    # Очищаем очередь после выдачи, чтобы сообщения не дублировались
    memory_db[tid] = [] 
    return jsonify({"messages": updates})
