#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Snap & TikTok Booster - Web Application
"""

from flask import Flask, render_template_string, request, jsonify, send_file
import json
import os
import time
import random
import threading
import subprocess
import re
from datetime import datetime

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
    <title>🚀 Social Boost Pro</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0a0a15; color: #e0e0e0; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; padding: 30px 0; border-bottom: 1px solid #1a1a3e; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; background: linear-gradient(135deg, #ff6b6b, #ffd93d, #6bcb77, #4d96ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .header p { color: #666; font-size: 1.1em; }
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 25px; }
        @media (max-width: 768px) { .grid-2 { grid-template-columns: 1fr; } }
        .card { background: #111128; border-radius: 15px; padding: 25px; border: 1px solid #1a1a3e; }
        .card h2 { color: #4d96ff; margin-bottom: 15px; font-size: 1.3em; }
        .card h2 .icon { margin-left: 10px; }
        .input-group { display: flex; flex-direction: column; gap: 10px; }
        .input-group input { padding: 12px 15px; border-radius: 10px; border: 1px solid #1a1a3e; background: #0a0a15; color: #fff; font-size: 15px; }
        .input-group input:focus { border-color: #4d96ff; outline: none; }
        .input-group select { padding: 12px 15px; border-radius: 10px; border: 1px solid #1a1a3e; background: #0a0a15; color: #fff; font-size: 15px; }
        .btn { padding: 12px 30px; border: none; border-radius: 10px; font-size: 16px; cursor: pointer; transition: all 0.3s; font-weight: bold; }
        .btn-primary { background: linear-gradient(135deg, #4d96ff, #6bcb77); color: #fff; }
        .btn-primary:hover { transform: scale(1.05); box-shadow: 0 0 20px rgba(77, 150, 255, 0.3); }
        .btn-danger { background: linear-gradient(135deg, #ff6b6b, #ff4757); color: #fff; }
        .btn-danger:hover { transform: scale(1.05); box-shadow: 0 0 20px rgba(255, 107, 107, 0.3); }
        .btn-success { background: linear-gradient(135deg, #6bcb77, #2ed573); color: #fff; }
        .btn-success:hover { transform: scale(1.05); box-shadow: 0 0 20px rgba(107, 203, 119, 0.3); }
        .btn-warning { background: linear-gradient(135deg, #ffd93d, #f9ca24); color: #111; }
        .btn-warning:hover { transform: scale(1.05); box-shadow: 0 0 20px rgba(255, 217, 61, 0.3); }
        .status-box { background: #0a0a15; padding: 15px; border-radius: 10px; margin-top: 15px; border: 1px solid #1a1a3e; min-height: 60px; color: #00ff88; font-family: monospace; max-height: 200px; overflow-y: auto; }
        .status-box.error { color: #ff6b6b; }
        .status-box.loading { color: #ffd93d; }
        .stat { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #1a1a3e; }
        .stat .label { color: #888; }
        .stat .value { color: #4d96ff; font-weight: bold; }
        .footer { text-align: center; padding: 30px 0; color: #444; font-size: 0.8em; border-top: 1px solid #1a1a3e; margin-top: 30px; }
        .quick-actions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px; }
        .quick-btn { padding: 6px 15px; background: #0a0a15; border: 1px solid #1a1a3e; border-radius: 20px; color: #888; cursor: pointer; font-size: 0.8em; transition: all 0.2s; }
        .quick-btn:hover { border-color: #4d96ff; color: #4d96ff; }
        .progress-bar { width: 100%; height: 6px; background: #1a1a3e; border-radius: 3px; overflow: hidden; margin: 10px 0; }
        .progress-bar .fill { height: 100%; background: linear-gradient(90deg, #4d96ff, #6bcb77); width: 0%; transition: width 0.5s; }
        .tabs { display: flex; gap: 5px; margin-bottom: 20px; flex-wrap: wrap; }
        .tab { padding: 10px 25px; background: #0a0a15; border: 1px solid #1a1a3e; border-radius: 8px 8px 0 0; cursor: pointer; color: #888; transition: all 0.3s; }
        .tab.active { background: #111128; color: #4d96ff; border-bottom: 2px solid #4d96ff; }
        .tab:hover { color: #fff; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .badge { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 0.7em; background: #4d96ff33; color: #4d96ff; border: 1px solid #4d96ff44; }
        .badge-success { background: #6bcb7733; color: #6bcb77; border: 1px solid #6bcb7744; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Social Boost Pro</h1>
            <p>رفع السيكور والمتابعين واللايكات بشكل آلي واحترافي</p>
        </div>

        <div class="tabs">
            <div class="tab active" onclick="switchTab('snap')">📸 سناب شات</div>
            <div class="tab" onclick="switchTab('tiktok')">🎵 تيك توك</div>
            <div class="tab" onclick="switchTab('stats')">📊 إحصائيات</div>
            <div class="tab" onclick="switchTab('settings')">⚙️ إعدادات</div>
        </div>

        <!-- Tab: Snapchat -->
        <div id="tab-snap" class="tab-content active">
            <div class="grid-2">
                <div class="card">
                    <h2><span class="icon">📸</span> رفع سيكور سناب شات</h2>
                    <div class="input-group">
                        <input type="text" id="snapUsername" placeholder="اسم المستخدم في سناب شات">
                        <input type="number" id="snapCount" placeholder="عدد السنابات المرسلة (100-1000)" value="200">
                        <select id="snapType">
                            <option value="story">نشر ستوريات</option>
                            <option value="chat">إرسال رسائل</option>
                            <option value="both" selected="selected">كلاً من الستوريات والرسائل</option>
                        </select>
                        <button class="btn btn-primary" onclick="boostSnap()">🚀 ابدأ الرفع</button>
                        <div class="quick-actions">
                            <span class="quick-btn" onclick="quickBoost(100)">100 سناب</span>
                            <span class="quick-btn" onclick="quickBoost(300)">300 سناب</span>
                            <span class="quick-btn" onclick="quickBoost(500)">500 سناب</span>
                            <span class="quick-btn" onclick="quickBoost(1000)">1000 سناب</span>
                        </div>
                    </div>
                    <div class="progress-bar"><div class="fill" id="snapProgress"></div></div>
                    <div class="status-box" id="snapStatus">⏳ جاهز للبدء...</div>
                </div>
                <div class="card">
                    <h2><span class="icon">📊</span> معلومات السيكور الحالي</h2>
                    <div id="snapInfo">
                        <div class="stat"><span class="label">👤 اسم المستخدم</span><span class="value" id="snapUserDisplay">-</span></div>
                        <div class="stat"><span class="label">⭐ السيكور الحالي</span><span class="value" id="snapScoreDisplay">-</span></div>
                        <div class="stat"><span class="label">📈 السيكور المستهدف</span><span class="value" id="snapTargetDisplay">-</span></div>
                        <div class="stat"><span class="label">📅 آخر تحديث</span><span class="value" id="snapLastUpdate">-</span></div>
                    </div>
                    <button class="btn btn-secondary" onclick="checkSnapScore()" style="margin-top:10px;">🔍 جلب السيكور</button>
                </div>
            </div>
        </div>

        <!-- Tab: TikTok -->
        <div id="tab-tiktok" class="tab-content">
            <div class="grid-2">
                <div class="card">
                    <h2><span class="icon">🎵</span> رفع متابعين تيك توك</h2>
                    <div class="input-group">
                        <input type="text" id="ttUsername" placeholder="اسم المستخدم في تيك توك">
                        <input type="number" id="ttCount" placeholder="عدد المتابعين/اللايكات" value="100">
                        <select id="ttType">
                            <option value="followers" selected="selected">متابعين</option>
                            <option value="likes">لايكات</option>
                            <option value="views">مشاهدات</option>
                        </select>
                        <button class="btn btn-success" onclick="boostTikTok()">🚀 ابدأ الرفع</button>
                    </div>
                    <div class="progress-bar"><div class="fill" id="ttProgress"></div></div>
                    <div class="status-box" id="ttStatus">⏳ جاهز للبدء...</div>
                </div>
                <div class="card">
                    <h2><span class="icon">📊</span> معلومات الحساب الحالي</h2>
                    <div id="ttInfo">
                        <div class="stat"><span class="label">👤 اسم المستخدم</span><span class="value" id="ttUserDisplay">-</span></div>
                        <div class="stat"><span class="label">👥 المتابعين الحاليين</span><span class="value" id="ttFollowersDisplay">-</span></div>
                        <div class="stat"><span class="label">❤️ اللايكات الحالية</span><span class="value" id="ttLikesDisplay">-</span></div>
                        <div class="stat"><span class="label">📅 آخر تحديث</span><span class="value" id="ttLastUpdate">-</span></div>
                    </div>
                    <button class="btn btn-secondary" onclick="checkTikTokStats()" style="margin-top:10px;">🔍 جلب الإحصائيات</button>
                </div>
            </div>
        </div>

        <!-- Tab: Stats -->
        <div id="tab-stats" class="tab-content">
            <div class="grid-2">
                <div class="card">
                    <h2>📊 إحصائيات السيكور</h2>
                    <div id="statsSnap">
                        <div class="stat"><span class="label">إجمالي السيكور المضاف</span><span class="value" id="totalSnapScore">0</span></div>
                        <div class="stat"><span class="label">عدد جلسات الرفع</span><span class="value" id="totalSnapSessions">0</span></div>
                        <div class="stat"><span class="label">متوسط السيكور لكل جلسة</span><span class="value" id="avgSnapScore">0</span></div>
                    </div>
                </div>
                <div class="card">
                    <h2>📊 إحصائيات تيك توك</h2>
                    <div id="statsTikTok">
                        <div class="stat"><span class="label">إجمالي المتابعين المضافين</span><span class="value" id="totalTTFollowers">0</span></div>
                        <div class="stat"><span class="label">إجمالي اللايكات المضافين</span><span class="value" id="totalTTLikes">0</span></div>
                        <div class="stat"><span class="label">عدد جلسات الرفع</span><span class="value" id="totalTTSessions">0</span></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Tab: Settings -->
        <div id="tab-settings" class="tab-content">
            <div class="card">
                <h2>⚙️ إعدادات متقدمة</h2>
                <div class="input-group">
                    <label style="color:#888;">السرعة (سنابات في الدقيقة)</label>
                    <input type="number" id="speedSetting" value="10" min="1" max="30">
                    <label style="color:#888;">وقت التأخير بين الجلسات (ثواني)</label>
                    <input type="number" id="delaySetting" value="5" min="1" max="60">
                    <label style="color:#888;">وضع الوكيل (Proxy)</label>
                    <select id="proxySetting">
                        <option value="none">بدون وكيل</option>
                        <option value="auto">تلقائي</option>
                        <option value="manual">يدوي</option>
                    </select>
                    <button class="btn btn-primary" onclick="saveSettings()">💾 حفظ الإعدادات</button>
                </div>
            </div>
            <div class="card">
                <h2>📥 تصدير البيانات</h2>
                <button class="btn btn-success" onclick="exportData()">📥 تصدير JSON</button>
                <button class="btn btn-success" onclick="exportDataCSV()" style="margin-right:10px;">📥 تصدير CSV</button>
                <button class="btn btn-danger" onclick="clearData()" style="margin-right:10px;">🗑️ مسح البيانات</button>
            </div>
        </div>

        <div class="footer">🔒 للأغراض التعليمية فقط | تم التطوير بواسطة 🤖</div>
    </div>

    <script>
        let boostInterval = null;
        let settings = JSON.parse(localStorage.getItem('boostSettings') || '{"speed":10, "delay":5, "proxy":"none"}');
        let stats = JSON.parse(localStorage.getItem('boostStats') || '{"snapScore":0, "snapSessions":0, "ttFollowers":0, "ttLikes":0, "ttSessions":0}');

        function switchTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelector(`.tab[onclick="switchTab('${tab}')"]`).classList.add('active');
            document.getElementById('tab-' + tab).classList.add('active');
        }

        function quickBoost(count) {
            document.getElementById('snapCount').value = count;
            boostSnap();
        }

        function boostSnap() {
            const username = document.getElementById('snapUsername').value.trim();
            const count = parseInt(document.getElementById('snapCount').value) || 100;
            const type = document.getElementById('snapType').value;
            if (!username) { alert('الرجاء إدخال اسم المستخدم'); return; }

            document.getElementById('snapStatus').className = 'status-box loading';
            document.getElementById('snapStatus').textContent = '⏳ جاري رفع السيكور...';
            document.getElementById('snapProgress').style.width = '0%';

            fetch('/boost_snap', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: username, count: count, type: type })
            })
            .then(r => r.json())
            .then(data => {
                document.getElementById('snapProgress').style.width = '100%';
                if (data.error) {
                    document.getElementById('snapStatus').className = 'status-box error';
                    document.getElementById('snapStatus').textContent = '❌ ' + data.error;
                    return;
                }
                document.getElementById('snapStatus').className = 'status-box';
                document.getElementById('snapStatus').textContent = '✅ ' + data.message;
                stats.snapScore += count;
                stats.snapSessions += 1;
                localStorage.setItem('boostStats', JSON.stringify(stats));
                updateStats();
                document.getElementById('snapUserDisplay').textContent = username;
                document.getElementById('snapTargetDisplay').textContent = count;
                document.getElementById('snapLastUpdate').textContent = new Date().toLocaleString();
            })
            .catch(e => {
                document.getElementById('snapStatus').className = 'status-box error';
                document.getElementById('snapStatus').textContent = '❌ خطأ: ' + e;
            });
        }

        function boostTikTok() {
            const username = document.getElementById('ttUsername').value.trim();
            const count = parseInt(document.getElementById('ttCount').value) || 100;
            const type = document.getElementById('ttType').value;
            if (!username) { alert('الرجاء إدخال اسم المستخدم'); return; }

            document.getElementById('ttStatus').className = 'status-box loading';
            document.getElementById('ttStatus').textContent = '⏳ جاري رفع المتابعين/اللايكات...';
            document.getElementById('ttProgress').style.width = '0%';

            fetch('/boost_tiktok', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: username, count: count, type: type })
            })
            .then(r => r.json())
            .then(data => {
                document.getElementById('ttProgress').style.width = '100%';
                if (data.error) {
                    document.getElementById('ttStatus').className = 'status-box error';
                    document.getElementById('ttStatus').textContent = '❌ ' + data.error;
                    return;
                }
                document.getElementById('ttStatus').className = 'status-box';
                document.getElementById('ttStatus').textContent = '✅ ' + data.message;
                if (type === 'followers') stats.ttFollowers += count;
                else if (type === 'likes') stats.ttLikes += count;
                stats.ttSessions += 1;
                localStorage.setItem('boostStats', JSON.stringify(stats));
                updateStats();
                document.getElementById('ttUserDisplay').textContent = username;
                document.getElementById('ttLastUpdate').textContent = new Date().toLocaleString();
            })
            .catch(e => {
                document.getElementById('ttStatus').className = 'status-box error';
                document.getElementById('ttStatus').textContent = '❌ خطأ: ' + e;
            });
        }

        function checkSnapScore() {
            const username = document.getElementById('snapUsername').value.trim();
            if (!username) { alert('الرجاء إدخال اسم المستخدم'); return; }
            document.getElementById('snapStatus').textContent = '⏳ جاري جلب السيكور...';
            fetch('/check_snap?username=' + encodeURIComponent(username))
            .then(r => r.json())
            .then(data => {
                if (data.error) {
                    document.getElementById('snapStatus').className = 'status-box error';
                    document.getElementById('snapStatus').textContent = '❌ ' + data.error;
                    return;
                }
                document.getElementById('snapStatus').className = 'status-box';
                document.getElementById('snapStatus').textContent = '✅ السيكور: ' + (data.score || 'غير معروف');
                document.getElementById('snapScoreDisplay').textContent = data.score || '-';
                document.getElementById('snapUserDisplay').textContent = username;
            })
            .catch(e => {
                document.getElementById('snapStatus').className = 'status-box error';
                document.getElementById('snapStatus').textContent = '❌ خطأ: ' + e;
            });
        }

        function checkTikTokStats() {
            const username = document.getElementById('ttUsername').value.trim();
            if (!username) { alert('الرجاء إدخال اسم المستخدم'); return; }
            document.getElementById('ttStatus').textContent = '⏳ جاري جلب الإحصائيات...';
            fetch('/check_tiktok?username=' + encodeURIComponent(username))
            .then(r => r.json())
            .then(data => {
                if (data.error) {
                    document.getElementById('ttStatus').className = 'status-box error';
                    document.getElementById('ttStatus').textContent = '❌ ' + data.error;
                    return;
                }
                document.getElementById('ttStatus').className = 'status-box';
                document.getElementById('ttStatus').textContent = '✅ تم جلب البيانات';
                document.getElementById('ttFollowersDisplay').textContent = data.followers || '-';
                document.getElementById('ttLikesDisplay').textContent = data.likes || '-';
                document.getElementById('ttUserDisplay').textContent = username;
            })
            .catch(e => {
                document.getElementById('ttStatus').className = 'status-box error';
                document.getElementById('ttStatus').textContent = '❌ خطأ: ' + e;
            });
        }

        function updateStats() {
            document.getElementById('totalSnapScore').textContent = stats.snapScore;
            document.getElementById('totalSnapSessions').textContent = stats.snapSessions;
            document.getElementById('avgSnapScore').textContent = stats.snapSessions > 0 ? Math.round(stats.snapScore / stats.snapSessions) : 0;
            document.getElementById('totalTTFollowers').textContent = stats.ttFollowers;
            document.getElementById('totalTTLikes').textContent = stats.ttLikes;
            document.getElementById('totalTTSessions').textContent = stats.ttSessions;
        }

        function saveSettings() {
            settings.speed = parseInt(document.getElementById('speedSetting').value) || 10;
            settings.delay = parseInt(document.getElementById('delaySetting').value) || 5;
            settings.proxy = document.getElementById('proxySetting').value;
            localStorage.setItem('boostSettings', JSON.stringify(settings));
            alert('✅ تم حفظ الإعدادات');
        }

        function exportData() {
            const data = { stats: stats, settings: settings, timestamp: new Date().toISOString() };
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `boost_data_${new Date().toISOString().slice(0,10)}.json`;
            a.click();
            URL.revokeObjectURL(url);
        }

        function exportDataCSV() {
            const rows = [
                ['المقياس', 'القيمة'],
                ['إجمالي السيكور المضاف', stats.snapScore],
                ['جلسات رفع السيكور', stats.snapSessions],
                ['متوسط السيكور', stats.snapSessions > 0 ? Math.round(stats.snapScore / stats.snapSessions) : 0],
                ['متابعين تيك توك المضافين', stats.ttFollowers],
                ['لايكات تيك توك المضافين', stats.ttLikes],
                ['جلسات رفع تيك توك', stats.ttSessions]
            ];
            let csv = rows.map(r => r.join(',')).join('\\n');
            const blob = new Blob(['\\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `boost_data_${new Date().toISOString().slice(0,10)}.csv`;
            a.click();
            URL.revokeObjectURL(url);
        }

        function clearData() {
            if (confirm('هل أنت متأكد من مسح كل البيانات؟')) {
                stats = { snapScore: 0, snapSessions: 0, ttFollowers: 0, ttLikes: 0, ttSessions: 0 };
                localStorage.setItem('boostStats', JSON.stringify(stats));
                updateStats();
                alert('✅ تم مسح البيانات');
            }
        }

        // تحميل الإعدادات
        document.getElementById('speedSetting').value = settings.speed || 10;
        document.getElementById('delaySetting').value = settings.delay || 5;
        document.getElementById('proxySetting').value = settings.proxy || 'none';
        updateStats();
    </script>
</body>
</html>
'''

# ============================================
# BACKEND FUNCTIONS
# ============================================

def simulate_snap_boost(username, count, boost_type):
    """محاكاة رفع سيكور سناب شات"""
    import time
    import random
    
    # محاكاة عملية الرفع
    steps = 10
    for i in range(steps):
        time.sleep(0.3)
        progress = (i + 1) / steps * 100
        yield f"{progress:.0f}% - جاري رفع السيكور... {i+1}/{steps}"
    
    # إضافة نقاط عشوائية للسيكور
    added_score = random.randint(int(count * 0.8), int(count * 1.2))
    yield f"✅ تم إضافة {added_score} نقطة سيكور لحساب {username}"
    return added_score

def simulate_tiktok_boost(username, count, boost_type):
    """محاكاة رفع متابعين/لايكات تيك توك"""
    import time
    import random
    
    steps = 8
    for i in range(steps):
        time.sleep(0.3)
        progress = (i + 1) / steps * 100
        yield f"{progress:.0f}% - جاري رفع {boost_type}... {i+1}/{steps}"
    
    added = random.randint(int(count * 0.9), int(count * 1.1))
    yield f"✅ تم إضافة {added} {boost_type} لحساب {username}"
    return added

# ============================================
# ROUTES
# ============================================

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/boost_snap', methods=['POST'])
def boost_snap():
    data = request.get_json()
    username = data.get('username', '').strip()
    count = int(data.get('count', 100))
    boost_type = data.get('type', 'both')
    
    if not username:
        return jsonify({'error': 'الرجاء إدخال اسم المستخدم'})
    
    # محاكاة رفع السيكور
    added_score = simulate_snap_boost(username, count, boost_type)
    
    return jsonify({'message': f'تم إضافة {added_score} نقطة سيكور بنجاح', 'score': added_score})

@app.route('/boost_tiktok', methods=['POST'])
def boost_tiktok():
    data = request.get_json()
    username = data.get('username', '').strip()
    count = int(data.get('count', 100))
    boost_type = data.get('type', 'followers')
    
    if not username:
        return jsonify({'error': 'الرجاء إدخال اسم المستخدم'})
    
    # محاكاة رفع التيك توك
    added = simulate_tiktok_boost(username, count, boost_type)
    
    return jsonify({'message': f'تم إضافة {added} {boost_type} بنجاح', 'added': added})

@app.route('/check_snap')
def check_snap():
    username = request.args.get('username', '').strip()
    if not username:
        return jsonify({'error': 'الرجاء إدخال اسم المستخدم'})
    
    # محاكاة جلب السيكور
    import random
    score = random.randint(1000, 50000)
    return jsonify({'score': score})

@app.route('/check_tiktok')
def check_tiktok():
    username = request.args.get('username', '').strip()
    if not username:
        return jsonify({'error': 'الرجاء إدخال اسم المستخدم'})
    
    # محاكاة جلب إحصائيات تيك توك
    import random
    followers = random.randint(100, 10000)
    likes = random.randint(500, 50000)
    return jsonify({'followers': followers, 'likes': likes})

# ============================================
# RUN
# ============================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 تشغيل السيرفر على المنفذ: {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
