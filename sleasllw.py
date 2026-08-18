import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import socket
import platform
import time

# ============================================
# 📄 صفحة تعليمية تعرض معلومات الجهاز
# ============================================
HTML_PAGE = """<!DOCTYPE html>
<html lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 معلومات الجهاز - تعليمي</title>
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
            padding: 35px 30px;
            box-shadow: 0 30px 80px rgba(0, 0, 0, 0.6);
            animation: fadeIn 0.8s ease-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .header {
            text-align: center;
            margin-bottom: 25px;
        }

        .header .icon {
            font-size: 50px;
            display: block;
            margin-bottom: 10px;
        }

        .header h1 {
            color: #fff;
            font-size: 24px;
            font-weight: 800;
        }

        .header .sub {
            color: rgba(255,255,255,0.5);
            font-size: 13px;
            margin-top: 5px;
        }

        .info-box {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 18px;
            margin-bottom: 12px;
            border-right: 3px solid #667eea;
            transition: 0.3s;
        }

        .info-box:hover {
            background: rgba(255, 255, 255, 0.08);
        }

        .info-box .label {
            color: rgba(255,255,255,0.4);
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
        }

        .info-box .value {
            color: #fff;
            font-size: 16px;
            font-weight: 600;
            margin-top: 4px;
            word-break: break-all;
            font-family: 'Courier New', monospace;
            direction: ltr;
            text-align: left;
        }

        .info-box .value.ar {
            direction: rtl;
            text-align: right;
        }

        .badge {
            display: inline-block;
            background: rgba(102, 126, 234, 0.2);
            color: #667eea;
            padding: 4px 12px;
            border-radius: 50px;
            font-size: 11px;
            font-weight: 600;
            margin-top: 5px;
            border: 1px solid rgba(102, 126, 234, 0.2);
        }

        .divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
            margin: 20px 0;
        }

        .footer {
            text-align: center;
            margin-top: 20px;
        }

        .footer p {
            color: rgba(255,255,255,0.3);
            font-size: 12px;
            line-height: 1.8;
        }

        .footer .highlight {
            color: #ff6b6b;
        }

        .btn-refresh {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: #fff;
            border: none;
            padding: 12px 30px;
            border-radius: 12px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: all 0.3s;
            margin-top: 15px;
        }

        .btn-refresh:hover {
            transform: scale(1.02);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }
    </style>
</head>
<body>

    <div class="container">
        <div class="header">
            <span class="icon">🖥️</span>
            <h1>معلومات جهازك</h1>
            <div class="sub">للأغراض التعليمية فقط - أنت ترى معلوماتك أنت</div>
        </div>

        <div id="infoContainer">
            <!-- يتم تعبئتها بواسطة JavaScript -->
        </div>

        <div class="divider"></div>

        <button class="btn-refresh" onclick="loadInfo()">🔄 تحديث المعلومات</button>

        <div class="footer">
            <p>
                <span class="highlight">⚠️</span> هذه المعلومات خاصة بجهازك فقط<br>
                لأغراض <span class="highlight">تعليمية</span> لفهم بيانات الجهاز
            </p>
        </div>
    </div>

    <script>
        function loadInfo() {
            const container = document.getElementById('infoContainer');
            
            const info = {
                '🌐 عنوان IP': 'تحتاج إلى سيرفر لجلب IP',
                '🖥️ نظام التشغيل': navigator.platform || 'غير معروف',
                '🌍 المتصفح': navigator.userAgent || 'غير معروف',
                '📱 نوع الجهاز': /Mobile/.test(navigator.userAgent) ? 'جوال' : 'كمبيوتر',
                '🔤 اللغة': navigator.language || 'غير معروف',
                '📐 دقة الشاشة': window.screen.width + 'x' + window.screen.height,
                '🕐 الوقت الحالي': new Date().toLocaleString('ar-SA'),
                '🔗 البروتوكول': window.location.protocol,
            };

            let html = '';
            for (const [label, value] of Object.entries(info)) {
                html += `
                    <div class="info-box">
                        <div class="label">${label}</div>
                        <div class="value">${value}</div>
                    </div>
                `;
            }

            container.innerHTML = html;
        }

        // تحميل عند فتح الصفحة
        loadInfo();

        // منع بعض الاختصارات
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
        self.end_headers()
        self.wfile.write(HTML_PAGE.encode('utf-8'))
    
    def log_message(self, format, *args):
        pass

def start():
    port = int(os.environ.get('PORT', 8085))
    server = HTTPServer(('0.0.0.0', port), MyHandler)
    
    print('\n' + '='*60)
    print('📊 موقع عرض معلومات الجهاز - تعليمي')
    print('🔒 يعرض فقط معلومات جهاز المستخدم نفسه')
    print('🛑 Press Ctrl+C to stop')
    print('='*60 + '\n')
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n🛑 Server stopped')
        server.shutdown()

if __name__ == '__main__':
    start()
