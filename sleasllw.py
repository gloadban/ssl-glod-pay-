#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Network Scanner & SNI Analyzer - Web Version v2.0
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
import re
import time
import base64
import hashlib
import ipaddress
import subprocess
import threading

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
    <title>🌐 Network Scanner & SNI Analyzer</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0a0a15; color: #e0e0e0; }
        .app-container { display: flex; min-height: 100vh; }
        .sidebar { width: 280px; background: #111128; border-right: 1px solid #222244; padding: 20px; position: fixed; height: 100vh; overflow-y: auto; }
        .sidebar .logo { text-align: center; padding: 20px 0; border-bottom: 1px solid #222244; margin-bottom: 20px; }
        .sidebar .logo h1 { font-size: 1.5em; background: linear-gradient(135deg, #00d4ff, #7b2ffc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .sidebar .logo small { color: #666; font-size: 0.8em; }
        .sidebar-menu { list-style: none; }
        .sidebar-menu li { padding: 12px 15px; margin: 5px 0; border-radius: 10px; cursor: pointer; transition: all 0.3s; color: #aaa; border-left: 3px solid transparent; }
        .sidebar-menu li:hover { background: #1a1a3e; color: #fff; }
        .sidebar-menu li.active { background: #1a1a3e; color: #00d4ff; border-left-color: #00d4ff; }
        .sidebar-menu li .icon { margin-left: 10px; }
        .sidebar-menu li .badge { float: left; background: #2a2a5a; padding: 2px 8px; border-radius: 20px; font-size: 0.7em; color: #888; }
        .main-content { margin-right: 280px; flex: 1; padding: 30px; }
        .header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 20px; border-bottom: 1px solid #222244; margin-bottom: 30px; }
        .header h2 { color: #fff; font-size: 1.8em; }
        .header .status { color: #00ff88; font-size: 0.9em; }
        .card { background: #111128; border-radius: 15px; padding: 25px; margin-bottom: 25px; border: 1px solid #222244; }
        .card h3 { color: #00d4ff; margin-bottom: 15px; font-size: 1.1em; }
        .input-group { display: flex; gap: 10px; flex-wrap: wrap; }
        .input-group input { flex: 1; padding: 12px 20px; border-radius: 10px; border: 1px solid #2a2a4a; background: #0a0a15; color: #fff; font-size: 16px; min-width: 200px; }
        .input-group input:focus { border-color: #00d4ff; outline: none; }
        .btn { padding: 12px 30px; border: none; border-radius: 10px; font-size: 16px; cursor: pointer; transition: all 0.3s; font-weight: bold; }
        .btn-primary { background: linear-gradient(135deg, #00d4ff, #7b2ffc); color: #fff; }
        .btn-primary:hover { transform: scale(1.05); box-shadow: 0 0 20px rgba(0, 212, 255, 0.3); }
        .btn-secondary { background: #2a2a4a; color: #fff; }
        .btn-secondary:hover { background: #3a3a5a; }
        .btn-success { background: #00ff8833; color: #00ff88; border: 1px solid #00ff8844; }
        .btn-success:hover { background: #00ff8844; }
        .btn-danger { background: #ff444433; color: #ff4444; border: 1px solid #ff444444; }
        .btn-danger:hover { background: #ff444455; }
        .results-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .stat-box { background: #0a0a15; padding: 20px; border-radius: 10px; border: 1px solid #1a1a3e; text-align: center; }
        .stat-box .number { font-size: 2.5em; font-weight: bold; color: #00d4ff; }
        .stat-box .label { color: #888; font-size: 0.85em; margin-top: 5px; }
        .stat-box .sub { color: #555; font-size: 0.7em; }
        .port-open { color: #00ff88; }
        .port-closed { color: #ff4444; }
        .port-filtered { color: #ffaa00; }
        .sni-item { background: #0a0a15; padding: 10px 15px; border-radius: 8px; margin: 5px 0; border-left: 3px solid #7b2ffc; display: flex; justify-content: space-between; align-items: center; }
        .sni-item .type { color: #888; font-size: 0.8em; }
        .sni-item .badge-sni { padding: 2px 10px; border-radius: 20px; font-size: 0.7em; background: #00d4ff22; color: #00d4ff; border: 1px solid #00d4ff44; }
        .subdomain-item { background: #0a0a15; padding: 6px 15px; border-radius: 5px; margin: 3px 0; font-size: 0.9em; color: #aaa; display: flex; justify-content: space-between; }
        .subdomain-item .ip { color: #666; font-size: 0.8em; }
        .loading { display: none; text-align: center; padding: 40px; }
        .loading .spinner { width: 50px; height: 50px; border: 4px solid #1a1a3e; border-top: 4px solid #00d4ff; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .tabs { display: flex; gap: 5px; margin-bottom: 20px; flex-wrap: wrap; }
        .tab { padding: 10px 20px; background: #0a0a15; border: 1px solid #1a1a3e; border-radius: 8px 8px 0 0; cursor: pointer; transition: all 0.3s; }
        .tab:hover { background: #1a1a3e; }
        .tab.active { background: #1a1a3e; border-bottom: 2px solid #00d4ff; color: #00d4ff; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .json-view { background: #0a0a15; padding: 15px; border-radius: 10px; overflow-x: auto; white-space: pre-wrap; font-family: monospace; font-size: 0.85em; max-height: 500px; overflow-y: auto; }
        .history-list { max-height: 400px; overflow-y: auto; }
        .history-item { padding: 10px 15px; background: #0a0a15; border-radius: 8px; margin: 5px 0; border: 1px solid #1a1a3e; display: flex; justify-content: space-between; align-items: center; }
        .history-item .time { color: #666; font-size: 0.8em; }
        .history-item .target { color: #00d4ff; }
        .footer { text-align: center; padding: 20px; color: #444; font-size: 0.8em; border-top: 1px solid #1a1a3e; margin-top: 30px; }
        .quick-buttons { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 10px; }
        .quick-btn { padding: 5px 15px; background: #0a0a15; border: 1px solid #1a1a3e; border-radius: 20px; color: #888; cursor: pointer; font-size: 0.8em; transition: all 0.2s; }
        .quick-btn:hover { border-color: #00d4ff; color: #00d4ff; background: #0a0a15; }
        .progress-bar { width: 100%; height: 4px; background: #1a1a3e; border-radius: 2px; overflow: hidden; margin: 10px 0; }
        .progress-bar .fill { height: 100%; background: linear-gradient(90deg, #00d4ff, #7b2ffc); width: 0%; transition: width 0.5s; }
        @media (max-width: 768px) { .sidebar { width: 100%; position: relative; height: auto; } .main-content { margin-right: 0; } .app-container { flex-direction: column; } }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #0a0a15; }
        ::-webkit-scrollbar-thumb { background: #1a1a3e; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: #2a2a5a; }
    </style>
</head>
<body>
    <div class="app-container">
        <!-- Sidebar -->
        <div class="sidebar">
            <div class="logo">
                <h1>🌐 SNI Scanner</h1>
                <small>v2.0 - Network Analyzer</small>
            </div>
            <ul class="sidebar-menu">
                <li class="active" onclick="switchPage('home')">
                    <span class="icon">🏠</span> الرئيسية
                </li>
                <li onclick="switchPage('scan')">
                    <span class="icon">🔍</span> فحص جديد
                </li>
                <li onclick="switchPage('history')">
                    <span class="icon">📋</span> السجل <span class="badge" id="historyCount">0</span>
                </li>
                <li onclick="switchPage('sni')">
                    <span class="icon">💡</span> توصيات SNI
                </li>
                <li onclick="switchPage('tools')">
                    <span class="icon">🛠️</span> أدوات
                </li>
                <li onclick="switchPage('settings')">
                    <span class="icon">⚙️</span> الإعدادات
                </li>
                <li onclick="switchPage('about')">
                    <span class="icon">ℹ️</span> عن الأداة
                </li>
            </ul>
        </div>

        <!-- Main Content -->
        <div class="main-content">
            <!-- Home -->
            <div id="page-home" class="page-content">
                <div class="header">
                    <h2>🏠 لوحة التحكم</h2>
                    <span class="status">🟢 السيرفر نشط</span>
                </div>
                <div class="results-grid" id="homeStats">
                    <div class="stat-box"><div class="number" id="statTargets">0</div><div class="label">إجمالي الفحوصات</div></div>
                    <div class="stat-box"><div class="number" id="statDomains">0</div><div class="label">نطاقات مفحوصة</div></div>
                    <div class="stat-box"><div class="number" id="statSubdomains">0</div><div class="label">نطاقات فرعية مكتشفة</div></div>
                    <div class="stat-box"><div class="number" id="statOpenPorts">0</div><div class="label">منافذ مفتوحة</div></div>
                </div>
                <div class="card">
                    <h3>🚀 ابدأ فحصاً سريعاً</h3>
                    <div class="input-group">
                        <input type="text" id="quickTarget" placeholder="أدخل نطاق (مثل stc.com.sa)" value="stc.com.sa">
                        <button class="btn btn-primary" onclick="quickScan()">🚀 فحص</button>
                    </div>
                    <div class="quick-buttons">
                        <span class="quick-btn" onclick="setTarget('stc.com.sa')">stc.com.sa</span>
                        <span class="quick-btn" onclick="setTarget('mobily.com.sa')">mobily.com.sa</span>
                        <span class="quick-btn" onclick="setTarget('zain.com.sa')">zain.com.sa</span>
                        <span class="quick-btn" onclick="setTarget('botgateway.stc.com.sa')">botgateway</span>
                        <span class="quick-btn" onclick="setTarget('cloud.stc.com.sa')">cloud.stc</span>
                        <span class="quick-btn" onclick="setTarget('mail.stcgroup.stc.com.sa')">mail.stc</span>
                        <span class="quick-btn" onclick="setTarget('camspm.scan.stc.com.sa')">camspm</span>
                    </div>
                </div>
            </div>

            <!-- Scan -->
            <div id="page-scan" class="page-content" style="display:none;">
                <div class="header">
                    <h2>🔍 فحص جديد</h2>
                    <span class="status">🟢 جاهز</span>
                </div>
                <div class="card">
                    <h3>🎯 إدخال الهدف</h3>
                    <div class="input-group">
                        <input type="text" id="targetInput" placeholder="أدخل نطاق (مثل stc.com.sa) أو IP">
                        <button class="btn btn-primary" onclick="startScan()">🚀 فحص</button>
                        <button class="btn btn-secondary" onclick="clearResults()">🗑️ مسح</button>
                    </div>
                    <div class="quick-buttons">
                        <span class="quick-btn" onclick="setTarget2('stc.com.sa')">stc.com.sa</span>
                        <span class="quick-btn" onclick="setTarget2('mobily.com.sa')">mobily.com.sa</span>
                        <span class="quick-btn" onclick="setTarget2('zain.com.sa')">zain.com.sa</span>
                        <span class="quick-btn" onclick="setTarget2('botgateway.stc.com.sa')">botgateway.stc</span>
                        <span class="quick-btn" onclick="setTarget2('cloud.stc.com.sa')">cloud.stc</span>
                        <span class="quick-btn" onclick="setTarget2('mail.stcgroup.stc.com.sa')">mail.stc</span>
                    </div>
                </div>

                <div id="loading" class="loading">
                    <div class="spinner"></div>
                    <p style="margin-top: 20px; color: #888;">جاري الفحص... قد يستغرق بعض الوقت</p>
                    <div class="progress-bar"><div class="fill" id="progressFill"></div></div>
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
            </div>

            <!-- History -->
            <div id="page-history" class="page-content" style="display:none;">
                <div class="header"><h2>📋 سجل الفحوصات</h2><span class="status" id="historyStatus">🟢 0 فحص</span></div>
                <div class="card">
                    <h3>الفحوصات السابقة</h3>
                    <div id="historyList" class="history-list">
                        <p style="color: #666; text-align: center; padding: 40px;">لا توجد فحوصات سابقة</p>
                    </div>
                    <button class="btn btn-danger" onclick="clearHistory()">🗑️ مسح السجل</button>
                </div>
            </div>

            <!-- SNI -->
            <div id="page-sni" class="page-content" style="display:none;">
                <div class="header"><h2>💡 توصيات SNI</h2><span class="status">🟢 جاهز</span></div>
                <div class="card">
                    <h3>أفضل النطاقات المقترحة للاستخدام</h3>
                    <div id="sniList">
                        <p style="color: #666; text-align: center; padding: 40px;">قم بفحص نطاق أولاً للحصول على توصيات</p>
                    </div>
                </div>
            </div>

            <!-- Tools -->
            <div id="page-tools" class="page-content" style="display:none;">
                <div class="header"><h2>🛠️ أدوات مساعدة</h2><span class="status">🟢 جاهز</span></div>
                <div class="results-grid">
                    <div class="card" style="grid-column: span 1;">
                        <h3>🔍 استعلام DNS</h3>
                        <input type="text" id="dnsQuery" placeholder="أدخل نطاق" style="width:100%; padding:10px; background:#0a0a15; border:1px solid #1a1a3e; border-radius:8px; color:#fff; margin-bottom:10px;">
                        <button class="btn btn-primary" onclick="dnsLookup()">🔍 استعلام</button>
                        <div id="dnsResult" style="margin-top:10px; color:#888;"></div>
                    </div>
                    <div class="card" style="grid-column: span 1;">
                        <h3>🌐 فحص IP</h3>
                        <input type="text" id="ipQuery" placeholder="أدخل IP" style="width:100%; padding:10px; background:#0a0a15; border:1px solid #1a1a3e; border-radius:8px; color:#fff; margin-bottom:10px;">
                        <button class="btn btn-primary" onclick="ipLookup()">🌐 فحص</button>
                        <div id="ipResult" style="margin-top:10px; color:#888;"></div>
                    </div>
                    <div class="card" style="grid-column: span 1;">
                        <h3>🔓 فحص منفذ</h3>
                        <input type="text" id="portTarget" placeholder="IP أو نطاق" style="width:100%; padding:10px; background:#0a0a15; border:1px solid #1a1a3e; border-radius:8px; color:#fff; margin-bottom:10px;">
                        <input type="number" id="portNumber" placeholder="رقم المنفذ" style="width:100%; padding:10px; background:#0a0a15; border:1px solid #1a1a3e; border-radius:8px; color:#fff; margin-bottom:10px;">
                        <button class="btn btn-primary" onclick="portCheck()">🔓 فحص</button>
                        <div id="portResult" style="margin-top:10px; color:#888;"></div>
                    </div>
                    <div class="card" style="grid-column: span 1;">
                        <h3>⚡ تحويل Host to IP</h3>
                        <input type="text" id="hostQuery" placeholder="أدخل نطاق" style="width:100%; padding:10px; background:#0a0a15; border:1px solid #1a1a3e; border-radius:8px; color:#fff; margin-bottom:10px;">
                        <button class="btn btn-primary" onclick="hostToIP()">⚡ تحويل</button>
                        <div id="hostResult" style="margin-top:10px; color:#888;"></div>
                    </div>
                </div>
            </div>

            <!-- Settings -->
            <div id="page-settings" class="page-content" style="display:none;">
                <div class="header"><h2>⚙️ الإعدادات</h2><span class="status">🟢 جاهز</span></div>
                <div class="card">
                    <h3>إعدادات الفحص</h3>
                    <div style="margin: 10px 0;">
                        <label style="color:#888;">عدد خيوط الفحص:</label>
                        <input type="number" id="threadsSetting" value="50" style="padding:8px; background:#0a0a15; border:1px solid #1a1a3e; border-radius:8px; color:#fff; width:80px;">
                    </div>
                    <div style="margin: 10px 0;">
                        <label style="color:#888;">زمن الانتظار (ثواني):</label>
                        <input type="number" id="timeoutSetting" value="3" style="padding:8px; background:#0a0a15; border:1px solid #1a1a3e; border-radius:8px; color:#fff; width:80px;">
                    </div>
                    <button class="btn btn-primary" onclick="saveSettings()">💾 حفظ الإعدادات</button>
                </div>
            </div>

            <!-- About -->
            <div id="page-about" class="page-content" style="display:none;">
                <div class="header"><h2>ℹ️ عن الأداة</h2><span class="status">🟢 v2.0</span></div>
                <div class="card">
                    <h3>🌐 Network Scanner & SNI Analyzer</h3>
                    <p style="color:#888; line-height:1.8; margin-top:10px;">
                        أداة متخصصة في فحص الشبكات وتحليل SNI لشبكات الاتصالات.<br>
                        <br>
                        <strong>المميزات:</strong><br>
                        🔍 فحص المنافذ المفتوحة (23 منفذ شائع)<br>
                        🌐 اكتشاف النطاقات الفرعية باستخدام crt.sh<br>
                        🔐 تحليل شهادات SSL واستخراج النطاقات البديلة<br>
                        💡 توليد توصيات SNI من النطاقات المكتشفة<br>
                        📋 سجل الفحوصات السابقة<br>
                        🛠️ أدوات مساعدة (DNS, IP, Port, Host to IP)<br>
                        <br>
                        <strong>للأغراض التعليمية والبحثية فقط</strong>
                    </p>
                </div>
            </div>

            <div class="footer">🔒 للأغراض التعليمية والبحثية فقط | تم التطوير بواسطة 🤖</div>
        </div>
    </div>

    <script>
        let scanResults = null;
        let history = JSON.parse(localStorage.getItem('scanHistory') || '[]');
        let settings = JSON.parse(localStorage.getItem('scannerSettings') || '{"threads":50, "timeout":3}');

        function updateHistoryCount() {
            document.getElementById('historyCount').textContent = history.length;
            document.getElementById('historyStatus').textContent = '🟢 ' + history.length + ' فحص';
        }
        updateHistoryCount();

        function switchPage(page) {
            document.querySelectorAll('.page-content').forEach(p => p.style.display = 'none');
            document.getElementById('page-' + page).style.display = 'block';
            document.querySelectorAll('.sidebar-menu li').forEach(l => l.classList.remove('active'));
            document.querySelectorAll('.sidebar-menu li').forEach(l => {
                if (l.textContent.includes(page === 'home' ? 'الرئيسية' :
                    page === 'scan' ? 'فحص جديد' :
                    page === 'history' ? 'السجل' :
                    page === 'sni' ? 'توصيات SNI' :
                    page === 'tools' ? 'أدوات' :
                    page === 'settings' ? 'الإعدادات' : 'عن الأداة')) {
                    l.classList.add('active');
                }
            });
            if (page === 'history') renderHistory();
            if (page === 'sni') renderSNI();
            if (page === 'home') updateHomeStats();
        }

        function setTarget(target) {
            document.getElementById('quickTarget').value = target;
            quickScan();
        }

        function setTarget2(target) {
            document.getElementById('targetInput').value = target;
        }

        function quickScan() {
            const target = document.getElementById('quickTarget').value.trim();
            if (!target) { alert('الرجاء إدخال نطاق'); return; }
            document.getElementById('targetInput').value = target;
            switchPage('scan');
            setTimeout(startScan, 300);
        }

        function startScan() {
            const target = document.getElementById('targetInput').value.trim();
            if (!target) { alert('الرجاء إدخال نطاق أو IP'); return; }

            document.getElementById('loading').style.display = 'block';
            document.getElementById('results').style.display = 'none';
            document.getElementById('progressFill').style.width = '10%';

            fetch('/scan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ target: target })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('progressFill').style.width = '100%';
                document.getElementById('loading').style.display = 'none';
                if (data.error) {
                    alert('❌ ' + data.error);
                    return;
                }
                scanResults = data;
                history.unshift({ target: data.target, time: data.scan_time, results: data });
                if (history.length > 50) history.pop();
                localStorage.setItem('scanHistory', JSON.stringify(history));
                updateHistoryCount();
                displayResults(data);
                document.getElementById('results').style.display = 'block';
                updateHomeStats();
            })
            .catch(error => {
                document.getElementById('loading').style.display = 'none';
                alert('❌ حدث خطأ: ' + error);
            });
        }

        function displayResults(data) {
            // Summary
            document.getElementById('tab-summary').innerHTML = `
                <div class="results-grid">
                    <div class="stat-box"><div class="number">${data.main_ip || 'N/A'}</div><div class="label">IP الرئيسي</div></div>
                    <div class="stat-box"><div class="number">${data.subdomains_count || 0}</div><div class="label">النطاقات الفرعية</div></div>
                    <div class="stat-box"><div class="number">${data.open_ports_count || 0}</div><div class="label">المنافذ المفتوحة</div></div>
                    <div class="stat-box"><div class="number">${data.sni_count || 0}</div><div class="label">توصيات SNI</div></div>
                </div>
                <div style="padding:15px; background:#0a0a15; border-radius:10px; margin-top:10px;">
                    <p><strong>🎯 النطاق:</strong> ${data.target}</p>
                    <p><strong>📌 الوقت:</strong> ${data.scan_time || 'N/A'}</p>
                    <p><strong>🏢 المزود:</strong> ${data.org || 'غير معروف'}</p>
                    <p><strong>📍 الموقع:</strong> ${data.location || 'غير معروف'}</p>
                </div>
            `;

            // Ports
            let portsHtml = '<div class="card"><h3>🔓 المنافذ المفتوحة</h3>';
            if (data.open_ports && data.open_ports.length > 0) {
                for (const p of data.open_ports) {
                    portsHtml += `<span class="port-open">✅ ${p.port} (${p.service})</span> `;
                }
            } else {
                portsHtml += '<p style="color:#888;">لا توجد منافذ مفتوحة مكتشفة</p>';
            }
            portsHtml += '</div>';
            document.getElementById('tab-ports').innerHTML = portsHtml;

            // Subdomains
            let subHtml = '<div class="card"><h3>🌐 النطاقات الفرعية المكتشفة</h3>';
            if (data.subdomains && data.subdomains.length > 0) {
                subHtml += `<p style="color:#888; margin-bottom:10px;">تم العثور على ${data.subdomains.length} نطاق فرعي</p>`;
                for (const sub of data.subdomains.slice(0, 50)) {
                    subHtml += `<div class="subdomain-item">${sub}</div>`;
                }
                if (data.subdomains.length > 50) {
                    subHtml += `<div class="subdomain-item" style="color:#666;">... و ${data.subdomains.length - 50} نطاق آخر</div>`;
                }
            } else {
                subHtml += '<p style="color:#888;">لا توجد نطاقات فرعية مكتشفة</p>';
            }
            subHtml += '</div>';
            document.getElementById('tab-subdomains').innerHTML = subHtml;

            // SNI
            let sniHtml = '<div class="card"><h3>💡 توصيات SNI</h3>';
            if (data.sni_recommendations && data.sni_recommendations.length > 0) {
                for (const item of data.sni_recommendations) {
                    const badge = item.type.includes('أساسي') ? 'badge-sni' : '';
                    sniHtml += `<div class="sni-item">
                        <span><strong>${item.domain}</strong> <span class="type">[${item.type}]</span></span>
                        <span class="${badge}">${item.type.includes('أساسي') ? '⭐ ممتاز' : ''}</span>
                    </div>`;
                }
            } else {
                sniHtml += '<p style="color:#888;">لا توجد توصيات SNI</p>';
            }
            sniHtml += '</div>';
            document.getElementById('tab-sni').innerHTML = sniHtml;

            // SSL
            let sslHtml = '<div class="card"><h3>🔐 معلومات شهادة SSL</h3>';
            if (data.ssl_info) {
                sslHtml += `
                    <p><strong>الجهة:</strong> ${data.ssl_info.subject || 'N/A'}</p>
                    <p><strong>المصدر:</strong> ${data.ssl_info.issuer || 'N/A'}</p>
                    <p><strong>صالحة حتى:</strong> ${data.ssl_info.notAfter || 'N/A'}</p>
                    <p><strong>النطاقات البديلة:</strong> ${data.ssl_info.san_count || 0}</p>
                `;
            } else {
                sslHtml += '<p style="color:#888;">لا توجد معلومات SSL متاحة</p>';
            }
            sslHtml += '</div>';
            document.getElementById('tab-ssl').innerHTML = sslHtml;

            // JSON
            document.getElementById('tab-json').innerHTML = `
                <div class="card">
                    <h3>📄 البيانات الخام (JSON)</h3>
                    <div class="json-view">${JSON.stringify(data, null, 2)}</div>
                    <button class="btn btn-secondary" style="margin-top:10px;" onclick="copyJSON()">📋 نسخ</button>
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
        }

        function copyJSON() {
            if (scanResults) {
                navigator.clipboard.writeText(JSON.stringify(scanResults, null, 2))
                    .then(() => alert('✅ تم نسخ JSON'));
            }
        }

        function renderHistory() {
            const container = document.getElementById('historyList');
            if (history.length === 0) {
                container.innerHTML = '<p style="color:#666; text-align:center; padding:40px;">لا توجد فحوصات سابقة</p>';
                return;
            }
            let html = '';
            for (const item of history) {
                const res = item.results || {};
                html += `<div class="history-item">
                    <div><span class="target">${item.target}</span> <span style="color:#666;font-size:0.8em;">${res.open_ports_count || 0} منفذ مفتوح</span></div>
                    <div><span class="time">${item.time}</span> <button class="btn btn-secondary" style="padding:3px 10px;font-size:0.7em;" onclick="loadHistory('${item.target}')">📂 فتح</button></div>
                </div>`;
            }
            container.innerHTML = html;
        }

        function loadHistory(target) {
            document.getElementById('targetInput').value = target;
            switchPage('scan');
            setTimeout(startScan, 300);
        }

        function clearHistory() {
            if (confirm('هل أنت متأكد من مسح السجل؟')) {
                history = [];
                localStorage.setItem('scanHistory', JSON.stringify(history));
                updateHistoryCount();
                renderHistory();
            }
        }

        function renderSNI() {
            const container = document.getElementById('sniList');
            if (!scanResults || !scanResults.sni_recommendations || scanResults.sni_recommendations.length === 0) {
                container.innerHTML = '<p style="color:#666; text-align:center; padding:40px;">قم بفحص نطاق أولاً للحصول على توصيات</p>';
                return;
            }
            let html = '';
            for (const item of scanResults.sni_recommendations) {
                html += `<div class="sni-item">
                    <span><strong>${item.domain}</strong> <span class="type">[${item.type}]</span></span>
                    <span class="badge-sni">${item.type.includes('أساسي') ? '⭐ ممتاز' : ''}</span>
                </div>`;
            }
            container.innerHTML = html;
        }

        function updateHomeStats() {
            document.getElementById('statTargets').textContent = history.length;
            let domains = 0, subdomains = 0, ports = 0;
            for (const item of history) {
                const res = item.results || {};
                if (res.target) domains++;
                if (res.subdomains_count) subdomains += res.subdomains_count;
                if (res.open_ports_count) ports += res.open_ports_count;
            }
            document.getElementById('statDomains').textContent = domains;
            document.getElementById('statSubdomains').textContent = subdomains;
            document.getElementById('statOpenPorts').textContent = ports;
        }

        // Tools
        function dnsLookup() {
            const domain = document.getElementById('dnsQuery').value.trim();
            if (!domain) { alert('أدخل نطاق'); return; }
            document.getElementById('dnsResult').innerHTML = '⏳ جاري البحث...';
            fetch('/dns?domain=' + encodeURIComponent(domain))
                .then(r => r.json())
                .then(data => {
                    document.getElementById('dnsResult').innerHTML = data.result || '❌ لا توجد نتائج';
                })
                .catch(() => document.getElementById('dnsResult').innerHTML = '❌ خطأ');
        }

        function ipLookup() {
            const ip = document.getElementById('ipQuery').value.trim();
            if (!ip) { alert('أدخل IP'); return; }
            document.getElementById('ipResult').innerHTML = '⏳ جاري الفحص...';
            fetch('/ipinfo?ip=' + encodeURIComponent(ip))
                .then(r => r.json())
                .then(data => {
                    document.getElementById('ipResult').innerHTML = data.result || '❌ لا توجد معلومات';
                })
                .catch(() => document.getElementById('ipResult').innerHTML = '❌ خطأ');
        }

        function portCheck() {
            const target = document.getElementById('portTarget').value.trim();
            const port = document.getElementById('portNumber').value.trim();
            if (!target || !port) { alert('أدخل IP/nطاق ورقم المنفذ'); return; }
            document.getElementById('portResult').innerHTML = '⏳ جاري الفحص...';
            fetch('/port?target=' + encodeURIComponent(target) + '&port=' + encodeURIComponent(port))
                .then(r => r.json())
                .then(data => {
                    document.getElementById('portResult').innerHTML = data.result || '❌ لا توجد معلومات';
                })
                .catch(() => document.getElementById('portResult').innerHTML = '❌ خطأ');
        }

        function hostToIP() {
            const host = document.getElementById('hostQuery').value.trim();
            if (!host) { alert('أدخل نطاق'); return; }
            document.getElementById('hostResult').innerHTML = '⏳ جاري التحويل...';
            fetch('/hosttoip?host=' + encodeURIComponent(host))
                .then(r => r.json())
                .then(data => {
                    document.getElementById('hostResult').innerHTML = data.result || '❌ لا توجد معلومات';
                })
                .catch(() => document.getElementById('hostResult').innerHTML = '❌ خطأ');
        }

        function saveSettings() {
            settings.threads = parseInt(document.getElementById('threadsSetting').value) || 50;
            settings.timeout = parseInt(document.getElementById('timeoutSetting').value) || 3;
            localStorage.setItem('scannerSettings', JSON.stringify(settings));
            alert('✅ تم حفظ الإعدادات');
        }

        // تحميل الإعدادات
        document.getElementById('threadsSetting').value = settings.threads || 50;
        document.getElementById('timeoutSetting').value = settings.timeout || 3;
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
    return list(subdomains)[:100]

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

def scan_ports(ip, timeout=2):
    ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 465, 587, 993, 995,
             1433, 3306, 3389, 5432, 6379, 8080, 8443, 8888]
    results = []
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(scan_port, ip, port, timeout): port for port in ports}
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
    return recommendations[:30]

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
        timeout = int(data.get('timeout', 3))
        open_ports = scan_ports(ip, timeout)
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

@app.route('/dns')
def dns_lookup():
    domain = request.args.get('domain', '')
    if not domain:
        return jsonify({'result': '❌ الرجاء إدخال نطاق'})
    try:
        answers = dns.resolver.resolve(domain, 'A')
        ips = [str(r) for r in answers]
        return jsonify({'result': f'✅ {domain} → {", ".join(ips)}'})
    except:
        return jsonify({'result': f'❌ فشل في حل {domain}'})

@app.route('/ipinfo')
def ip_info():
    ip = request.args.get('ip', '')
    if not ip:
        return jsonify({'result': '❌ الرجاء إدخال IP'})
    try:
        info = get_ip_info(ip)
        return jsonify({'result': f'✅ {ip}\n🏢 {info["org"]}\n📍 {info["city"]}, {info["country"]}'})
    except:
        return jsonify({'result': f'❌ فشل في جلب معلومات {ip}'})

@app.route('/port')
def port_check():
    target = request.args.get('target', '')
    port = request.args.get('port', '')
    if not target or not port:
        return jsonify({'result': '❌ الرجاء إدخال هدف ومنفذ'})
    try:
        port = int(port)
        ip = resolve_domain(target) or target
        result = scan_port(ip, port)
        if result:
            return jsonify({'result': f'✅ {target}:{port} → مفتوح ({result["service"]})'})
        else:
            return jsonify({'result': f'❌ {target}:{port} → مغلق أو غير مستجيب'})
    except:
        return jsonify({'result': f'❌ خطأ في فحص {target}:{port}'})

@app.route('/hosttoip')
def host_to_ip():
    host = request.args.get('host', '')
    if not host:
        return jsonify({'result': '❌ الرجاء إدخال نطاق'})
    try:
        ip = resolve_domain(host)
        if ip:
            return jsonify({'result': f'✅ {host} → {ip}'})
        else:
            return jsonify({'result': f'❌ فشل في حل {host}'})
    except:
        return jsonify({'result': f'❌ خطأ في تحويل {host}'})

# ============================================
# التشغيل
# ============================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 تشغيل السيرفر على المنفذ: {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
