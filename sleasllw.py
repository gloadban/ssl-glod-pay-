#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
All-in-One Network Tools - Web Version
"""

from flask import Flask, render_template_string, request, jsonify, send_file
import socket
import ssl
import dns.resolver
import requests
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import base64
import hashlib
import ipaddress
import time
import csv
import io

app = Flask(__name__)

# ============================================
# HTML TEMPLATE
# ============================================

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔧 Network Tools</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0a0a15; color: #e0e0e0; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; padding: 30px 0; border-bottom: 1px solid #1a1a3e; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; background: linear-gradient(135deg, #00d4ff, #7b2ffc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .header p { color: #666; }
        .grid-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; }
        .card { background: #111128; border-radius: 15px; padding: 25px; border: 1px solid #1a1a3e; }
        .card h3 { color: #00d4ff; margin-bottom: 15px; font-size: 1.1em; }
        .card p { color: #888; font-size: 0.9em; margin-bottom: 10px; }
        .input-group { display: flex; gap: 10px; flex-wrap: wrap; }
        .input-group input, .input-group textarea { flex: 1; padding: 10px 15px; border-radius: 8px; border: 1px solid #1a1a3e; background: #0a0a15; color: #fff; font-size: 14px; min-width: 150px; }
        .input-group textarea { min-height: 80px; resize: vertical; font-family: monospace; }
        .btn { padding: 10px 25px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; transition: all 0.3s; }
        .btn-primary { background: linear-gradient(135deg, #00d4ff, #7b2ffc); color: #fff; }
        .btn-primary:hover { transform: scale(1.03); box-shadow: 0 0 20px rgba(0,212,255,0.2); }
        .btn-success { background: #00ff8833; color: #00ff88; border: 1px solid #00ff8844; }
        .btn-success:hover { background: #00ff8844; }
        .btn-danger { background: #ff444433; color: #ff4444; border: 1px solid #ff444444; }
        .btn-danger:hover { background: #ff444455; }
        .btn-secondary { background: #2a2a4a; color: #fff; }
        .btn-secondary:hover { background: #3a3a5a; }
        .result-box { background: #0a0a15; padding: 15px; border-radius: 10px; margin-top: 10px; border: 1px solid #1a1a3e; color: #00ff88; font-family: monospace; font-size: 0.85em; overflow-x: auto; white-space: pre-wrap; max-height: 300px; overflow-y: auto; }
        .result-box.error { color: #ff4444; }
        .result-box.info { color: #00d4ff; }
        .stat { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.8em; }
        .stat-open { background: #00ff8822; color: #00ff88; border: 1px solid #00ff8844; }
        .stat-closed { background: #ff444422; color: #ff4444; border: 1px solid #ff444444; }
        .stat-filtered { background: #ffaa0022; color: #ffaa00; border: 1px solid #ffaa0044; }
        .footer { text-align: center; padding: 30px 0; color: #444; font-size: 0.8em; border-top: 1px solid #1a1a3e; margin-top: 30px; }
        .quick-btns { display: flex; gap: 8px; flex-wrap: wrap; margin: 10px 0; }
        .quick-btn { padding: 4px 12px; background: #0a0a15; border: 1px solid #1a1a3e; border-radius: 15px; color: #888; cursor: pointer; font-size: 0.8em; transition: all 0.2s; }
        .quick-btn:hover { border-color: #00d4ff; color: #00d4ff; }
        @media (max-width: 768px) { .grid-3 { grid-template-columns: 1fr; } }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #0a0a15; }
        ::-webkit-scrollbar-thumb { background: #1a1a3e; border-radius: 3px; }
        .tabs { display: flex; gap: 5px; flex-wrap: wrap; margin-bottom: 15px; }
        .tab { padding: 8px 18px; background: #0a0a15; border: 1px solid #1a1a3e; border-radius: 8px 8px 0 0; cursor: pointer; color: #888; transition: all 0.3s; }
        .tab.active { background: #1a1a3e; color: #00d4ff; border-bottom: 2px solid #00d4ff; }
        .tab:hover { color: #fff; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .badge { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 0.7em; background: #00d4ff22; color: #00d4ff; border: 1px solid #00d4ff44; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔧 Network Tools</h1>
            <p>أدوات متكاملة لفحص الشبكات، تحليل SNI، فك التشفير، والبحث عن المستخدمين</p>
        </div>

        <!-- Tabs -->
        <div class="tabs">
            <div class="tab active" onclick="switchTab('scan')">🔍 فحص الشبكة</div>
            <div class="tab" onclick="switchTab('sni')">💡 توصيات SNI</div>
            <div class="tab" onclick="switchTab('crypto')">🔐 تشفير/فك</div>
            <div class="tab" onclick="switchTab('osint')">👤 بحث مستخدم</div>
            <div class="tab" onclick="switchTab('speed')">⚡ سرعة النت</div>
            <div class="tab" onclick="switchTab('history')">📋 السجل</div>
        </div>

        <!-- Tab: Scan -->
        <div id="tab-scan" class="tab-content active">
            <div class="card">
                <h3>🎯 فحص نطاق أو IP</h3>
                <div class="input-group">
                    <input type="text" id="targetInput" placeholder="مثل stc.com.sa" value="stc.com.sa">
                    <button class="btn btn-primary" onclick="startScan()">🚀 فحص</button>
                    <button class="btn btn-secondary" onclick="clearResults()">🗑️ مسح</button>
                </div>
                <div class="quick-btns">
                    <span class="quick-btn" onclick="setTarget('stc.com.sa')">stc.com.sa</span>
                    <span class="quick-btn" onclick="setTarget('mobily.com.sa')">mobily.com.sa</span>
                    <span class="quick-btn" onclick="setTarget('zain.com.sa')">zain.com.sa</span>
                    <span class="quick-btn" onclick="setTarget('botgateway.stc.com.sa')">botgateway</span>
                    <span class="quick-btn" onclick="setTarget('cloud.stc.com.sa')">cloud.stc</span>
                </div>
            </div>
            <div id="loading" style="display:none;text-align:center;padding:30px;">
                <div style="display:inline-block;width:40px;height:40px;border:3px solid #1a1a3e;border-top:3px solid #00d4ff;border-radius:50%;animation:spin 1s linear infinite;"></div>
                <p style="color:#888;margin-top:10px;">جاري الفحص...</p>
            </div>
            <div id="results" style="display:none;">
                <div class="card">
                    <h3>📊 النتائج</h3>
                    <div id="summaryResult"></div>
                    <div style="margin-top:10px;">
                        <strong>🔓 المنافذ المفتوحة:</strong> <span id="portsResult">-</span>
                    </div>
                    <div style="margin-top:10px;">
                        <strong>🌐 النطاقات الفرعية:</strong> <span id="subdomainsResult">-</span>
                    </div>
                    <div style="margin-top:10px;">
                        <strong>💡 توصيات SNI:</strong> <span id="sniResult">-</span>
                    </div>
                    <div style="margin-top:10px;">
                        <strong>🔐 SSL:</strong> <span id="sslResult">-</span>
                    </div>
                    <button class="btn btn-success" style="margin-top:15px;" onclick="exportJSON()">📥 تصدير JSON</button>
                    <button class="btn btn-success" style="margin-top:15px;margin-right:10px;" onclick="exportCSV()">📥 تصدير CSV</button>
                </div>
            </div>
        </div>

        <!-- Tab: SNI -->
        <div id="tab-sni" class="tab-content">
            <div class="card">
                <h3>💡 توصيات SNI</h3>
                <p style="color:#888;">قم بفحص نطاق أولاً (من تبويب الفحص) لتظهر التوصيات</p>
                <div id="sniList" style="margin-top:10px;"></div>
            </div>
        </div>

        <!-- Tab: Crypto -->
        <div id="tab-crypto" class="tab-content">
            <div class="grid-3">
                <div class="card">
                    <h3>🔓 فك Base64</h3>
                    <textarea id="decryptInput" style="width:100%;min-height:80px;padding:10px;background:#0a0a15;border:1px solid #1a1a3e;border-radius:8px;color:#fff;font-family:monospace;" placeholder="أدخل النص المشفر..."></textarea>
                    <button class="btn btn-primary" onclick="decryptBase64()" style="margin-top:10px;">🔓 فك</button>
                    <button class="btn btn-secondary" onclick="document.getElementById('decryptInput').value='';document.getElementById('decryptResult').innerHTML='';" style="margin-top:10px;">🗑️ مسح</button>
                    <div id="decryptResult" class="result-box" style="display:none;"></div>
                </div>
                <div class="card">
                    <h3>🔒 تشفير Base64</h3>
                    <textarea id="encryptInput" style="width:100%;min-height:80px;padding:10px;background:#0a0a15;border:1px solid #1a1a3e;border-radius:8px;color:#fff;font-family:monospace;" placeholder="أدخل النص المراد تشفيره..."></textarea>
                    <button class="btn btn-primary" onclick="encryptBase64()" style="margin-top:10px;">🔒 تشفير</button>
                    <button class="btn btn-secondary" onclick="document.getElementById('encryptInput').value='';document.getElementById('encryptResult').innerHTML='';" style="margin-top:10px;">🗑️ مسح</button>
                    <div id="encryptResult" class="result-box" style="display:none;"></div>
                </div>
                <div class="card">
                    <h3>🔐 Hash (MD5/SHA)</h3>
                    <input type="text" id="hashInput" placeholder="أدخل النص" style="width:100%;padding:10px;background:#0a0a15;border:1px solid #1a1a3e;border-radius:8px;color:#fff;">
                    <button class="btn btn-primary" onclick="hashText()" style="margin-top:10px;">🔐 توليد</button>
                    <div id="hashResult" class="result-box" style="display:none;"></div>
                </div>
            </div>
        </div>

        <!-- Tab: OSINT -->
        <div id="tab-osint" class="tab-content">
            <div class="card">
                <h3>👤 البحث عن مستخدم (OSINT)</h3>
                <p style="color:#888;">ابحث عن اسم مستخدم في 50+ موقع ومنصة</p>
                <div class="input-group">
                    <input type="text" id="osintInput" placeholder="أدخل اسم المستخدم">
                    <button class="btn btn-primary" onclick="osintSearch()">🔍 بحث</button>
                    <button class="btn btn-secondary" onclick="document.getElementById('osintResult').innerHTML='';document.getElementById('osintInput').value='';">🗑️ مسح</button>
                </div>
                <div id="osintResult" class="result-box" style="display:none;"></div>
            </div>
        </div>

        <!-- Tab: Speed -->
        <div id="tab-speed" class="tab-content">
            <div class="card">
                <h3>⚡ اختبار سرعة النت</h3>
                <p style="color:#888;">يقيس زمن الاستجابة (Ping) لخوادم مختلفة</p>
                <button class="btn btn-primary" onclick="speedTest()">🚀 اختبار</button>
                <div id="speedResult" class="result-box" style="display:none;"></div>
            </div>
        </div>

        <!-- Tab: History -->
        <div id="tab-history" class="tab-content">
            <div class="card">
                <h3>📋 سجل الفحوصات</h3>
                <div id="historyList" style="max-height:400px;overflow-y:auto;"></div>
                <button class="btn btn-danger" onclick="clearHistory()" style="margin-top:10px;">🗑️ مسح السجل</button>
                <button class="btn btn-success" onclick="exportHistory()" style="margin-top:10px;margin-right:10px;">📥 تصدير السجل</button>
            </div>
        </div>

        <div class="footer">🔒 للأغراض التعليمية والبحثية فقط | تم التطوير بواسطة 🤖</div>
    </div>

    <script>
        let scanResults = null;
        let history = JSON.parse(localStorage.getItem('toolsHistory') || '[]');

        function switchTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelector(`.tab[onclick="switchTab('${tab}')"]`).classList.add('active');
            document.getElementById('tab-' + tab).classList.add('active');
            if (tab === 'history') renderHistory();
            if (tab === 'sni') renderSNI();
        }

        function setTarget(t) {
            document.getElementById('targetInput').value = t;
            startScan();
        }

        function startScan() {
            const target = document.getElementById('targetInput').value.trim();
            if (!target) { alert('الرجاء إدخال نطاق'); return; }
            document.getElementById('loading').style.display = 'block';
            document.getElementById('results').style.display = 'none';
            fetch('/scan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ target: target })
            })
            .then(r => r.json())
            .then(data => {
                document.getElementById('loading').style.display = 'none';
                if (data.error) { alert('❌ ' + data.error); return; }
                scanResults = data;
                history.unshift({ target: data.target, time: data.scan_time, results: data });
                if (history.length > 50) history.pop();
                localStorage.setItem('toolsHistory', JSON.stringify(history));
                displayResults(data);
                document.getElementById('results').style.display = 'block';
                renderHistory();
            })
            .catch(e => {
                document.getElementById('loading').style.display = 'none';
                alert('❌ خطأ: ' + e);
            });
        }

        function displayResults(data) {
            document.getElementById('summaryResult').innerHTML = `
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;">
                    <div style="background:#0a0a15;padding:15px;border-radius:8px;text-align:center;border:1px solid #1a1a3e;">
                        <div style="font-size:1.5em;color:#00d4ff;">${data.main_ip || 'N/A'}</div>
                        <div style="color:#666;font-size:0.8em;">IP الرئيسي</div>
                    </div>
                    <div style="background:#0a0a15;padding:15px;border-radius:8px;text-align:center;border:1px solid #1a1a3e;">
                        <div style="font-size:1.5em;color:#00d4ff;">${data.subdomains_count || 0}</div>
                        <div style="color:#666;font-size:0.8em;">النطاقات الفرعية</div>
                    </div>
                    <div style="background:#0a0a15;padding:15px;border-radius:8px;text-align:center;border:1px solid #1a1a3e;">
                        <div style="font-size:1.5em;color:#00d4ff;">${data.open_ports_count || 0}</div>
                        <div style="color:#666;font-size:0.8em;">منافذ مفتوحة</div>
                    </div>
                    <div style="background:#0a0a15;padding:15px;border-radius:8px;text-align:center;border:1px solid #1a1a3e;">
                        <div style="font-size:1.5em;color:#00d4ff;">${data.sni_count || 0}</div>
                        <div style="color:#666;font-size:0.8em;">توصيات SNI</div>
                    </div>
                </div>
                <div style="margin-top:10px;padding:10px;background:#0a0a15;border-radius:8px;border:1px solid #1a1a3e;">
                    <p><strong>🎯 النطاق:</strong> ${data.target}</p>
                    <p><strong>🏢 المزود:</strong> ${data.org || 'غير معروف'}</p>
                    <p><strong>📍 الموقع:</strong> ${data.location || 'غير معروف'}</p>
                    <p><strong>📌 الوقت:</strong> ${data.scan_time || 'N/A'}</p>
                </div>
            `;
            document.getElementById('portsResult').innerHTML = data.open_ports && data.open_ports.length > 0 ?
                data.open_ports.map(p => `<span class="stat stat-open">${p.port} (${p.service})</span>`).join(' ') :
                'لا توجد منافذ مفتوحة';
            document.getElementById('subdomainsResult').innerHTML = data.subdomains && data.subdomains.length > 0 ?
                data.subdomains.slice(0, 20).join('، ') + (data.subdomains.length > 20 ? ` ... و ${data.subdomains.length - 20} نطاق` : '') :
                'لا توجد نطاقات فرعية';
            document.getElementById('sniResult').innerHTML = data.sni_recommendations && data.sni_recommendations.length > 0 ?
                data.sni_recommendations.slice(0, 10).map(i => `<span class="badge">${i.domain}</span>`).join(' ') :
                'لا توجد توصيات';
            document.getElementById('sslResult').innerHTML = data.ssl_info ?
                `الجهة: ${data.ssl_info.subject || 'N/A'} | صالحة حتى: ${data.ssl_info.notAfter || 'N/A'}` :
                'لا توجد معلومات SSL';
            renderSNI();
        }

        function renderSNI() {
            const container = document.getElementById('sniList');
            if (!scanResults || !scanResults.sni_recommendations || scanResults.sni_recommendations.length === 0) {
                container.innerHTML = '<p style="color:#666;">قم بفحص نطاق أولاً</p>';
                return;
            }
            container.innerHTML = scanResults.sni_recommendations.map(item =>
                `<div style="padding:8px 12px;background:#0a0a15;border-radius:6px;margin:5px 0;border-left:3px solid #7b2ffc;">
                    <strong>${item.domain}</strong> <span style="color:#666;font-size:0.8em;">[${item.type}]</span>
                </div>`
            ).join('');
        }

        function renderHistory() {
            const container = document.getElementById('historyList');
            if (history.length === 0) {
                container.innerHTML = '<p style="color:#666;text-align:center;padding:20px;">لا توجد فحوصات سابقة</p>';
                return;
            }
            container.innerHTML = history.map((item, index) =>
                `<div style="padding:10px 15px;background:#0a0a15;border-radius:8px;margin:5px 0;border:1px solid #1a1a3e;display:flex;justify-content:space-between;align-items:center;">
                    <div><strong style="color:#00d4ff;">${item.target}</strong> <span style="color:#666;font-size:0.8em;">${item.time}</span></div>
                    <div><span class="badge">${item.results?.open_ports_count || 0} منفذ</span>
                    <button class="btn btn-secondary" style="padding:2px 10px;font-size:0.7em;" onclick="loadHistory(${index})">📂 فتح</button></div>
                </div>`
            ).join('');
        }

        function loadHistory(index) {
            const item = history[index];
            if (item && item.results) {
                document.getElementById('targetInput').value = item.target;
                displayResults(item.results);
                scanResults = item.results;
                document.getElementById('results').style.display = 'block';
                switchTab('scan');
            }
        }

        function clearHistory() {
            if (confirm('مسح السجل؟')) {
                history = [];
                localStorage.setItem('toolsHistory', JSON.stringify(history));
                renderHistory();
            }
        }

        function clearResults() {
            document.getElementById('results').style.display = 'none';
            scanResults = null;
        }

        function exportJSON() {
            if (!scanResults) { alert('لا توجد نتائج للتصدير'); return; }
            const blob = new Blob([JSON.stringify(scanResults, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `scan_${scanResults.target}_${new Date().toISOString().slice(0,10)}.json`;
            a.click();
            URL.revokeObjectURL(url);
        }

        function exportCSV() {
            if (!scanResults) { alert('لا توجد نتائج للتصدير'); return; }
            const rows = [
                ['النطاق', scanResults.target],
                ['IP الرئيسي', scanResults.main_ip || ''],
                ['المزود', scanResults.org || ''],
                ['الموقع', scanResults.location || ''],
                ['عدد النطاقات الفرعية', scanResults.subdomains_count || 0],
                ['عدد المنافذ المفتوحة', scanResults.open_ports_count || 0],
                ['توصيات SNI', (scanResults.sni_recommendations || []).map(i => i.domain).join(', ')]
            ];
            let csv = rows.map(r => r.join(',')).join('\\n');
            const blob = new Blob(['\\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `scan_${scanResults.target}_${new Date().toISOString().slice(0,10)}.csv`;
            a.click();
            URL.revokeObjectURL(url);
        }

        function exportHistory() {
            if (history.length === 0) { alert('السجل فارغ'); return; }
            const blob = new Blob([JSON.stringify(history, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `history_${new Date().toISOString().slice(0,10)}.json`;
            a.click();
            URL.revokeObjectURL(url);
        }

        // Crypto
        function decryptBase64() {
            const input = document.getElementById('decryptInput').value.trim();
            if (!input) { alert('أدخل نص مشفر'); return; }
            try {
                const decoded = atob(input);
                document.getElementById('decryptResult').style.display = 'block';
                document.getElementById('decryptResult').className = 'result-box';
                document.getElementById('decryptResult').textContent = decoded;
            } catch(e) {
                document.getElementById('decryptResult').style.display = 'block';
                document.getElementById('decryptResult').className = 'result-box error';
                document.getElementById('decryptResult').textContent = '❌ خطأ: النص غير صالح لـ Base64';
            }
        }

        function encryptBase64() {
            const input = document.getElementById('encryptInput').value.trim();
            if (!input) { alert('أدخل نص للتشفير'); return; }
            try {
                const encoded = btoa(input);
                document.getElementById('encryptResult').style.display = 'block';
                document.getElementById('encryptResult').className = 'result-box';
                document.getElementById('encryptResult').textContent = encoded;
            } catch(e) {
                document.getElementById('encryptResult').style.display = 'block';
                document.getElementById('encryptResult').className = 'result-box error';
                document.getElementById('encryptResult').textContent = '❌ خطأ: النص يحتوي على أحرف غير مدعومة';
            }
        }

        function hashText() {
            const input = document.getElementById('hashInput').value.trim();
            if (!input) { alert('أدخل نص'); return; }
            const md5 = CryptoJS.MD5(input).toString();
            const sha1 = CryptoJS.SHA1(input).toString();
            const sha256 = CryptoJS.SHA256(input).toString();
            document.getElementById('hashResult').style.display = 'block';
            document.getElementById('hashResult').className = 'result-box';
            document.getElementById('hashResult').innerHTML = `MD5: ${md5}\\nSHA1: ${sha1}\\nSHA256: ${sha256}`;
        }

        // OSINT
        function osintSearch() {
            const username = document.getElementById('osintInput').value.trim();
            if (!username) { alert('أدخل اسم مستخدم'); return; }
            document.getElementById('osintResult').style.display = 'block';
            document.getElementById('osintResult').className = 'result-box';
            document.getElementById('osintResult').textContent = '⏳ جاري البحث...';
            fetch('/osint?username=' + encodeURIComponent(username))
                .then(r => r.json())
                .then(data => {
                    document.getElementById('osintResult').className = 'result-box';
                    if (data.error) {
                        document.getElementById('osintResult').textContent = '❌ ' + data.error;
                        return;
                    }
                    let text = '✅ نتائج البحث عن: ' + username + '\\n\\n';
                    if (data.results && data.results.length > 0) {
                        for (const r of data.results) {
                            text += `📌 ${r.site}: ${r.url}\\n`;
                        }
                    } else {
                        text += '❌ لم يتم العثور على نتائج';
                    }
                    document.getElementById('osintResult').textContent = text;
                })
                .catch(e => {
                    document.getElementById('osintResult').className = 'result-box error';
                    document.getElementById('osintResult').textContent = '❌ خطأ: ' + e;
                });
        }

        // Speed Test
        function speedTest() {
            document.getElementById('speedResult').style.display = 'block';
            document.getElementById('speedResult').className = 'result-box';
            document.getElementById('speedResult').textContent = '⏳ جاري اختبار السرعة...';
            fetch('/speed')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('speedResult').className = 'result-box';
                    if (data.error) {
                        document.getElementById('speedResult').textContent = '❌ ' + data.error;
                        return;
                    }
                    let text = '⚡ نتائج اختبار السرعة\\n\\n';
                    for (const [server, time] of Object.entries(data.results)) {
                        text += `🌐 ${server}: ${time}ms\\n`;
                    }
                    text += `\\n📊 المتوسط: ${data.average || 0}ms`;
                    document.getElementById('speedResult').textContent = text;
                })
                .catch(e => {
                    document.getElementById('speedResult').className = 'result-box error';
                    document.getElementById('speedResult').textContent = '❌ خطأ: ' + e;
                });
        }

        // Load CryptoJS for hashing
        const cryptoScript = document.createElement('script');
        cryptoScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.1.1/crypto-js.min.js';
        document.head.appendChild(cryptoScript);
    </script>
</body>
</html>
'''

# ============================================
# BACKEND FUNCTIONS
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
            return {'org': data.get('org', 'غير معروف'), 'city': data.get('city', 'غير معروف'), 'country': data.get('country', 'غير معروف')}
    except:
        pass
    return {'org': 'غير معروف', 'city': 'غير معروف', 'country': 'غير معروف'}

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
            services = {21:'FTP',22:'SSH',23:'Telnet',25:'SMTP',53:'DNS',80:'HTTP',110:'POP3',143:'IMAP',443:'HTTPS',445:'SMB',465:'SMTPS',587:'SMTP',993:'IMAPS',995:'POP3S',1433:'MSSQL',3306:'MySQL',3389:'RDP',5432:'PostgreSQL',6379:'Redis',8080:'HTTP-Alt',8443:'HTTPS-Alt',8888:'HTTP-Alt'}
            return {'port': port, 'service': services.get(port, f'Port-{port}'), 'status': 'open'}
    except:
        pass
    return None

def scan_ports(ip, timeout=2):
    ports = [21,22,23,25,53,80,110,143,443,445,465,587,993,995,1433,3306,3389,5432,6379,8080,8443,8888]
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
                    return {'subject': subject.get('commonName', 'N/A'), 'issuer': issuer.get('commonName', 'N/A'), 'notAfter': cert.get('notAfter', 'N/A'), 'san_count': len(sans)}
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
        for san in ssl_info.get('sans', []):
            if san not in seen and san.endswith(domain):
                recommendations.append({'domain': san, 'type': 'نطاق بديل (SSL)'})
                seen.add(san)
    return recommendations[:30]

# ============================================
# ROUTES
# ============================================

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/scan', methods=['POST'])
def scan():
    data = request.get_json()
    target = data.get('target', '').strip()
    if not target:
        return jsonify({'error': 'الرجاء إدخال نطاق'})
    try:
        ip = resolve_domain(target)
        if not ip:
            try:
                socket.inet_aton(target)
                ip = target
            except:
                return jsonify({'error': 'فشل في حل النطاق'})
        ip_info = get_ip_info(ip)
        subdomains = find_subdomains(target)
        timeout = int(data.get('timeout', 3))
        open_ports = scan_ports(ip, timeout)
        ssl_info = None
        if any(p['port'] == 443 for p in open_ports):
            ssl_info = analyze_ssl(ip)
        sni = generate_sni_recommendations(target, subdomains, ssl_info)
        result = {
            'target': target,
            'main_ip': ip,
            'org': ip_info.get('org', 'غير معروف'),
            'location': f"{ip_info.get('city', 'غير معروف')}, {ip_info.get('country', 'غير معروف')}",
            'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'subdomains_count': len(subdomains),
            'open_ports_count': len(open_ports),
            'sni_count': len(sni),
            'subdomains': subdomains,
            'open_ports': open_ports,
            'ssl_info': ssl_info,
            'sni_recommendations': sni
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/osint')
def osint():
    username = request.args.get('username', '').strip()
    if not username:
        return jsonify({'error': 'الرجاء إدخال اسم مستخدم'})
    sites = [
        {'site': 'GitHub', 'url': f'https://github.com/{username}'},
        {'site': 'Twitter', 'url': f'https://twitter.com/{username}'},
        {'site': 'Instagram', 'url': f'https://instagram.com/{username}'},
        {'site': 'Facebook', 'url': f'https://facebook.com/{username}'},
        {'site': 'YouTube', 'url': f'https://youtube.com/@{username}'},
        {'site': 'TikTok', 'url': f'https://tiktok.com/@{username}'},
        {'site': 'Reddit', 'url': f'https://reddit.com/user/{username}'},
        {'site': 'Snapchat', 'url': f'https://snapchat.com/add/{username}'},
        {'site': 'Telegram', 'url': f'https://t.me/{username}'},
        {'site': 'WhatsApp', 'url': f'https://wa.me/{username}'},
    ]
    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(check_site, site['url']): site for site in sites}
        for future in as_completed(futures):
            site = futures[future]
            try:
                status = future.result()
                if status:
                    results.append({'site': site['site'], 'url': site['url']})
            except:
                pass
    return jsonify({'results': results})

def check_site(url):
    try:
        r = requests.get(url, timeout=3, allow_redirects=True)
        return r.status_code == 200
    except:
        return False

@app.route('/speed')
def speed():
    servers = {'Google': '8.8.8.8', 'Cloudflare': '1.1.1.1', 'Quad9': '9.9.9.9', 'OpenDNS': '208.67.222.222'}
    results = {}
    for name, ip in servers.items():
        try:
            start = time.time()
            socket.create_connection((ip, 53), timeout=3)
            results[name] = int((time.time() - start) * 1000)
        except:
            results[name] = '✖️'
    avg = [v for v in results.values() if isinstance(v, int)]
    return jsonify({'results': results, 'average': sum(avg)//len(avg) if avg else 0})

# ============================================
# RUN
# ============================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Running on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
