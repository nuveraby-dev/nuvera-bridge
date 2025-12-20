<script src="https://cdn.jsdelivr.net/npm/browser-image-compression@2.0.2/dist/browser-image-compression.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap" rel="stylesheet">

<style>
    :root { --brand: #d7ff2f; --dark: #000; --bg: #f5f5f5; }
    #nv-chat { position: fixed; bottom: 20px; right: 20px; z-index: 999999; font-family: 'Montserrat', sans-serif; }
    
    #chat-win { 
        position: absolute; bottom: 85px; right: 0; width: 340px; 
        background: #fff; border-radius: 24px; box-shadow: 0 15px 40px rgba(0,0,0,0.2); 
        display: none; flex-direction: column; overflow: hidden; 
        transform-origin: bottom right; transition: 0.3s;
    }
    #chat-win.active { display: flex; animation: appleScale 0.3s ease-out; }
    @keyframes appleScale { from { opacity: 0; transform: scale(0.8); } to { opacity: 1; transform: scale(1); } }

    .header { background: var(--dark); color: var(--brand); padding: 18px 22px; font-weight: 700; font-size: 13px; display: flex; justify-content: space-between; align-items: center; letter-spacing: 0.5px; }

    .body { padding: 20px; display: flex; flex-direction: column; gap: 12px; align-items: center; }
    
    #flow { width: 100%; height: 320px; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; padding: 5px; box-sizing: border-box; }
    
    .input { 
        width: 100%; padding: 14px; border-radius: 12px; border: none; 
        background: var(--bg); font-size: 14px; outline: none; box-sizing: border-box; 
        font-family: 'Montserrat'; text-align: center; 
    }
    
    .btn-main { width: 100%; background: var(--dark); color: var(--brand); border: none; padding: 16px; border-radius: 12px; font-weight: 700; cursor: pointer; }

    .msg { padding: 10px 14px; border-radius: 16px; font-size: 13px; max-width: 80%; word-wrap: break-word; }
    .msg.client { background: var(--bg); align-self: flex-end; border-bottom-right-radius: 2px; }
    .msg.admin { background: var(--brand); align-self: flex-start; border-bottom-left-radius: 2px; font-weight: 600; }

    /* Файлы */
    .f-area { display: flex; flex-wrap: wrap; gap: 6px; justify-content: center; width: 100%; }
    .f-chip { background: var(--dark); color: var(--brand); font-size: 9px; padding: 5px 10px; border-radius: 20px; display: flex; align-items: center; }
    .f-remove { cursor: pointer; color: #fff; font-weight: bold; margin-left: 5px; }

    /* Нижняя панель ввода */
    .bottom-bar { display: flex; width: 100%; gap: 10px; align-items: center; background: #fff; padding: 15px; border-top: 1px solid #eee; box-sizing: border-box; }

    #trigger { width: 65px; height: 65px; background: var(--brand); border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; box-shadow: 0 10px 25px rgba(0,0,0,0.2); }
</style>

<div id="nv-chat">
    <div id="chat-win">
        <div class="header">
            <span>NUVERA LIVE CHAT</span>
            <span onclick="toggleChat()" style="cursor:pointer; font-size:20px;">×</span>
        </div>
        
        <div class="body" id="s-form">
            <input type="text" id="n-in" class="input" placeholder="ваше имя">
            <input type="text" id="c-in" class="input" placeholder="телефон / telegram">
            <textarea id="m-in" class="input" style="height:80px; resize:none" placeholder="опишите задачу..."></textarea>
            
            <div id="f-list-1" class="f-area"></div>
            
            <label style="cursor:pointer; font-size:22px;" title="Прикрепить файлы">
                📎 <input type="file" id="fi-1" style="display:none" multiple onchange="handleFiles(this, 'f-list-1')">
            </label>
            
            <button id="btn-start" class="btn-main" onclick="startChat()">ОТПРАВИТЬ ЗАПРОС</button>
        </div>

        <div id="s-chat" style="display:none; flex-direction:column;">
            <div class="body"><div id="flow"></div></div>
            <div id="f-list-2" class="f-area" style="padding:0 15px;"></div>
            <div class="bottom-bar">
                <label style="cursor:pointer; font-size:20px;">
                    📎 <input type="file" id="fi-2" style="display:none" multiple onchange="handleFiles(this, 'f-list-2')">
                </label>
                <input type="text" id="rep-in" class="input" style="text-align:left;" placeholder="сообщение..." onkeypress="if(event.key==='Enter')sendMsg()">
                <button onclick="sendMsg()" style="background:none; border:none; font-size:20px; cursor:pointer;">➤</button>
            </div>
        </div>
    </div>

    <div id="trigger" onclick="toggleChat()">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2.5"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
    </div>
</div>

<script>
    const API = "https://nuvera-bridge.vercel.app";
    let tid = localStorage.getItem('nv_tid_v11');
    let fileQueue = [];

    function toggleChat() { document.getElementById('chat-win').classList.toggle('active'); }

    async function handleFiles(input, divId) {
        for (let f of input.files) {
            let proc = f;
            if (f.type.startsWith('image/')) proc = await imageCompression(f, { maxSizeMB: 1 });
            const id = Math.random().toString(36).substr(2, 9);
            fileQueue.push({ id, file: proc, name: f.name, divId });
        }
        renderChips();
        input.value = "";
    }

    function removeFile(id) {
        fileQueue = fileQueue.filter(f => f.id !== id);
        renderChips();
    }

    function renderChips() {
        ['f-list-1', 'f-list-2'].forEach(id => {
            const el = document.getElementById(id); if(!el) return; el.innerHTML = "";
            fileQueue.filter(f => f.divId === id).forEach(f => {
                const s = document.createElement('div');
                s.className = 'f-chip';
                s.innerHTML = `<span>${f.name.substring(0,10)}</span><span class="f-remove" onclick="removeFile('${f.id}')">×</span>`;
                el.appendChild(s);
            });
        });
    }

    function renderMsg(txt, isAdm) {
        const f = document.getElementById('flow');
        const m = document.createElement('div');
        m.className = isAdm ? 'msg admin' : 'msg client';
        m.innerText = txt;
        f.appendChild(m); f.scrollTop = f.scrollHeight;
    }

    async function poll() {
        if (tid) {
            try {
                const r = await fetch(`${API}/get_updates?tid=${tid}`);
                const d = await r.json();
                if (d.messages) d.messages.forEach(m => renderMsg(m.text, true));
            } catch(e) {}
        }
        setTimeout(poll, 3000);
    }

    async function startChat() {
        const n = document.getElementById('n-in').value, c = document.getElementById('c-in').value, m = document.getElementById('m-in').value;
        if(!n || !c) return alert("Заполните имя и телефон");
        const fd = new FormData();
        fd.append('name', n); fd.append('contact', c); fd.append('message', m);
        fileQueue.forEach(f => { if(f.divId === 'f-list-1') fd.append('files[]', f.file, f.name); });
        const r = await fetch(`${API}/ai_chat`, { method: 'POST', body: fd });
        const d = await r.json();
        if(d.tid) {
            tid = d.tid; localStorage.setItem('nv_tid_v11', tid);
            document.getElementById('s-form').style.display = 'none';
            document.getElementById('s-chat').style.display = 'flex';
            renderMsg(m || "Заявка отправлена", false);
            fileQueue = []; renderChips();
        }
    }

    async function sendMsg() {
        const i = document.getElementById('rep-in'); if(!i.value && fileQueue.length === 0) return;
        const txt = i.value;
        const fd = new FormData(); fd.append('tid', tid); fd.append('message', txt);
        fileQueue.forEach(f => { if(f.divId === 'f-list-2') fd.append('files[]', f.file, f.name); });
        renderMsg(txt || "📎 Файлы отправлены", false);
        i.value = ""; fileQueue = []; renderChips();
        await fetch(`${API}/send_message`, { method: 'POST', body: fd });
    }

    window.onload = () => {
        if(tid) { document.getElementById('s-form').style.display = 'none'; document.getElementById('s-chat').style.display = 'flex'; }
        poll();
    };
</script>
