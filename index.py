<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
    :root { --brand: #d7ff2f; }
    #nuvera-chat-wrapper { position: fixed; bottom: 20px; right: 20px; z-index: 999999; font-family: 'Montserrat', sans-serif; }
    #chat-window { position: absolute; bottom: 75px; right: 0; width: 330px; background: #fff; border-radius: 24px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); display: flex; flex-direction: column; overflow: hidden; opacity: 0; pointer-events: none; transform: scale(0.7); transform-origin: bottom right; transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
    #chat-window.active { opacity: 1; pointer-events: auto; transform: scale(1); }
    #chat-trigger { width: 60px; height: 60px; background: var(--brand); border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
    .header { background: #000; color: var(--brand); padding: 15px 20px; font-weight: 800; display: flex; justify-content: space-between; align-items: center; font-size: 12px; letter-spacing: 1px; }
    #chat-form-el, #chat-container { padding: 15px; display: flex; flex-direction: column; gap: 8px; }
    #chat-container { display: none; height: 400px; }
    .input-field { width: 100%; padding: 12px; border-radius: 10px; border: none; background: #f5f5f5; font-size: 13px; outline: none; box-sizing: border-box; font-family: 'Montserrat'; }
    .btn-main { background: #000; color: var(--brand); border: none; padding: 14px; border-radius: 12px; font-weight: 800; cursor: pointer; text-transform: uppercase; font-size: 11px; }
    .msg-list { flex-grow: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 6px; }
    .m-item { padding: 10px 14px; border-radius: 15px; font-size: 13px; max-width: 85%; line-height: 1.4; }
    .m-user { align-self: flex-end; background: #eee; border-bottom-right-radius: 2px; }
    .m-admin { align-self: flex-start; background: var(--brand); font-weight: 600; border-bottom-left-radius: 2px; }
    .input-bar { display: flex; align-items: center; gap: 8px; background: #f5f5f5; padding: 8px 12px; border-radius: 20px; }
    .input-bar input { flex-grow: 1; border: none; background: transparent; outline: none; font-size: 13px; }
    #f-q { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 4px; }
    .q-tag { background: #000; color: var(--brand); font-size: 9px; padding: 3px 7px; border-radius: 5px; }
</style>

<div id="nuvera-chat-wrapper">
    <audio id="msg-sound" src="https://assets.mixkit.co/active_storage/sfx/1344/1344-preview.mp3"></audio>
    <div id="chat-window">
        <div class="header"><div>NUVERA LIVE CHAT</div><div style="cursor:pointer; font-size:20px" onclick="toggleChat()">×</div></div>
        <form id="chat-form-el" onsubmit="event.preventDefault(); start();">
            <input type="text" id="u-n" class="input-field" placeholder="Ваше имя" required>
            <input type="text" id="u-c" class="input-field" placeholder="Телефон / TG" required>
            <textarea id="u-m" class="input-field" style="height:70px; resize:none;" placeholder="Ваш вопрос..."></textarea>
            <div id="f-q"></div>
            <label class="btn-main" style="background:#eee; color:#333; text-align:center; font-size:9px; cursor:pointer;">
                + ПРИКРЕПИТЬ ФАЙЛЫ
                <input type="file" id="f-i" style="display:none" multiple onchange="addF(this)">
            </label>
            <button type="submit" class="btn-main">ОТПРАВИТЬ</button>
        </form>
        <div id="chat-container">
            <div id="m-list" class="msg-list"></div>
            <div class="input-bar">
                <label for="f-chat" style="cursor:pointer;"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path></svg></label>
                <input type="file" id="f-chat" style="display:none" multiple onchange="sendF(this)">
                <input type="text" id="c-i" placeholder="Напишите..." onkeydown="if(event.key==='Enter') sendT()">
                <button onclick="sendT()" style="background:none; border:none; cursor:pointer;"><svg width="18" viewBox="0 0 24 24" fill="#000"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg></button>
            </div>
        </div>
    </div>
    <div id="chat-trigger" onclick="toggleChat()"><svg viewBox="0 0 24 24" fill="#000" width="26"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/></svg></div>
</div>

<script>
    const API = "https://nuvera-bridge.vercel.app/api";
    let queue = [];
    const urlId = new URLSearchParams(window.location.search).get('id');
    if(urlId) localStorage.setItem('nv_cid', urlId);
    let cid = localStorage.getItem('nv_cid') || "nv_" + Math.random().toString(36).substr(2,9);
    localStorage.setItem('nv_cid', cid);

    window.onload = () => {
        if(urlId) {
            document.getElementById('chat-form-el').style.display='none';
            document.getElementById('chat-container').style.display='flex';
            toggleChat(); poll();
        } else {
            setTimeout(() => { if(!document.getElementById('chat-window').classList.contains('active')) toggleChat(); }, 2000);
        }
    }

    function toggleChat() { document.getElementById('chat-window').classList.toggle('active'); }

    function addF(input) {
        const zone = document.getElementById('f-q');
        for(let f of input.files) {
            queue.push(f);
            let s = document.createElement('span'); s.className='q-tag'; s.innerText=f.name; zone.appendChild(s);
        }
        input.value="";
    }

    async function start() {
        const fd = new FormData();
        fd.append('chat_id', cid);
        fd.append('name', document.getElementById('u-n').value);
        fd.append('contact', document.getElementById('u-c').value);
        fd.append('message', document.getElementById('u-m').value);
        fd.append('admin_link', window.location.origin + window.location.pathname);
        queue.forEach(f => { fd.append('files[]', f); ui(f.name, 'user', true); });
        if(document.getElementById('u-m').value) ui(document.getElementById('u-m').value, 'user');
        
        document.getElementById('chat-form-el').style.display='none';
        document.getElementById('chat-container').style.display='flex';
        fetch(`${API}/ai_chat`, {method:'POST', body:fd}).then(r => { if(!r.ok) console.error('Ошибка 404: Проверьте деплой Vercel'); });
        queue = []; poll();
    }

    async function sendF(input) {
        const fd = new FormData(); fd.append('chat_id', cid);
        for(let f of input.files) { fd.append('files[]', f); ui(f.name, 'user', true); }
        fetch(`${API}/send_message`, {method:'POST', body:fd});
        input.value="";
    }

    function sendT() {
        const i = document.getElementById('c-i'); if(!i.value) return;
        ui(i.value, 'user');
        const fd = new FormData(); fd.append('chat_id', cid); fd.append('message', i.value);
        fetch(`${API}/send_message`, {method:'POST', body:fd});
        i.value="";
    }

    function ui(t, s, isF=false) {
        const l = document.getElementById('m-list');
        const d = document.createElement('div'); d.className = `m-item m-${s}`;
        d.innerHTML = isF ? `DOC: ${t}` : t;
        l.appendChild(d); l.scrollTop = l.scrollHeight;
    }

    function poll() {
        setInterval(async () => {
            try {
                const r = await fetch(`${API}/get_messages?chat_id=${cid}`);
                if(r.ok) {
                    const d = await r.json();
                    if(d.new_messages) d.new_messages.forEach(m => { 
                        const isF = m.text.startsWith("DOC: ");
                        ui(isF ? m.text.replace("DOC: ","") : m.text, m.is_admin?'admin':'user', isF);
                        if(m.is_admin) document.getElementById('msg-sound').play().catch(()=>{});
                    });
                }
            } catch(e){}
        }, 3000);
    }
</script>
