#!/usr/bin/env python3
"""
LightMon Setup Wizard
Runs on port 7777, generates all configs, then launches the full stack.
"""

import os, json, subprocess, socket, ipaddress, re, threading, time, shutil
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

BASE_DIR = Path(__file__).parent.parent.resolve()
CONFIG_FILE = BASE_DIR / ".wizard_config.json"

# ─── HTML UI ──────────────────────────────────────────────────────────────────
HTML = r"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LightMon Setup Wizard</title>
<style>
  :root {
    --bg: #0f1117; --card: #1a1d27; --border: #2a2d3e;
    --accent: #6366f1; --accent2: #22d3ee; --green: #10b981;
    --red: #ef4444; --yellow: #f59e0b; --text: #e2e8f0; --muted: #64748b;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', system-ui, sans-serif; min-height: 100vh; }

  .topbar { background: var(--card); border-bottom: 1px solid var(--border); padding: 16px 32px; display: flex; align-items: center; gap: 12px; }
  .topbar .logo { font-size: 22px; font-weight: 800; background: linear-gradient(135deg, var(--accent), var(--accent2)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  .topbar .subtitle { color: var(--muted); font-size: 13px; }

  .container { max-width: 860px; margin: 0 auto; padding: 40px 24px; }

  /* Steps nav */
  .steps { display: flex; gap: 0; margin-bottom: 40px; }
  .step { flex: 1; position: relative; }
  .step-inner { display: flex; flex-direction: column; align-items: center; gap: 8px; }
  .step-circle { width: 36px; height: 36px; border-radius: 50%; background: var(--border); border: 2px solid var(--border); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px; transition: all .3s; z-index: 1; position: relative; }
  .step.active .step-circle { background: var(--accent); border-color: var(--accent); color: #fff; }
  .step.done .step-circle { background: var(--green); border-color: var(--green); color: #fff; }
  .step-label { font-size: 11px; color: var(--muted); text-align: center; }
  .step.active .step-label { color: var(--text); }
  .step::after { content: ''; position: absolute; top: 18px; left: 50%; width: 100%; height: 2px; background: var(--border); z-index: 0; }
  .step:last-child::after { display: none; }
  .step.done::after { background: var(--green); }

  /* Cards */
  .card { background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 32px; margin-bottom: 24px; }
  .card-title { font-size: 20px; font-weight: 700; margin-bottom: 6px; }
  .card-desc { color: var(--muted); font-size: 14px; margin-bottom: 28px; line-height: 1.6; }

  /* Form */
  .form-group { margin-bottom: 20px; }
  .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  label { display: block; font-size: 13px; font-weight: 600; color: var(--muted); margin-bottom: 6px; text-transform: uppercase; letter-spacing: .5px; }
  input, select, textarea {
    width: 100%; padding: 11px 14px; background: var(--bg); border: 1px solid var(--border);
    border-radius: 8px; color: var(--text); font-size: 14px; transition: border .2s;
    outline: none;
  }
  input:focus, select:focus, textarea:focus { border-color: var(--accent); }
  input.error { border-color: var(--red); }
  .hint { font-size: 12px; color: var(--muted); margin-top: 5px; }
  .hint.ok { color: var(--green); }
  .hint.err { color: var(--red); }

  /* Toggle */
  .toggle-row { display: flex; align-items: center; justify-content: space-between; padding: 14px 0; border-bottom: 1px solid var(--border); }
  .toggle-row:last-child { border-bottom: none; }
  .toggle-info .toggle-title { font-weight: 600; font-size: 14px; }
  .toggle-info .toggle-desc { font-size: 12px; color: var(--muted); margin-top: 2px; }
  .toggle { position: relative; width: 44px; height: 24px; }
  .toggle input { opacity: 0; width: 0; height: 0; }
  .slider { position: absolute; inset: 0; background: var(--border); border-radius: 24px; cursor: pointer; transition: .3s; }
  .slider:before { content: ''; position: absolute; width: 18px; height: 18px; left: 3px; bottom: 3px; background: #fff; border-radius: 50%; transition: .3s; }
  input:checked + .slider { background: var(--accent); }
  input:checked + .slider:before { transform: translateX(20px); }

  /* Section expander */
  .section { border: 1px solid var(--border); border-radius: 12px; overflow: hidden; margin-bottom: 12px; }
  .section-header { padding: 16px 20px; background: var(--bg); display: flex; align-items: center; justify-content: space-between; cursor: pointer; user-select: none; }
  .section-header:hover { background: #16192280; }
  .section-title { font-weight: 600; font-size: 15px; display: flex; align-items: center; gap: 10px; }
  .badge { font-size: 11px; padding: 2px 8px; border-radius: 20px; background: var(--border); color: var(--muted); font-weight: 600; }
  .badge.enabled { background: #10b98120; color: var(--green); }
  .chevron { transition: transform .3s; font-size: 12px; color: var(--muted); }
  .section-body { padding: 20px; border-top: 1px solid var(--border); display: none; }
  .section-body.open { display: block; }

  /* Buttons */
  .btn-row { display: flex; gap: 12px; justify-content: flex-end; margin-top: 28px; }
  button { padding: 11px 28px; border-radius: 8px; border: none; font-size: 14px; font-weight: 600; cursor: pointer; transition: all .2s; }
  .btn-primary { background: var(--accent); color: #fff; }
  .btn-primary:hover { background: #4f46e5; transform: translateY(-1px); }
  .btn-secondary { background: var(--border); color: var(--text); }
  .btn-secondary:hover { background: #374151; }
  .btn-primary:disabled { opacity: .5; cursor: not-allowed; transform: none; }

  /* Progress / deploy */
  .deploy-log { background: #000; border-radius: 8px; padding: 16px; font-family: monospace; font-size: 13px; height: 320px; overflow-y: auto; }
  .log-line { padding: 2px 0; }
  .log-ok   { color: var(--green); }
  .log-warn { color: var(--yellow); }
  .log-err  { color: var(--red); }
  .log-info { color: var(--accent2); }
  .log-plain { color: #94a3b8; }

  .progress-bar { background: var(--border); border-radius: 8px; height: 8px; overflow: hidden; margin: 16px 0; }
  .progress-fill { height: 100%; background: linear-gradient(90deg, var(--accent), var(--accent2)); border-radius: 8px; transition: width .5s ease; width: 0%; }

  /* Summary cards */
  .summary-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  .summary-item { background: var(--bg); border: 1px solid var(--border); border-radius: 10px; padding: 14px 16px; }
  .summary-item .skey { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: .5px; }
  .summary-item .sval { font-size: 15px; font-weight: 600; margin-top: 4px; word-break: break-all; }

  /* URL links */
  .url-card { background: var(--bg); border: 1px solid var(--accent); border-radius: 10px; padding: 16px 20px; display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
  .url-card .url-label { font-size: 13px; color: var(--muted); }
  .url-card .url-val { font-size: 15px; font-weight: 600; color: var(--accent2); }
  .url-card .url-copy { font-size: 12px; color: var(--muted); cursor: pointer; padding: 4px 10px; border: 1px solid var(--border); border-radius: 6px; }
  .url-card .url-copy:hover { color: var(--text); border-color: var(--accent); }

  /* IP detect */
  .ip-row { display: flex; gap: 10px; }
  .ip-row input { flex: 1; }
  .btn-detect { padding: 11px 16px; background: var(--border); color: var(--text); border-radius: 8px; border: none; cursor: pointer; font-size: 13px; white-space: nowrap; }
  .btn-detect:hover { background: #374151; }

  /* Page visibility */
  .page { display: none; }
  .page.active { display: block; }

  /* Test button */
  .btn-test { padding: 8px 16px; background: transparent; border: 1px solid var(--border); color: var(--muted); border-radius: 6px; font-size: 13px; cursor: pointer; margin-top: 10px; }
  .btn-test:hover { border-color: var(--accent2); color: var(--accent2); }
  .test-result { font-size: 12px; margin-top: 6px; padding: 6px 10px; border-radius: 6px; display: none; }
  .test-result.ok { background: #10b98115; color: var(--green); display: block; }
  .test-result.err { background: #ef444415; color: var(--red); display: block; }
</style>
</head>
<body>

<div class="topbar">
  <div class="logo">⚡ LightMon</div>
  <div class="subtitle">Setup Wizard — Monitoring Stack</div>
</div>

<div class="container">

  <!-- STEPS NAV -->
  <div class="steps" id="stepsNav">
    <div class="step active" id="stepNav1"><div class="step-inner"><div class="step-circle">1</div><div class="step-label">Network</div></div></div>
    <div class="step" id="stepNav2"><div class="step-inner"><div class="step-circle">2</div><div class="step-label">Services</div></div></div>
    <div class="step" id="stepNav3"><div class="step-inner"><div class="step-circle">3</div><div class="step-label">Alerts</div></div></div>
    <div class="step" id="stepNav4"><div class="step-inner"><div class="step-circle">4</div><div class="step-label">Security</div></div></div>
    <div class="step" id="stepNav5"><div class="step-inner"><div class="step-circle">5</div><div class="step-label">Deploy</div></div></div>
  </div>

  <!-- PAGE 1: Network & IPs -->
  <div class="page active" id="page1">
    <div class="card">
      <div class="card-title">🌐 Konfigurasi Jaringan</div>
      <div class="card-desc">Masukkan IP address server ini. Semua komponen (Grafana, Prometheus, Loki) akan dikonfigurasi otomatis berdasarkan IP ini.</div>

      <div class="form-group">
        <label>IP Address Server Ini</label>
        <div class="ip-row">
          <input type="text" id="serverIp" placeholder="contoh: 192.168.1.100" oninput="validateIp(this)">
          <button class="btn-detect" onclick="detectIp()">🔍 Auto Detect</button>
        </div>
        <div class="hint" id="ipHint">IP yang akan digunakan untuk mengakses semua layanan monitoring</div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>Port Grafana</label>
          <input type="number" id="portGrafana" value="3000" min="1024" max="65535">
          <div class="hint">Default: 3000</div>
        </div>
        <div class="form-group">
          <label>Port Prometheus</label>
          <input type="number" id="portPrometheus" value="9090" min="1024" max="65535">
          <div class="hint">Default: 9090</div>
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>Port Loki</label>
          <input type="number" id="portLoki" value="3100" min="1024" max="65535">
          <div class="hint">Default: 3100</div>
        </div>
        <div class="form-group">
          <label>Port Alertmanager</label>
          <input type="number" id="portAlertmanager" value="9093" min="1024" max="65535">
          <div class="hint">Default: 9093</div>
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>Port Dashboard (Nginx)</label>
          <input type="number" id="portNginx" value="80" min="1" max="65535">
          <div class="hint">Port utama akses web</div>
        </div>
        <div class="form-group">
          <label>Port Backend API</label>
          <input type="number" id="portBackend" value="8000" min="1024" max="65535">
          <div class="hint">Default: 8000</div>
        </div>
      </div>

      <div class="btn-row">
        <button class="btn-primary" onclick="goTo(2)">Lanjut →</button>
      </div>
    </div>
  </div>

  <!-- PAGE 2: Services -->
  <div class="page" id="page2">
    <div class="card">
      <div class="card-title">⚙️ Konfigurasi Services</div>
      <div class="card-desc">Pilih komponen yang ingin diaktifkan dan versi yang akan digunakan.</div>

      <div class="toggle-row">
        <div class="toggle-info">
          <div class="toggle-title">📊 Grafana</div>
          <div class="toggle-desc">Dashboard visualisasi metrics dan log. Versi terbaru (latest).</div>
        </div>
        <label class="toggle"><input type="checkbox" id="enableGrafana" checked disabled><span class="slider"></span></label>
      </div>
      <div class="toggle-row">
        <div class="toggle-info">
          <div class="toggle-title">🔥 Prometheus</div>
          <div class="toggle-desc">Pengumpulan dan penyimpanan metrics. Versi terbaru (latest).</div>
        </div>
        <label class="toggle"><input type="checkbox" id="enablePrometheus" checked disabled><span class="slider"></span></label>
      </div>
      <div class="toggle-row">
        <div class="toggle-info">
          <div class="toggle-title">📝 Loki + Promtail</div>
          <div class="toggle-desc">Agregasi log sistem (syslog, auth.log, journald, dpkg).</div>
        </div>
        <label class="toggle"><input type="checkbox" id="enableLoki" checked><span class="slider"></span></label>
      </div>
      <div class="toggle-row">
        <div class="toggle-info">
          <div class="toggle-title">🔔 Alertmanager</div>
          <div class="toggle-desc">Routing alert ke Telegram/Slack/Email.</div>
        </div>
        <label class="toggle"><input type="checkbox" id="enableAlertmanager" checked><span class="slider"></span></label>
      </div>
      <div class="toggle-row">
        <div class="toggle-info">
          <div class="toggle-title">🖥️ Node Exporter</div>
          <div class="toggle-desc">Metrics CPU, RAM, Disk, Network dari sistem host.</div>
        </div>
        <label class="toggle"><input type="checkbox" id="enableNodeExporter" checked><span class="slider"></span></label>
      </div>
      <div class="toggle-row">
        <div class="toggle-info">
          <div class="toggle-title">🐳 cAdvisor</div>
          <div class="toggle-desc">Metrics resource per container Docker.</div>
        </div>
        <label class="toggle"><input type="checkbox" id="enableCadvisor" checked><span class="slider"></span></label>
      </div>

      <div class="btn-row">
        <button class="btn-secondary" onclick="goTo(1)">← Kembali</button>
        <button class="btn-primary" onclick="goTo(3)">Lanjut →</button>
      </div>
    </div>
  </div>

  <!-- PAGE 3: Alerting -->
  <div class="page" id="page3">
    <div class="card">
      <div class="card-title">🔔 Konfigurasi Notifikasi Alert</div>
      <div class="card-desc">Aktifkan minimal satu channel notifikasi. Semua konfigurasi Alertmanager akan digenerate otomatis.</div>

      <!-- Telegram -->
      <div class="section" id="secTelegram">
        <div class="section-header" onclick="toggleSection('telegram')">
          <div class="section-title">🤖 Telegram Bot <span class="badge" id="badgeTelegram">Nonaktif</span></div>
          <span class="chevron" id="chevTelegram">▼</span>
        </div>
        <div class="section-body" id="bodyTelegram">
          <div class="toggle-row" style="padding-top:0">
            <span style="font-size:13px;color:var(--muted)">Aktifkan Telegram</span>
            <label class="toggle"><input type="checkbox" id="enableTelegram" onchange="updateBadge('Telegram')"><span class="slider"></span></label>
          </div>
          <div class="form-group" style="margin-top:14px">
            <label>Bot Token</label>
            <input type="text" id="telegramToken" placeholder="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz">
            <div class="hint">Dapatkan dari @BotFather → /newbot</div>
          </div>
          <div class="form-group">
            <label>Chat ID</label>
            <input type="text" id="telegramChatId" placeholder="-1001234567890">
            <div class="hint">Kirim pesan ke bot, lalu buka: https://api.telegram.org/bot&lt;TOKEN&gt;/getUpdates</div>
          </div>
          <button class="btn-test" onclick="testTelegram()">🧪 Test Kirim Pesan</button>
          <div class="test-result" id="testTelegramResult"></div>
        </div>
      </div>

      <!-- Slack -->
      <div class="section" id="secSlack">
        <div class="section-header" onclick="toggleSection('slack')">
          <div class="section-title">💬 Slack <span class="badge" id="badgeSlack">Nonaktif</span></div>
          <span class="chevron" id="chevSlack">▼</span>
        </div>
        <div class="section-body" id="bodySlack">
          <div class="toggle-row" style="padding-top:0">
            <span style="font-size:13px;color:var(--muted)">Aktifkan Slack</span>
            <label class="toggle"><input type="checkbox" id="enableSlack" onchange="updateBadge('Slack')"><span class="slider"></span></label>
          </div>
          <div class="form-group" style="margin-top:14px">
            <label>Webhook URL</label>
            <input type="text" id="slackWebhook" placeholder="https://hooks.slack.com/services/...">
            <div class="hint">Buat di: api.slack.com/apps → Incoming Webhooks</div>
          </div>
          <div class="form-group">
            <label>Channel</label>
            <input type="text" id="slackChannel" placeholder="#monitoring-alerts" value="#monitoring-alerts">
          </div>
          <button class="btn-test" onclick="testSlack()">🧪 Test Kirim Pesan</button>
          <div class="test-result" id="testSlackResult"></div>
        </div>
      </div>

      <!-- Email -->
      <div class="section" id="secEmail">
        <div class="section-header" onclick="toggleSection('email')">
          <div class="section-title">📧 Email SMTP <span class="badge" id="badgeEmail">Nonaktif</span></div>
          <span class="chevron" id="chevEmail">▼</span>
        </div>
        <div class="section-body" id="bodyEmail">
          <div class="toggle-row" style="padding-top:0">
            <span style="font-size:13px;color:var(--muted)">Aktifkan Email</span>
            <label class="toggle"><input type="checkbox" id="enableEmail" onchange="updateBadge('Email')"><span class="slider"></span></label>
          </div>
          <div class="form-row" style="margin-top:14px">
            <div class="form-group">
              <label>SMTP Host</label>
              <input type="text" id="smtpHost" placeholder="smtp.gmail.com">
            </div>
            <div class="form-group">
              <label>SMTP Port</label>
              <input type="number" id="smtpPort" value="587">
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Email Pengirim</label>
              <input type="email" id="smtpFrom" placeholder="monitor@domain.com">
            </div>
            <div class="form-group">
              <label>Email Tujuan Alert</label>
              <input type="email" id="smtpTo" placeholder="admin@domain.com">
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Username SMTP</label>
              <input type="text" id="smtpUser" placeholder="monitor@domain.com">
            </div>
            <div class="form-group">
              <label>Password SMTP</label>
              <input type="password" id="smtpPass" placeholder="app password">
            </div>
          </div>
        </div>
      </div>

      <div class="btn-row">
        <button class="btn-secondary" onclick="goTo(2)">← Kembali</button>
        <button class="btn-primary" onclick="goTo(4)">Lanjut →</button>
      </div>
    </div>
  </div>

  <!-- PAGE 4: Security -->
  <div class="page" id="page4">
    <div class="card">
      <div class="card-title">🔐 Keamanan & Akses</div>
      <div class="card-desc">Atur kredensial untuk Grafana. Secret key akan di-generate otomatis jika dikosongkan.</div>

      <div class="form-row">
        <div class="form-group">
          <label>Username Grafana</label>
          <input type="text" id="grafanaUser" value="admin">
        </div>
        <div class="form-group">
          <label>Password Grafana</label>
          <input type="password" id="grafanaPass" placeholder="Minimal 8 karakter" oninput="checkPass(this)">
          <div class="hint" id="passHint">Gunakan password yang kuat</div>
        </div>
      </div>

      <div class="form-group">
        <label>Retensi Data Prometheus</label>
        <select id="retentionDays">
          <option value="7d">7 hari</option>
          <option value="15d">15 hari</option>
          <option value="30d" selected>30 hari</option>
          <option value="60d">60 hari</option>
          <option value="90d">90 hari</option>
        </select>
        <div class="hint">Semakin lama, semakin besar storage yang dibutuhkan</div>
      </div>

      <div class="form-group">
        <label>Retensi Log Loki</label>
        <select id="retentionLoki">
          <option value="72h">3 hari</option>
          <option value="168h">7 hari</option>
          <option value="720h" selected>30 hari</option>
          <option value="2160h">90 hari</option>
        </select>
      </div>

      <div class="form-group">
        <label>Scrape Interval Prometheus</label>
        <select id="scrapeInterval">
          <option value="10s">10 detik (high frequency)</option>
          <option value="15s" selected>15 detik (recommended)</option>
          <option value="30s">30 detik (low resource)</option>
          <option value="60s">60 detik (minimal)</option>
        </select>
      </div>

      <div class="btn-row">
        <button class="btn-secondary" onclick="goTo(3)">← Kembali</button>
        <button class="btn-primary" onclick="goTo(5)">Review & Deploy →</button>
      </div>
    </div>
  </div>

  <!-- PAGE 5: Deploy -->
  <div class="page" id="page5">
    <div class="card" id="reviewCard">
      <div class="card-title">🚀 Review & Deploy</div>
      <div class="card-desc">Periksa konfigurasi sebelum deploy. LightMon akan generate semua file config dan menjalankan stack.</div>

      <div class="summary-grid" id="summaryGrid"></div>

      <div class="btn-row">
        <button class="btn-secondary" onclick="goTo(4)">← Edit</button>
        <button class="btn-primary" id="deployBtn" onclick="startDeploy()">🚀 Deploy Sekarang</button>
      </div>
    </div>

    <div class="card" id="deployCard" style="display:none">
      <div class="card-title">⚙️ Deploying LightMon...</div>
      <div class="progress-bar"><div class="progress-fill" id="progressFill"></div></div>
      <div class="deploy-log" id="deployLog"></div>
    </div>

    <div class="card" id="doneCard" style="display:none">
      <div class="card-title">✅ LightMon Berhasil Dideploy!</div>
      <div class="card-desc" style="margin-bottom:20px">Semua services berjalan. Akses dashboard di bawah ini.</div>
      <div id="urlCards"></div>
      <div style="margin-top:20px;padding:14px;background:var(--bg);border-radius:8px;font-size:13px;color:var(--muted)">
        ⚠️ Ganti password Grafana setelah login pertama: <strong>Profile → Change Password</strong>
      </div>
    </div>
  </div>

</div><!-- /container -->

<script>
let cfg = {};
let currentPage = 1;

// ─── Navigation ───────────────────────────────────────────────────────────────
function goTo(n) {
  if (n > currentPage && !validatePage(currentPage)) return;
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById('page' + n).classList.add('active');
  for (let i = 1; i <= 5; i++) {
    const el = document.getElementById('stepNav' + i);
    el.classList.remove('active', 'done');
    if (i < n) el.classList.add('done');
    else if (i === n) el.classList.add('active');
  }
  currentPage = n;
  if (n === 5) buildSummary();
  window.scrollTo(0, 0);
}

function validatePage(n) {
  if (n === 1) {
    const ip = document.getElementById('serverIp').value.trim();
    if (!isValidIp(ip)) {
      showHint('ipHint', 'IP address tidak valid!', 'err');
      document.getElementById('serverIp').classList.add('error');
      return false;
    }
  }
  if (n === 4) {
    const pass = document.getElementById('grafanaPass').value;
    if (pass && pass.length < 8) {
      document.getElementById('passHint').textContent = 'Password minimal 8 karakter!';
      document.getElementById('passHint').className = 'hint err';
      return false;
    }
  }
  return true;
}

// ─── Sections ─────────────────────────────────────────────────────────────────
function toggleSection(name) {
  const body = document.getElementById('body' + cap(name));
  const chev = document.getElementById('chev' + cap(name));
  body.classList.toggle('open');
  chev.textContent = body.classList.contains('open') ? '▲' : '▼';
}
function cap(s) { return s.charAt(0).toUpperCase() + s.slice(1); }

function updateBadge(name) {
  const enabled = document.getElementById('enable' + name).checked;
  const badge = document.getElementById('badge' + name);
  badge.textContent = enabled ? 'Aktif' : 'Nonaktif';
  badge.className = 'badge' + (enabled ? ' enabled' : '');
}

// ─── IP Validation ────────────────────────────────────────────────────────────
function isValidIp(ip) {
  return /^(\d{1,3}\.){3}\d{1,3}$/.test(ip) &&
    ip.split('.').every(n => parseInt(n) <= 255);
}
function validateIp(el) {
  const valid = isValidIp(el.value.trim());
  el.classList.toggle('error', !valid && el.value.length > 0);
  showHint('ipHint', valid ? '✓ IP valid' : 'IP address tidak valid', valid ? 'ok' : (el.value.length > 0 ? 'err' : ''));
}
function showHint(id, msg, cls) {
  const el = document.getElementById(id);
  el.textContent = msg;
  el.className = 'hint' + (cls ? ' ' + cls : '');
}
async function detectIp() {
  try {
    const r = await fetch('/api/detect-ip');
    const d = await r.json();
    document.getElementById('serverIp').value = d.ip;
    validateIp(document.getElementById('serverIp'));
  } catch(e) { alert('Gagal detect IP: ' + e); }
}

// ─── Password check ───────────────────────────────────────────────────────────
function checkPass(el) {
  const v = el.value;
  if (!v) { document.getElementById('passHint').textContent = 'Gunakan password yang kuat'; document.getElementById('passHint').className = 'hint'; return; }
  if (v.length < 8) { showHint('passHint','Terlalu pendek (min 8 karakter)','err'); return; }
  if (!/[A-Z]/.test(v)||!/[0-9]/.test(v)) { showHint('passHint','Tambahkan huruf besar dan angka','warn'); return; }
  showHint('passHint','✓ Password kuat','ok');
}

// ─── Test buttons ─────────────────────────────────────────────────────────────
async function testTelegram() {
  const token = document.getElementById('telegramToken').value.trim();
  const chatId = document.getElementById('telegramChatId').value.trim();
  const res = document.getElementById('testTelegramResult');
  if (!token || !chatId) { res.className='test-result err'; res.textContent='Isi token dan chat ID dulu!'; return; }
  try {
    const r = await fetch('/api/test-telegram', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({token, chat_id: chatId}) });
    const d = await r.json();
    res.className = 'test-result ' + (d.ok ? 'ok' : 'err');
    res.textContent = d.ok ? '✓ Pesan terkirim ke Telegram!' : '✗ Gagal: ' + d.error;
  } catch(e) { res.className='test-result err'; res.textContent='Error: '+e; }
}
async function testSlack() {
  const webhook = document.getElementById('slackWebhook').value.trim();
  const res = document.getElementById('testSlackResult');
  if (!webhook) { res.className='test-result err'; res.textContent='Isi Webhook URL dulu!'; return; }
  try {
    const r = await fetch('/api/test-slack', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({webhook}) });
    const d = await r.json();
    res.className = 'test-result ' + (d.ok ? 'ok' : 'err');
    res.textContent = d.ok ? '✓ Pesan terkirim ke Slack!' : '✗ Gagal: ' + d.error;
  } catch(e) { res.className='test-result err'; res.textContent='Error: '+e; }
}

// ─── Summary ──────────────────────────────────────────────────────────────────
function collectConfig() {
  return {
    server_ip: document.getElementById('serverIp').value.trim(),
    port_grafana: +document.getElementById('portGrafana').value,
    port_prometheus: +document.getElementById('portPrometheus').value,
    port_loki: +document.getElementById('portLoki').value,
    port_alertmanager: +document.getElementById('portAlertmanager').value,
    port_nginx: +document.getElementById('portNginx').value,
    port_backend: +document.getElementById('portBackend').value,
    enable_loki: document.getElementById('enableLoki').checked,
    enable_alertmanager: document.getElementById('enableAlertmanager').checked,
    enable_node_exporter: document.getElementById('enableNodeExporter').checked,
    enable_cadvisor: document.getElementById('enableCadvisor').checked,
    enable_telegram: document.getElementById('enableTelegram').checked,
    telegram_token: document.getElementById('telegramToken').value.trim(),
    telegram_chat_id: document.getElementById('telegramChatId').value.trim(),
    enable_slack: document.getElementById('enableSlack').checked,
    slack_webhook: document.getElementById('slackWebhook').value.trim(),
    slack_channel: document.getElementById('slackChannel').value.trim(),
    enable_email: document.getElementById('enableEmail').checked,
    smtp_host: document.getElementById('smtpHost').value.trim(),
    smtp_port: +document.getElementById('smtpPort').value,
    smtp_from: document.getElementById('smtpFrom').value.trim(),
    smtp_to: document.getElementById('smtpTo').value.trim(),
    smtp_user: document.getElementById('smtpUser').value.trim(),
    smtp_pass: document.getElementById('smtpPass').value,
    grafana_user: document.getElementById('grafanaUser').value.trim() || 'admin',
    grafana_pass: document.getElementById('grafanaPass').value || 'lightmon123',
    retention_prometheus: document.getElementById('retentionDays').value,
    retention_loki: document.getElementById('retentionLoki').value,
    scrape_interval: document.getElementById('scrapeInterval').value,
  };
}

function buildSummary() {
  cfg = collectConfig();
  const grid = document.getElementById('summaryGrid');
  const items = [
    ['IP Server', cfg.server_ip],
    ['Grafana', cfg.server_ip + ':' + cfg.port_grafana],
    ['Prometheus', cfg.server_ip + ':' + cfg.port_prometheus],
    ['Loki', cfg.enable_loki ? cfg.server_ip + ':' + cfg.port_loki : 'Nonaktif'],
    ['Alertmanager', cfg.enable_alertmanager ? cfg.server_ip + ':' + cfg.port_alertmanager : 'Nonaktif'],
    ['Telegram Alert', cfg.enable_telegram ? '✓ Aktif' : '✗ Nonaktif'],
    ['Slack Alert', cfg.enable_slack ? '✓ Aktif' : '✗ Nonaktif'],
    ['Email Alert', cfg.enable_email ? '✓ Aktif' : '✗ Nonaktif'],
    ['Grafana User', cfg.grafana_user],
    ['Retensi Prometheus', cfg.retention_prometheus],
    ['Retensi Loki', cfg.retention_loki],
    ['Scrape Interval', cfg.scrape_interval],
  ];
  grid.innerHTML = items.map(([k,v]) => `<div class="summary-item"><div class="skey">${k}</div><div class="sval">${v}</div></div>`).join('');
}

// ─── Deploy ───────────────────────────────────────────────────────────────────
async function startDeploy() {
  document.getElementById('reviewCard').style.display = 'none';
  document.getElementById('deployCard').style.display = 'block';
  document.getElementById('deployBtn').disabled = true;

  const logEl = document.getElementById('deployLog');
  const progEl = document.getElementById('progressFill');

  function addLog(msg, cls='plain') {
    const d = document.createElement('div');
    d.className = 'log-line log-' + cls;
    d.textContent = msg;
    logEl.appendChild(d);
    logEl.scrollTop = logEl.scrollHeight;
  }

  try {
    addLog('[*] Mengirim konfigurasi ke server...', 'info');
    const r = await fetch('/api/deploy', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(cfg)
    });

    const reader = r.body.getReader();
    const decoder = new TextDecoder();
    let progress = 0;

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const text = decoder.decode(value, {stream: true});
        for (const line of text.split('\n')) {
          if (!line.trim()) continue;
          let cls = 'plain';
          if (line.startsWith('[OK]')) cls = 'ok';
          else if (line.startsWith('[ERR]')) cls = 'err';
          else if (line.startsWith('[WARN]')) cls = 'warn';
          else if (line.startsWith('[*]')) cls = 'info';
          addLog(line, cls);
          progress = Math.min(progress + 4, 95);
          progEl.style.width = progress + '%';
        }
      }
    } catch(streamErr) {
      // TypeError/AbortError terjadi saat koneksi ditutup server setelah selesai — ini normal
      console.log('Stream ended:', streamErr.message);
    }

    progEl.style.width = '100%';
    addLog('[OK] Deploy selesai!', 'ok');
    setTimeout(() => showDone(), 1500);
  } catch(e) {
    // Kalau error bukan dari stream reader, baru tampilkan error
    if (e.name !== 'TypeError' && e.name !== 'AbortError') {
      addLog('[ERR] Error: ' + e, 'err');
    } else {
      // Koneksi terputus setelah deploy selesai — anggap sukses
      progEl.style.width = '100%';
      addLog('[OK] Deploy selesai!', 'ok');
      setTimeout(() => showDone(), 1500);
    }
  }
}

function showDone() {
  document.getElementById('deployCard').style.display = 'none';
  document.getElementById('doneCard').style.display = 'block';
  const ip = cfg.server_ip;
  const urls = [
    ['🌐 Dashboard Utama', `http://${ip}:${cfg.port_nginx}/`],
    ['📊 Grafana', `http://${ip}:${cfg.port_nginx}/grafana/  (${cfg.grafana_user} / ${cfg.grafana_pass})`],
    ['🔥 Prometheus', `http://${ip}:${cfg.port_prometheus}/`],
    ['📝 Loki', `http://${ip}:${cfg.port_loki}/ready`],
    ['🔔 Alertmanager', `http://${ip}:${cfg.port_alertmanager}/`],
    ['⚡ Backend API', `http://${ip}:${cfg.port_backend}/docs`],
  ];
  document.getElementById('urlCards').innerHTML = urls.map(([label, url]) => `
    <div class="url-card">
      <div><div class="url-label">${label}</div><div class="url-val">${url}</div></div>
      <span class="url-copy" onclick="navigator.clipboard.writeText('${url.split(' ')[0]}');this.textContent='✓'">Copy</span>
    </div>
  `).join('');
}
</script>
</body>
</html>"""

# ─── HTTP Handler ──────────────────────────────────────────────────────────────
class WizardHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass  # suppress default logs

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/' or path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML.encode())
        elif path == '/api/detect-ip':
            ip = self._get_local_ip()
            self._json({'ip': ip})
        else:
            self._json({'error': 'not found'}, 404)

    def do_POST(self):
        path = urlparse(self.path).path
        body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
        try:
            data = json.loads(body) if body else {}
        except:
            data = {}

        if path == '/api/test-telegram':
            self._test_telegram(data)
        elif path == '/api/test-slack':
            self._test_slack(data)
        elif path == '/api/deploy':
            self._deploy(data)
        else:
            self._json({'error': 'not found'}, 404)

    def _get_local_ip(self):
        """Detect real host IP, skip Docker bridge IPs (172.17/18.x.x)."""
        import subprocess
        
        # Cara 1: ip route get — paling akurat, pakai routing table
        try:
            result = subprocess.run(
                ['ip', 'route', 'get', '8.8.8.8'],
                capture_output=True, text=True, timeout=3
            )
            for token in result.stdout.split():
                if token == 'src':
                    idx = result.stdout.split().index('src')
                    ip = result.stdout.split()[idx + 1]
                    if not ip.startswith('172.'):
                        return ip
        except:
            pass

        # Cara 2: cek semua interface, skip Docker/loopback
        try:
            result = subprocess.run(
                ['ip', '-4', 'addr', 'show'],
                capture_output=True, text=True, timeout=3
            )
            import re
            for line in result.stdout.splitlines():
                m = re.search(r'inet ([\d.]+)/', line)
                if m:
                    ip = m.group(1)
                    if ip == '127.0.0.1':
                        continue
                    if ip.startswith('172.'):
                        continue  # skip Docker bridge
                    return ip
        except:
            pass

        # Cara 3: UDP socket fallback
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
            if not ip.startswith('172.'):
                return ip
        except:
            pass

        return '127.0.0.1'

    def _test_telegram(self, data):
        import urllib.request
        token = data.get('token', '')
        chat_id = data.get('chat_id', '')
        url = f'https://api.telegram.org/bot{token}/sendMessage'
        payload = json.dumps({'chat_id': chat_id, 'text': '✅ LightMon test alert berhasil!'}).encode()
        try:
            req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=10) as r:
                resp = json.loads(r.read())
                if resp.get('ok'):
                    self._json({'ok': True})
                else:
                    self._json({'ok': False, 'error': resp.get('description', 'Unknown')})
        except Exception as e:
            self._json({'ok': False, 'error': str(e)})

    def _test_slack(self, data):
        import urllib.request
        webhook = data.get('webhook', '')
        payload = json.dumps({'text': '✅ LightMon test alert berhasil!'}).encode()
        try:
            req = urllib.request.Request(webhook, data=payload, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=10) as r:
                self._json({'ok': True})
        except Exception as e:
            self._json({'ok': False, 'error': str(e)})

    def _deploy(self, cfg):
        """Stream deploy progress back to client using chunked encoding."""
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Transfer-Encoding', 'chunked')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('X-Accel-Buffering', 'no')
        self.end_headers()

        def emit(msg):
            line = msg + '\n'
            data = line.encode('utf-8')
            chunk = f'{len(data):X}\r\n'.encode() + data + b'\r\n'
            try:
                self.wfile.write(chunk)
                self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass  # Client disconnected — normal saat deploy selesai

        try:
            generator = ConfigGenerator(BASE_DIR, cfg)
            generator.run(emit)
            emit('[DONE] selesai')
        except Exception as e:
            emit(f'[ERR] Exception: {e}')

        try:
            # Kirim terminating chunk
            self.wfile.write(b'0\r\n\r\n')
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass  # Normal — client sudah tutup koneksi

    def _json(self, data, code=200):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


# ─── Config Generator ──────────────────────────────────────────────────────────
class ConfigGenerator:
    def __init__(self, base_dir: Path, cfg: dict):
        self.base = base_dir
        self.cfg = cfg

    def run(self, emit):
        emit('[*] Memulai generate konfigurasi...')
        self._gen_env(emit)
        self._gen_prometheus(emit)
        self._gen_alertmanager(emit)
        self._gen_loki(emit)
        self._gen_promtail(emit)
        self._gen_datasources(emit)
        self._gen_docker_compose(emit)
        self._deploy_stack(emit)
        self._health_check(emit)

    # ── .env ──────────────────────────────────────────────────────────────────
    def _gen_env(self, emit):
        emit('[*] Generating .env ...')
        import secrets
        secret = secrets.token_hex(32)
        c = self.cfg
        content = f"""# Auto-generated by LightMon Wizard
SECRET_KEY={secret}
GRAFANA_USER={c['grafana_user']}
GRAFANA_PASSWORD={c['grafana_pass']}
GRAFANA_PORT={c['port_grafana']}
PROMETHEUS_PORT={c['port_prometheus']}
LOKI_PORT={c['port_loki']}
ALERTMANAGER_PORT={c['port_alertmanager']}
NGINX_PORT={c['port_nginx']}
BACKEND_PORT={c['port_backend']}
SERVER_IP={c['server_ip']}
TELEGRAM_BOT_TOKEN={c.get('telegram_token','')}
TELEGRAM_CHAT_ID={c.get('telegram_chat_id','')}
SLACK_WEBHOOK_URL={c.get('slack_webhook','')}
SLACK_CHANNEL={c.get('slack_channel','#monitoring-alerts')}
SMTP_HOST={c.get('smtp_host','')}
SMTP_PORT={c.get('smtp_port',587)}
SMTP_FROM={c.get('smtp_from','')}
SMTP_TO={c.get('smtp_to','')}
SMTP_USER={c.get('smtp_user','')}
SMTP_PASS={c.get('smtp_pass','')}
"""
        (self.base / '.env').write_text(content)
        emit('[OK] .env digenerate')

    # ── prometheus.yml ────────────────────────────────────────────────────────
    def _gen_prometheus(self, emit):
        emit('[*] Generating prometheus/prometheus.yml ...')
        c = self.cfg
        ip = c['server_ip']
        interval = c['scrape_interval']
        retention = c['retention_prometheus']

        extras = ''
        if c['enable_node_exporter']:
            extras += f"""
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['{ip}:9100']
        labels:
          instance: 'local'
"""
        if c['enable_cadvisor']:
            extras += f"""
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['{ip}:8080']
        labels:
          instance: 'local'
"""
        if c['enable_alertmanager']:
            extras += f"""
  - job_name: 'alertmanager'
    static_configs:
      - targets: ['{ip}:{c["port_alertmanager"]}']
"""

        content = f"""global:
  scrape_interval: {interval}
  evaluation_interval: {interval}
  external_labels:
    monitor: 'lightmon'
    server: '{ip}'

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:{c['port_alertmanager']}']

rule_files:
  - /etc/prometheus/rules/*.yml

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'lightmon-backend'
    static_configs:
      - targets: ['backend:8000']
        labels:
          instance: 'lightmon-backend'
{extras}"""
        (self.base / 'prometheus' / 'prometheus.yml').write_text(content)
        emit('[OK] prometheus.yml digenerate')

    # ── alertmanager.yml ──────────────────────────────────────────────────────
    def _gen_alertmanager(self, emit):
        emit('[*] Generating prometheus/alertmanager.yml ...')
        c = self.cfg
        receivers = []
        routes = []

        # Telegram
        if c['enable_telegram'] and c.get('telegram_token') and c.get('telegram_chat_id'):
            receivers.append(f"""  - name: 'telegram'
    telegram_configs:
      - bot_token: '{c['telegram_token']}'
        chat_id: {c['telegram_chat_id']}
        message: |
          🚨 *{{{{ .GroupLabels.alertname }}}}*
          📊 *Status:* {{{{ .Status | toUpper }}}}
          🖥️ *Instance:* {{{{ .CommonLabels.instance }}}}
          📝 *Detail:* {{{{ .CommonAnnotations.description }}}}
        parse_mode: 'Markdown'
        send_resolved: true""")
            routes.append("    - receiver: 'telegram'\n      group_wait: 10s")

        # Slack
        if c['enable_slack'] and c.get('slack_webhook'):
            channel = c.get('slack_channel', '#monitoring-alerts')
            receivers.append(f"""  - name: 'slack'
    slack_configs:
      - api_url: '{c['slack_webhook']}'
        channel: '{channel}'
        title: '🚨 {{{{ .GroupLabels.alertname }}}}'
        text: |
          *Status:* {{{{ .Status | toUpper }}}}
          *Instance:* {{{{ .CommonLabels.instance }}}}
          *Detail:* {{{{ .CommonAnnotations.description }}}}
        send_resolved: true""")
            routes.append("    - receiver: 'slack'\n      group_wait: 10s")

        # Email
        if c['enable_email'] and c.get('smtp_host') and c.get('smtp_to'):
            receivers.append(f"""  - name: 'email'
    email_configs:
      - to: '{c['smtp_to']}'
        from: '{c['smtp_from']}'
        smarthost: '{c['smtp_host']}:{c['smtp_port']}'
        auth_username: '{c['smtp_user']}'
        auth_password: '{c['smtp_pass']}'
        require_tls: true
        send_resolved: true""")
            routes.append("    - receiver: 'email'\n      group_wait: 30s")

        default_recv = 'null-receiver'
        if receivers:
            default_recv = receivers[0].split("'")[1]

        receivers_str = '\n'.join(receivers) if receivers else "  - name: 'null-receiver'"
        routes_str = '\n'.join(routes)

        content = f"""global:
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'instance']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: '{default_recv}'
  routes:
{routes_str if routes_str else "    []"}

receivers:
{receivers_str}

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'instance']
"""
        (self.base / 'prometheus' / 'alertmanager.yml').write_text(content)
        emit('[OK] alertmanager.yml digenerate')

    # ── loki-config.yml ───────────────────────────────────────────────────────
    def _gen_loki(self, emit):
        emit('[*] Generating prometheus/loki-config.yml ...')
        c = self.cfg
        retention = c['retention_loki']
        content = f"""auth_enabled: false

server:
  http_listen_port: {c['port_loki']}
  grpc_listen_port: 9096
  log_level: warn

common:
  instance_addr: 127.0.0.1
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory

query_range:
  results_cache:
    cache:
      embedded_cache:
        enabled: true
        max_size_mb: 100

schema_config:
  configs:
    - from: 2020-10-24
      store: tsdb
      object_store: filesystem
      schema: v13
      index:
        prefix: index_
        period: 24h

storage_config:
  tsdb_shipper:
    active_index_directory: /loki/index
    cache_location: /loki/index_cache

compactor:
  working_directory: /loki/compactor
  compaction_interval: 10m
  retention_enabled: true
  retention_delete_delay: 2h
  retention_delete_worker_count: 150
  delete_request_store: filesystem

limits_config:
  retention_period: {retention}
  ingestion_rate_mb: 16
  ingestion_burst_size_mb: 32
  allow_structured_metadata: false
  volume_enabled: true

ruler:
  alertmanager_url: http://alertmanager:{c['port_alertmanager']}
"""
        (self.base / 'prometheus' / 'loki-config.yml').write_text(content)
        emit('[OK] loki-config.yml digenerate')

    # ── promtail-config.yml ───────────────────────────────────────────────────
    def _gen_promtail(self, emit):
        emit('[*] Generating prometheus/promtail-config.yml ...')
        c = self.cfg
        content = f"""server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:{c['port_loki']}/loki/api/v1/push
    backoff_config:
      min_period: 500ms
      max_period: 5m
      max_retries: 10

scrape_configs:

  - job_name: syslog
    static_configs:
      - targets: [localhost]
        labels:
          job: syslog
          host: '{c['server_ip']}'
          __path__: /var/log/syslog

  - job_name: auth-log
    static_configs:
      - targets: [localhost]
        labels:
          job: auth
          host: '{c['server_ip']}'
          __path__: /var/log/auth.log
    pipeline_stages:
      - regex:
          expression: '(?P<timestamp>\\w{{3}}\\s+\\d{{1,2}} \\d{{2}}:\\d{{2}}:\\d{{2}}) (?P<hostname>\\S+) (?P<service>\\S+?)(?:\\[\\d+\\])?: (?P<message>.*)'
      - labels:
          service:
      - match:
          selector: '{{job="auth"}}'
          stages:
            - regex:
                expression: '(?i).*(?P<event>Failed password|Invalid user|Accepted password|authentication failure|session opened|session closed|sudo)'
            - labels:
                event:

  - job_name: kern-log
    static_configs:
      - targets: [localhost]
        labels:
          job: kernel
          host: '{c['server_ip']}'
          __path__: /var/log/kern.log

  - job_name: dpkg-log
    static_configs:
      - targets: [localhost]
        labels:
          job: dpkg
          host: '{c['server_ip']}'
          __path__: /var/log/dpkg.log

  - job_name: daemon-log
    static_configs:
      - targets: [localhost]
        labels:
          job: daemon
          host: '{c['server_ip']}'
          __path__: /var/log/daemon.log

  - job_name: journald
    journal:
      max_age: 12h
      path: /run/log/journal
      labels:
        job: journald
        host: '{c['server_ip']}'
    relabel_configs:
      - source_labels: [__journal__systemd_unit]
        target_label: unit
      - source_labels: [__journal__hostname]
        target_label: hostname
      - source_labels: [__journal_priority_keyword]
        target_label: level

  - job_name: docker
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
        refresh_interval: 5s
        filters:
          - name: status
            values: [running]
    relabel_configs:
      - source_labels: [__meta_docker_container_name]
        regex: "/(.*)"
        target_label: container
      - source_labels: [__meta_docker_container_label_com_docker_compose_service]
        target_label: service
    pipeline_stages:
      - docker: {{}}
"""
        (self.base / 'prometheus' / 'promtail-config.yml').write_text(content)
        emit('[OK] promtail-config.yml digenerate')

    # ── grafana datasources ───────────────────────────────────────────────────
    def _gen_datasources(self, emit):
        emit('[*] Generating grafana datasources ...')
        c = self.cfg
        ds_path = self.base / 'grafana' / 'provisioning' / 'datasources'
        ds_path.mkdir(parents=True, exist_ok=True)

        sources = f"""apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:{c['port_prometheus']}
    isDefault: true
    editable: false
    jsonData:
      timeInterval: "{c['scrape_interval']}"
"""
        if c['enable_loki']:
            sources += f"""
  - name: Loki
    type: loki
    access: proxy
    url: http://loki:{c['port_loki']}
    editable: false
    jsonData:
      maxLines: 1000
"""
        if c['enable_alertmanager']:
            sources += f"""
  - name: Alertmanager
    type: alertmanager
    access: proxy
    url: http://alertmanager:{c['port_alertmanager']}
    editable: false
    jsonData:
      handleGrafanaManagedAlerts: false
      implementation: prometheus
"""
        (ds_path / 'datasources.yml').write_text(sources)
        emit('[OK] datasources.yml digenerate')

    # ── docker-compose.yml ────────────────────────────────────────────────────
    def _gen_docker_compose(self, emit):
        emit('[*] Generating docker-compose.yml ...')
        c = self.cfg
        ip = c['server_ip']

        svc = {}

        # Prometheus
        svc['prometheus'] = f"""  prometheus:
    image: prom/prometheus:latest
    container_name: lightmon-prometheus
    restart: unless-stopped
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./prometheus/rules:/etc/prometheus/rules:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time={c['retention_prometheus']}'
      - '--web.enable-lifecycle'
      - '--web.enable-admin-api'
    networks: [lightmon-net]
    ports:
      - '{c["port_prometheus"]}:9090'
    healthcheck:
      test: ['CMD','wget','--quiet','--tries=1','--spider','http://localhost:9090/-/ready']
      interval: 30s
      timeout: 10s
      retries: 3"""

        # Grafana
        svc['grafana'] = f"""  grafana:
    image: grafana/grafana:latest
    container_name: lightmon-grafana
    restart: unless-stopped
    environment:
      - GF_SECURITY_ADMIN_USER=${{GRAFANA_USER}}
      - GF_SECURITY_ADMIN_PASSWORD=${{GRAFANA_PASSWORD}}
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_SERVER_ROOT_URL=http://{ip}:{c['port_nginx']}/grafana
      - GF_SERVER_SERVE_FROM_SUB_PATH=true
      - GF_PATHS_PROVISIONING=/etc/grafana/provisioning
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning:ro
      - grafana_dashboards:/var/lib/grafana/dashboards
    networks: [lightmon-net]
    ports:
      - '{c["port_grafana"]}:3000'
    depends_on:
      - prometheus
    healthcheck:
      test: ['CMD','wget','--quiet','--tries=1','--spider','http://localhost:3000/api/health']
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s"""

        # Alertmanager
        if c['enable_alertmanager']:
            svc['alertmanager'] = f"""  alertmanager:
    image: prom/alertmanager:latest
    container_name: lightmon-alertmanager
    restart: unless-stopped
    volumes:
      - ./prometheus/alertmanager.yml:/etc/alertmanager/alertmanager.yml:ro
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
    networks: [lightmon-net]
    ports:
      - '{c["port_alertmanager"]}:9093'
    healthcheck:
      test: ['CMD','wget','--quiet','--tries=1','--spider','http://localhost:9093/-/ready']
      interval: 30s
      timeout: 10s
      retries: 3"""

        # Loki
        if c['enable_loki']:
            svc['loki'] = f"""  loki:
    image: grafana/loki:latest
    container_name: lightmon-loki
    restart: unless-stopped
    volumes:
      - ./prometheus/loki-config.yml:/etc/loki/local-config.yaml:ro
      - loki_data:/loki
    command: -config.file=/etc/loki/local-config.yaml
    networks: [lightmon-net]
    ports:
      - '{c["port_loki"]}:3100'
    healthcheck:
      test: ['CMD','wget','--quiet','--tries=1','--spider','http://localhost:3100/ready']
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s"""

            svc['promtail'] = f"""  promtail:
    image: grafana/promtail:latest
    container_name: lightmon-promtail
    restart: unless-stopped
    volumes:
      - /var/log:/var/log:ro
      - /run/log/journal:/run/log/journal:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./prometheus/promtail-config.yml:/etc/promtail/config.yml:ro
    command: -config.file=/etc/promtail/config.yml
    networks: [lightmon-net]
    depends_on:
      - loki"""

        # Node Exporter
        if c['enable_node_exporter']:
            svc['node-exporter'] = f"""  node-exporter:
    image: prom/node-exporter:latest
    container_name: lightmon-node-exporter
    restart: unless-stopped
    pid: host
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    networks: [lightmon-net]
    ports:
      - '9100:9100'"""

        # cAdvisor
        if c['enable_cadvisor']:
            svc['cadvisor'] = f"""  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: lightmon-cadvisor
    restart: unless-stopped
    privileged: true
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    networks: [lightmon-net]
    ports:
      - '8080:8080'"""

        # Backend
        svc['backend'] = f"""  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: lightmon-backend
    restart: unless-stopped
    env_file: .env
    environment:
      - PROMETHEUS_URL=http://prometheus:9090
      - LOKI_URL=http://loki:{c['port_loki']}
      - ALERTMANAGER_URL=http://alertmanager:{c['port_alertmanager']}
    networks: [lightmon-net]
    ports:
      - '{c["port_backend"]}:8000'
    depends_on:
      - prometheus
    healthcheck:
      test: ['CMD','curl','-f','http://localhost:8000/health']
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 20s"""

        # Nginx
        svc['nginx'] = f"""  nginx:
    image: nginx:alpine
    container_name: lightmon-nginx
    restart: unless-stopped
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./frontend:/usr/share/nginx/html:ro
    networks: [lightmon-net]
    ports:
      - '{c["port_nginx"]}:80'
    depends_on:
      - grafana
      - backend
    healthcheck:
      test: ['CMD','wget','--quiet','--tries=1','--spider','http://localhost/health']
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 15s"""

        volumes = ['prometheus_data', 'grafana_data', 'grafana_dashboards']
        if c['enable_loki']:
            volumes.append('loki_data')
        volumes_str = '\n'.join(f'  {v}:' for v in volumes)

        all_svcs = '\n\n'.join(svc.values())

        compose = f"""

networks:
  lightmon-net:
    driver: bridge

volumes:
{volumes_str}

services:

{all_svcs}
"""
        (self.base / 'docker-compose.yml').write_text(compose)
        emit('[OK] docker-compose.yml digenerate')

    # ── Docker deploy ─────────────────────────────────────────────────────────
    def _deploy_stack(self, emit):
        emit('[*] Menjalankan docker compose pull...')
        self._run(['docker', 'compose', 'pull', '--quiet'], emit, cwd=self.base)

        emit('[*] Build backend image...')
        self._run(['docker', 'compose', 'build', 'backend'], emit, cwd=self.base)

        emit('[*] Menjalankan docker compose up...')
        self._run(['docker', 'compose', 'up', '-d', '--remove-orphans'], emit, cwd=self.base)

        emit('[OK] Stack berhasil dijalankan')

    def _run(self, cmd, emit, cwd=None):
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            cwd=str(cwd or self.base), text=True
        )
        for line in proc.stdout:
            line = line.strip()
            if line:
                emit('    ' + line)
        proc.wait()
        if proc.returncode != 0:
            emit(f'[WARN] Proses selesai dengan kode: {proc.returncode}')

    # ── Health check ──────────────────────────────────────────────────────────
    def _health_check(self, emit):
        import urllib.request
        c = self.cfg
        emit('[*] Menunggu services ready (60 detik)...')
        time.sleep(60)

        checks = [
            ('Prometheus', f'http://localhost:{c["port_prometheus"]}/-/ready'),
            ('Grafana',    f'http://localhost:{c["port_grafana"]}/api/health'),
            ('Backend',    f'http://localhost:{c["port_backend"]}/health'),
        ]
        if c['enable_alertmanager']:
            checks.append(('Alertmanager', f'http://localhost:{c["port_alertmanager"]}/-/ready'))
        if c['enable_loki']:
            checks.append(('Loki', f'http://localhost:{c["port_loki"]}/ready'))

        for name, url in checks:
            try:
                urllib.request.urlopen(url, timeout=5)
                emit(f'[OK] {name}: Running ✓')
            except:
                emit(f'[WARN] {name}: Belum ready (mungkin masih starting)')


# ─── Entrypoint ───────────────────────────────────────────────────────────────
def main():
    port = 7777
    host = '0.0.0.0'

    # Detect and show local IP
    # Detect real IP, skip Docker bridge
    import subprocess as _sp, re as _re
    local_ip = 'localhost'
    try:
        r = _sp.run(['ip','route','get','8.8.8.8'], capture_output=True, text=True, timeout=3)
        for i, t in enumerate(r.stdout.split()):
            if t == 'src' and i+1 < len(r.stdout.split()):
                candidate = r.stdout.split()[i+1]
                if not candidate.startswith('172.'):
                    local_ip = candidate
                    break
    except:
        pass
    if local_ip == 'localhost':
        try:
            result = _sp.run(['ip','-4','addr','show'], capture_output=True, text=True, timeout=3)
            for line in result.stdout.splitlines():
                m = _re.search(r"inet ([\d.]+)/", line)
                if m:
                    ip = m.group(1)
                    if ip != '127.0.0.1' and not ip.startswith('172.'):
                        local_ip = ip
                        break
        except:
            pass

    print(f"""
╔══════════════════════════════════════════════════════╗
║          ⚡  LightMon Setup Wizard                    ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  Buka browser dan akses:                             ║
║                                                      ║
║     http://{local_ip:<42}║
║     http://localhost:{port:<34}║
║                                                      ║
║  Ikuti wizard untuk konfigurasi otomatis.            ║
║  Tekan Ctrl+C untuk keluar.                          ║
╚══════════════════════════════════════════════════════╝
""".replace(f'http://{local_ip}', f'http://{local_ip}:{port}'))

    server = HTTPServer((host, port), WizardHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n[!] Wizard dihentikan.')


if __name__ == '__main__':
    main()
