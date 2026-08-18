import os
from http.server import HTTPServer, BaseHTTPRequestHandler

# ============================================
# 📄 صفحة HTML - رسالة إيقاف الموقع
# ============================================
HTML_PAGE = """<!DOCTYPE html>
<html lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚫 الموقع متوقف</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            min-height: 100vh;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
            direction: rtl;
        }

        .container {
            max-width: 550px;
            width: 100%;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 30px;
            padding: 45px 35px;
            text-align: center;
            box-shadow: 0 30px 80px rgba(0, 0, 0, 0.6);
            animation: fadeIn 0.8s ease-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .icon {
            font-size: 70px;
            margin-bottom: 15px;
            display: block;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }

        h1 {
            color: #ff6b6b;
            font-size: 28px;
            font-weight: 800;
            margin-bottom: 12px;
            letter-spacing: 1px;
        }

        .subtitle {
            color: #ffd93d;
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 20px;
            background: rgba(255, 217, 61, 0.1);
            padding: 8px 20px;
            border-radius: 50px;
            display: inline-block;
        }

        .divider {
            height: 2px;
            background: linear-gradient(90deg, transparent, rgba(255, 107, 107, 0.5), transparent);
            margin: 20px 0 25px 0;
        }

        .message-box {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 25px;
            border-right: 4px solid #ff6b6b;
            text-align: right;
        }

        .message-box p {
            color: #e0e0e0;
            font-size: 15px;
            line-height: 1.8;
            margin-bottom: 10px;
        }

        .message-box p:last-child {
            margin-bottom: 0;
        }

        .message-box .highlight {
            color: #ff6b6b;
            font-weight: 700;
        }

        .warning-badge {
            display: inline-block;
            background: rgba(255, 107, 107, 0.15);
            color: #ff6b6b;
            padding: 6px 16px;
            border-radius: 50px;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 15px;
            border: 1px solid rgba(255, 107, 107, 0.3);
        }

        .btn-exit {
            background: linear-gradient(135deg, #ff6b6b, #ee5a24);
            color: #fff;
            border: none;
            padding: 16px 40px;
            border-radius: 16px;
            font-size: 18px;
            font-weight: 700;
            cursor: pointer;
            width: 100%;
            transition: all 0.3s ease;
            box-shadow: 0 10px 30px rgba(255, 107, 107, 0.3);
            letter-spacing: 1px;
        }

        .btn-exit:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 15px 40px rgba(255, 107, 107, 0.5);
        }

        .btn-exit:active {
            transform: scale(0.97);
        }

        .footer {
            margin-top: 20px;
            font-size: 12px;
            color: rgba(255, 255, 255, 0.3);
            letter-spacing: 0.5px;
        }

        .footer span {
            color: rgba(255, 107, 107, 0.5);
        }

        /* توهج خلفي */
        .glow {
            position: fixed;
            width: 300px;
            height: 300px;
            background: radial-gradient(circle, rgba(255, 107, 107, 0.1), transparent 70%);
            border-radius: 50%;
            top: -100px;
            right: -100px;
            z-index: -1;
        }

        .glow2 {
            position: fixed;
            width: 400px;
            height: 400px;
            background: radial-gradient(circle, rgba(255, 217, 61, 0.05), transparent 70%);
            border-radius: 50%;
            bottom: -150px;
            left: -150px;
            z-index: -1;
        }
    </style>
</head>
<body>

    <!-- توهجات خلفية -->
    <div class="glow"></div>
    <div class="glow2"></div>

    <div class="container">
        <span class="icon">🚫</span>
        <h1>تم إيقاف الموقع</h1>
        <div class="subtitle">⛔ لأسباب أمنية</div>

        <div class="divider"></div>

        <div class="warning-badge">🔒 إشعار أمني</div>

        <div class="message-box">
            <p>
                <span class="highlight">•</span> تم <span class="highlight">إيقاف</span> هذا الموقع بشكل <span class="highlight">فوري</span> 
                بسبب نشاط مشبوه.
            </p>
            <p>
                <span class="highlight">•</span> هذا الموقع لأغراض <span class="highlight">تعليمية</span> فقط، 
                ولا نتحمل أي <span class="highlight">مسؤولية</span> عن أي استخدام آخر.
            </p>
            <p>
                <span class="highlight">•</span> للاستفسارات، يرجى التواصل مع إدارة الموقع.
            </p>
        </div>

        <button class="btn-exit" onclick="exitPage()">
            🚪 الخروج الآن
        </button>

        <div class="footer">
            <span>⚠️</span> هذا الموقع غير متاح حالياً <span>⚠️</span>
        </div>
    </div>

    <script>
        function exitPage() {
            // محاولة إغلاق الصفحة بعدة طرق
            window.close();
            
            // محاولة توجيه إلى صفحة فارغة
            document.body.innerHTML = '';
            window.location.href = 'about:blank';
            
            // محاولة إعادة التوجيه لصفحة لا شيء
            setTimeout(function() {
                window.location.href = 'data:text/html,<h1>تم الخروج</h1>';
            }, 100);
        }

        // منع النقر بزر اليمين
        document.addEventListener('contextmenu', function(e) {
            e.preventDefault();
        });

        // منع F12 و Ctrl+Shift+I و Ctrl+U
        document.addEventListener('keydown', function(e) {
            if (e.key === 'F12' || 
                (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'J')) ||
                (e.ctrlKey && e.key === 'U')) {
                e.preventDefault();
                return false;
            }
        });
    </script>

</body>
</html>"""

# ============================================
# 🚀 خادم معدل لـ Render
# ============================================
class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.end_headers()
        self.wfile.write(HTML_PAGE.encode('utf-8'))
    
    def log_message(self, format, *args):
        pass

def start():
    port = int(os.environ.get('PORT', 8085))
    server = HTTPServer(('0.0.0.0', port), MyHandler)
    
    print('\n' + '='*60)
    print('🚫 الموقع متوقف لأسباب أمنية')
    print('📌 يعرض رسالة احترافية مع زر خروج')
    print('🛑 Press Ctrl+C to stop')
    print('='*60 + '\n')
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n🛑 Server stopped')
        server.shutdown()

if __name__ == '__main__':
    start()
