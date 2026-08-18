#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Network Scanner & SNI Analyzer - Web Version
للعمل على Render
"""

from flask import Flask, render_template_string, request, jsonify
import socket
import ssl
import dns.resolver
import requests
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

app = Flask(__name__)

# ============================================
# القوالب HTML
# ============================================

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Network Scanner & SNI Analyzer</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f0f1a; color: #e0e0e0; padding: 20px; }
        .container { max-width: 1400px; margin: 0 auto; }
        .header { text-align: center; padding: 30px 0; border-bottom: 2px solid #2a2a4a; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; background: linear-gradient(135deg, #00d4ff, #7b2ffc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .header p { color: #888; margin-top: 10px; }
        .card { background: #1a1a2e; border-radius: 15px; padding: 25px; margin-bottom: 25px; border: 1px solid #2a2a4a; }
        .card h2 { color: #00d4ff; margin-bottom: 15px; font-size: 1.3em; }
        .input-group { display: flex; gap: 10px; flex-wrap: wrap; }
        .input-group input { flex: 1; padding: 12px 20px; border-radius: 10px; border: 1px solid #2a2a4a; background: #0f0f1a; color: #fff; font-size: 16px; min-width: 200px; }
        .input-group input:focus { border-color: #00d4ff; outline: none; }
        .btn { padding: 12px 30px; border: none; border-radius: 10px; font-size: 16px; cursor: pointer; transition: all 0.3s; font-weight: bold; }
        .btn-primary { background: linear-gradient(135deg, #00d4ff, #7b2ffc); color: #fff; }
        .btn-primary:hover { transform: scale(1.05); box-shadow: 0 0 20px rgba(0, 212, 255, 0.3); }
        .btn-secondary { background: #2a2a4a; color: #fff; }
        .btn-secondary:hover { background: #3a3a5a; }
        .results-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        @media (max-width: 768px) { .results-grid { grid-template-columns: 1fr; } }
        .stat-box { background: #0f0f1a; padding: 15px; border-radius: 10px; border: 1px solid #2a2a4a; text-align: center; }
        .stat-box .number { font-size: 2em; color: #00d4ff; }
        .stat-box .label { color: #888; font-size: 0.9em; }
        .port-open { color: #00ff88; }
        .sni-item { background: #0f0f1a; padding: 8px 15px; border-radius: 8px; margin: 5px 0; border-left: 3px solid #7b2ffc; }
        .sni-item .type { color: #888; font-size: 0.8em; }
        .subdomain-item { background: #0f0f1a; padding: 5px 15px; border-radius: 5px; margin: 3px 0; font-size: 0.9em; color: #aaa; }
        .loading { display: none; text-align: center; padding: 40px; }
        .loading .spinner { width: 50px; height: 50px; border: 4px solid #2a2a4a; border-top: 4px solid #00d4ff; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .tabs { display: flex; gap: 5px; margin-bottom: 20px; flex-wrap: wrap; }
        .tab { padding: 10px 20px; background: #0f0f1a; border: 1px solid #2a2a4a; border-radius: 8px 8px 0 0; cursor: pointer; }
        .tab.active { background: #1a1a2e; border-bottom: 2px solid #00d4ff; color: #00d4ff; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .json-view { background: #0f0f1a; padding: 15px; border-radius: 10px; overflow-x: auto; white-space: pre-wrap; font-family: monospace; font-size: 0.85em; }
        .footer { text-align: center; padding: 20px; color: #555; font-size: 0.8em; border-top: 1px solid #2a2a4a; margin-top: 30px; }
        .quick-buttons { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px; }
        .quick-btn { padding: 5px 15px; background: #0f0f1a; border: 1px solid #2a2a4a; border-radius: 20px; color: #aaa; cursor: pointer; font-size: 0.85em; transition: all 0.2s; }
        .quick-btn:hover { border-color: #00d4ff; color: #00d4ff; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌐 Network Scanner & SNI Analyzer</h1>
            <p>مسح المنافذ المفتوحة، اكتشاف النطاقات الفرعية، وتحليل SNI لشبكات الاتصالات</p>
        </div>

        <div class="card">
            <h2>🎯 إدخال الهدف</h2>
            <div class="input-group">
                <input type="text" id="targetInput" placeholder="أدخل نطاق (مثل stc.com.sa) أو IP" value="stc.com.sa">
                <button class="btn btn-primary" onclick="startScan()">🚀 فحص</button>
                <button class="btn btn-secondary" onclick="clearResults()">🗑️ مسح</button>
            </div>
            <div class="quick-buttons">
                <span class="quick-btn" onclick="quickScan('stc.com.sa')">stc.com.sa</span>
                <span class="quick-btn" onclick="quickScan('mobily.com.sa')">mobily.com.sa</span>
                <span class="quick-btn" onclick="quickScan('zain.com.sa')">zain.com.sa</span>
                <span class="quick-btn" onclick="quickScan('botgateway.stc.com.sa')">botgateway.stc.com.sa</span>
                <span class="quick-btn" onclick="quickScan('cloud.stc.com.sa')">cloud.stc.com.sa</span>
            </div>
        </div>

        <div id="loading" class="loading">
            <div class="spinner"></div>
            <p style="margin-top: 20px; color: #888;">جاري الفحص... قد يستغرق بعض الوقت</p>
        </div>

        <div id="results" style="display: none;">
            <div class="tabs" id="tabs">
                <div class="tab active" onclick="switchTab('summary')">📊 ملخص</div>
                <div class="tab" onclick="switchTab('ports')">🔓 المنافذ</div>
                <div class="tab" onclick="switchTab('subdomains')">🌐 النطاقات الفرعية</div>
                <div class="tab" onclick="switchTab('sni')">💡 توصيات SNI</div>
                <div class="tab" onclick="switchTab('ssl')">🔐 SSL</div>
                <div class="tab" onclick="switchTab('json')">📄 JSON</div>
            </div>

            <div id="tab-summary" class="tab-content active"></div>
            <div id="tab-ports" class="tab-content"></div>
            <div id="tab-subdomains" class="tab-content"></div>
            <div id="tab-sni" class="tab-content"></div>
            <div id="tab-ssl" class="tab-content"></div>
            <div id="tab-json" class="tab-content"></div>
        </div>

        <div class="footer">
            🔒 للأغراض التعليمية والبحثية فقط
        </div>
    </div>

    <script>
        let scanResults = null;

        function quickScan(target) {
            document.getElementById('targetInput').value = target;
            startScan();
        }

        function startScan() {
            const target = document.getElementById('targetInput').value.trim();
            if (!target) {
                alert('الرجاء إدخال نطاق أو IP');
                return;
            }

            document.getElementById('loading').style.display = 'block';
            document.getElementById('results').style.display = 'none';

            fetch('/scan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ target: target })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('loading').style.display = 'none';
                if (data.error) {
                    alert('❌ ' + data.error);
                    return;
                }
                scanResults = data;
                displayResults(data);
                document.getElementById('results').style.display = 'block';
            })
            .catch(error => {
                document.getElementById('loading').style.display = 'none';
                alert('❌ حدث خطأ: ' + error);
            });
        }

        function displayResults(data) {
            // Summary
            const summary = document.getElementById('tab-summary');
            summary.innerHTML = `
                <div class="results-grid">
                    <div class="stat-box"><div class="number">${data.main_ip || 'N/A'}</div><div class="label">IP الرئيسي</div></div>
                    <div class="stat-box"><div class="number">${data.subdomains_count || 0}</div><div class="label">النطاقات الفرعية</div></div>
                    <div class="stat-box"><div class="number">${data.open_ports_count || 0}</div><div class="label">المنافذ المفتوحة</div></div>
                    <div class="stat-box"><div class="number">${data.sni_count || 0}</div><div class="label">توصيات SNI</div></div>
                </div>
                <div style="margin-top: 20px; padding: 15px; background: #0f0f1a; border-radius: 10px;">
                    <p><strong>🎯 النطاق:</strong> ${data.target}</p>
                    <p><strong>📌 الوقت:</strong> ${data.scan_time || 'N/A'}</p>
                    <p><strong>🏢 المزود:</strong> ${data.org || 'غير معروف'}</p>
                    <p><strong>📍 الموقع:</strong> ${data.location || 'غير معروف'}</p>
                </div>
            `;

            // Ports
            const ports = document.getElementById('tab-ports');
            if (data.open_ports && data.open_ports.length > 0) {
                let html = '<div class="card"><h2>🔓 المنافذ المفتوحة</h2>';
                for (const p of data.open_ports) {
                    html += `<span class="port-open">✅ ${p.port} (${p.service})</span> `;
                }
                html += '</div>';
                ports.innerHTML = html;
            } else {
                ports.innerHTML = '<div class="card"><p style="color: #888;">لا توجد منافذ مفتوحة مكتشفة</p></div>';
            }

            // Subdomains
            const subdomains = document.getElementById('tab-subdomains');
            if (data.subdomains && data.subdomains.length > 0) {
                let html = '<div class="card"><h2>🌐 النطاقات الفرعية المكتشفة</h2>';
                html += `<p style="color: #888;">تم العثور على ${data.subdomains.length} نطاق فرعي</p>`;
                for (const sub of data.subdomains.slice(0, 30)) {
                    html += `<div class="subdomain-item">${sub}</div>`;
                }
                if (data.subdomains.length > 30) {
                    html += `<div class="subdomain-item">... و ${data.subdomains.length - 30} نطاق آخر</div>`;
                }
                html += '</div>';
                subdomains.innerHTML = html;
            } else {
                subdomains.innerHTML = '<div class="card"><p style="color: #888;">لا توجد نطاقات فرعية مكتشفة</p></div>';
            }

            // SNI
            const sni = document.getElementById('tab-sni');
            if (data.sni_recommendations && data.sni_recommendations.length > 0) {
                let html = '<div class="card"><h2>💡 توصيات SNI</h2>';
                for (const item of data.sni_recommendations) {
                    html += `<div class="sni-item"><strong>${item.domain}</strong> <span class="type">[${item.type}]</span></div>`;
                }
                html += '</div>';
                sni.innerHTML = html;
            } else {
                sni.innerHTML = '<div class="card"><p style="color: #888;">لا توجد توصيات SNI</p></div>';
            }

            // SSL
            const ssl = document.getElementById('tab-ssl');
            if (data.ssl_info) {
                let html = '<div class="card"><h2>🔐 معلومات شهادة SSL</h2>';
                html += `<p><strong>الجهة:</strong> ${data.ssl_info.subject || 'N/A'}</p>`;
                html += `<p><strong>المصدر:</strong> ${data.ssl_info.issuer || 'N/A'}</p>`;
                html += `<p><strong>صالحة حتى:</strong> ${data.ssl_info.notAfter || 'N/A'}</p>`;
                html += `<p><strong>النطاقات البديلة:</strong> ${data.ssl_info.san_count || 0}</p>`;
                html += '</div>';
                ssl.innerHTML = html;
            } else {
                ssl.innerHTML = '<div class="card"><p style="color: #888;">لا توجد معلومات SSL متاحة</p></div>';
            }

            // JSON
            document.getElementById('tab-json').innerHTML = `
                <div class="card">
                    <h2>📄 البيانات الخام (JSON)</h2>
                    <div class="json-view">${JSON.stringify(data, null, 2)}</div>
                    <button class="btn btn-secondary" style="margin-top: 10px;" onclick="copyJSON()">📋 نسخ</button>
                </div>
            `;

            switchTab('summary');
        }

        function switchTab(tabId) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));

            document.querySelector(`.tab[onclick="switchTab('${tabId}')"]`).classList.add('active');
            document.getElementById(`tab-${tabId}`).classList.add('active');
        }

        function clearResults() {
            document.getElementById('results').style.display = 'none';
            scanResults = null;
            document.getElementById('targetInput').value = '';
        }

        function copyJSON() {
            if (scanResults) {
                navigator.clipboard.writeText(JSON.stringify(scanResults, null, 2))
                    .then(() => alert('✅ تم نسخ JSON'));
            }
        }
    </script>
</body>
</html>
'''

# ============================================
# دوال المسح
# ============================================

def resolve_domain(domain):
    try:
        answers = dns.resolver.resolve(domain, 'A')
        for rdata in answers:
            return str(rdata)
    except:
        return None

def get_ip_info(ip):
    try:
        response = requests.get(f'https://ipinfo.io/{ip}/json', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                'org': data.get('org', 'غير معروف'),
                'city': data.get('city', 'غير معروف'),
                'region': data.get('region', 'غير معروف'),
                'country': data.get('country', 'غير معروف')
            }
    except:
        pass
    return {'org': 'غير معروف', 'city': 'غير معروف', 'region': 'غير معروف', 'country': 'غير معروف'}

def find_subdomains(domain):
    subdomains = set()
    try:
        url = f"https://crt.sh/?q=%.{domain}&output=json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            for entry in data:
                name = entry.get('name_value', '')
                if name and name.endswith(f'.{domain}'):
                    subdomains.add(name.lower())
    except:
        pass
    return list(subdomains)[:50]

def scan_port(ip, port, timeout=2):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        if result == 0:
            services = {
                21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS',
                80: 'HTTP', 110: 'POP3', 143: 'IMAP', 443: 'HTTPS', 445: 'SMB',
                465: 'SMTPS', 587: 'SMTP', 993: 'IMAPS', 995: 'POP3S',
                1433: 'MSSQL', 3306: 'MySQL', 3389: 'RDP', 5432: 'PostgreSQL',
                6379: 'Redis', 8080: 'HTTP-Alt', 8443: 'HTTPS-Alt', 8888: 'HTTP-Alt'
            }
            return {'port': port, 'service': services.get(port, f'Port-{port}'), 'status': 'open'}
    except:
        pass
    return None

def scan_ports(ip):
    ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 465, 587, 993, 995,
             1433, 3306, 3389, 5432, 6379, 8080, 8443, 8888]
    results = []
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = {executor.submit(scan_port, ip, port): port for port in ports}
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
    return results

def analyze_ssl(ip, port=443):
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        with socket.create_connection((ip, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=ip) as ssock:
                cert = ssock.getpeercert()
                if cert:
                    subject = dict(x[0] for x in cert.get('subject', []))
                    issuer = dict(x[0] for x in cert.get('issuer', []))
                    sans = [alt[1] for alt in cert.get('subjectAltName', []) if alt[0] == 'DNS']
                    return {
                        'subject': subject.get('commonName', 'N/A'),
                        'issuer': issuer.get('commonName', 'N/A'),
                        'notAfter': cert.get('notAfter', 'N/A'),
                        'san_count': len(sans),
                        'sans': sans[:10]
                    }
    except:
        pass
    return None

def generate_sni_recommendations(domain, subdomains, ssl_info):
    recommendations = []
    seen = set()

    recommendations.append({'domain': domain, 'type': 'النطاق الأساسي'})
    seen.add(domain)

    for sub in subdomains:
        if sub not in seen:
            recommendations.append({'domain': sub, 'type': 'نطاق فرعي'})
            seen.add(sub)

    if ssl_info and 'sans' in ssl_info:
        for san in ssl_info['sans']:
            if san not in seen and san.endswith(domain):
                recommendations.append({'domain': san, 'type': 'نطاق بديل (SSL)'})
                seen.add(san)

    return recommendations[:20]

# ============================================
# Routes
# ============================================

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/scan', methods=['POST'])
def scan():
    data = request.get_json()
    target = data.get('target', '').strip()
    if not target:
        return jsonify({'error': 'الرجاء إدخال نطاق أو IP'})

    try:
        ip = resolve_domain(target)
        if not ip:
            try:
                socket.inet_aton(target)
                ip = target
            except:
                return jsonify({'error': 'فشل في حل النطاق أو IP غير صالح'})

        ip_info = get_ip_info(ip)
        subdomains = find_subdomains(target)
        open_ports = scan_ports(ip)

        ssl_info = None
        if any(p['port'] == 443 for p in open_ports):
            ssl_info = analyze_ssl(ip)

        sni_recommendations = generate_sni_recommendations(target, subdomains, ssl_info)

        result = {
            'target': target,
            'main_ip': ip,
            'org': ip_info.get('org', 'غير معروف'),
            'location': f"{ip_info.get('city', 'غير معروف')}, {ip_info.get('country', 'غير معروف')}",
            'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'subdomains_count': len(subdomains),
            'open_ports_count': len(open_ports),
            'sni_count': len(sni_recommendations),
            'subdomains': subdomains,
            'open_ports': open_ports,
            'ssl_info': ssl_info,
            'sni_recommendations': sni_recommendations
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)})

# ============================================
# التشغيل
# ============================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 تشغيل السيرفر على المنفذ: {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
