import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
GROUP_ID = "-1003265048579"
URL = f"https://api.telegram.org/bot{TOKEN}"

updates_store = {} # Временное хранилище для синхронизации

def send_files(tid, files):
    """Универсальная отправка файлов как документов"""
    for f in files:
        if f.filename:
            requests.post(f"{URL}/sendDocument", 
                          params={"chat_id": GROUP_ID, "message_thread_id": tid}, 
                          files={"document": (f.filename, f.read())})

@app.route('/ai_chat', methods=['POST'])
def ai_chat():
    d = request.form
    res = requests.post(f"{URL}/createForumTopic", data={"chat_id": GROUP_ID, "name": f"заказ: {d.get('name')}"}).json()
    tid = str(res.get("result", {}).get("message_thread_id"))
    
    if tid:
        updates_store[tid] = []
        text = f"🌟 **Новый запрос**\n👤 {d.get('name')}\n📞 {d.get('contact')}\n💬 {d.get('message')}\n\n🔗 Чат: {d.get('admin_link')}#tid={tid}"
        requests.post(f"{URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": tid, "text": text})
        
        if 'files[]' in request.files:
            send_files(tid, request.files.getlist('files[]'))
        
        return jsonify({"status": "ok", "tid": tid})
    return jsonify({"status": "error"}), 400

@app.route('/send_message', methods=['POST'])
def send_message():
    tid = str(request.form.get("tid"))
    msg = request.form.get("message")
    is_admin = request.form.get("is_admin") == 'true'
    
    if tid in updates_store:
        updates_store[tid].append({"text": msg, "is_admin": is_admin})
        if not is_admin and msg:
            requests.post(f"{URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": tid, "text": msg})
        if 'files[]' in request.files:
            send_files(tid, request.files.getlist('files[]'))
            
    return jsonify({"status": "ok"})

@app.route('/get_updates', methods=['GET'])
def get_updates():
    tid = str(request.args.get("tid"))
    msgs = updates_store.get(tid, [])
    updates_store[tid] = [] # Очистка после получения
    return jsonify({"messages": msgs})
