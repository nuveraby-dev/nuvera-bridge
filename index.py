import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TOKEN = "8514796589:AAEJqdm3DsCtki-gneHQTLEEIUZKqyiz_tg"
GROUP_ID = "-1003265048579"
URL = f"https://api.telegram.org/bot{TOKEN}"

def upload_to_tg(tid, files):
    """Отправка любых файлов как документов (сохранение качества)"""
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
        tid = res.get("result", {}).get("message_thread_id")
        
        if tid:
            # Ссылка через хэш (#) для мгновенного срабатывания в Tilda
            base_url = d.get('admin_link').split('?')[0].split('#')[0].rstrip('/')
            admin_url = f"{base_url}/#tid={tid}"
            
            text = (
                f"🌟 **nuvera live: новый запрос**\n\n"
                f"👤 **клиент:** {name}\n"
                f"📞 **связь:** {d.get('contact')}\n"
                f"💬 **сообщение:** {d.get('message')}\n\n"
                f"📥 **ответить клиенту по ссылке:**\n{admin_url}"
            )
            
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
    is_admin = request.form.get("is_admin") # Флаг от Tilda
    
    if tid:
        # Если пишет клиент (не админ), отправляем в Telegram
        if msg and not is_admin:
            requests.post(f"{URL}/sendMessage", data={"chat_id": GROUP_ID, "message_thread_id": tid, "text": msg})
        
        if 'files[]' in request.files:
            upload_to_tg(tid, request.files.getlist('files[]'))
            
    return jsonify({"status": "ok"})
