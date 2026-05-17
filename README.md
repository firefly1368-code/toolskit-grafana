<div align="center">

# ⚡ LightMon

**Self-hosted Monitoring Toolbox dengan Setup Wizard berbasis web.**
Deploy Grafana + Prometheus + Loki + Alertmanager dalam hitungan menit — tanpa konfigurasi manual.

[![MIT License](https://img.shields.io/badge/License-MIT-6366f1?style=flat-square)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Required-2496ED?style=flat-square&logo=docker)](https://docker.com)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python)](https://python.org)
[![Grafana](https://img.shields.io/badge/Grafana-Latest-F46800?style=flat-square&logo=grafana)](https://grafana.com)
[![Prometheus](https://img.shields.io/badge/Prometheus-Latest-E6522C?style=flat-square&logo=prometheus)](https://prometheus.io)

</div>

---

## 📖 Tentang

LightMon adalah monitoring toolbox yang dirancang untuk kemudahan — cukup jalankan satu perintah, lalu ikuti Setup Wizard di browser untuk mengkonfigurasi seluruh stack monitoring secara otomatis.

Tidak perlu edit file YAML, tidak perlu konfigurasi manual. Semua digenerate otomatis.

---

## ✨ Fitur

- 🧙 **Setup Wizard berbasis web** — konfigurasi IP, port, dan alert lewat UI browser
- 📊 **Grafana Dashboard** — visualisasi metrics real-time
- 🔥 **Prometheus** — pengumpulan metrics CPU, RAM, Disk, Network
- 📝 **Loki + Promtail** — agregasi log sistem (syslog, auth.log, journald)
- 🔔 **Alertmanager** — notifikasi alert ke **Telegram Bot**, **Slack**, dan **Email**
- 🐳 **cAdvisor** — monitoring resource per container Docker
- 🖥️ **Node Exporter** — metrics dari sistem host
- 🌐 **Multi-server** — tambah server remote untuk dimonitor
- 💾 **Backup & Restore** — backup data Prometheus, Grafana, Loki

---

## 🖥️ Platform yang Didukung

| OS | Status |
|---|---|
| Kali Linux Purple / Rolling | ✅ |
| Debian 11 / 12 | ✅ |
| Ubuntu 20 / 22 / 24 | ✅ |

---

## 🚀 Cara Install

```bash
# 1. Clone repo
git clone https://github.com/USERNAME/lightmon.git
cd lightmon

# 2. Jalankan installer
sudo bash install.sh

# 3. Buka browser → Setup Wizard otomatis terbuka
# http://localhost:7777
```

> ⚠️ Butuh Docker. Jika belum ada, `install.sh` akan menginstall otomatis.

---

## 🧙 Setup Wizard

Setelah `install.sh` selesai, buka browser dan ikuti 5 langkah wizard:

| Step | Konfigurasi |
|---|---|
| 1️⃣ Network | IP server, port Grafana/Prometheus/Loki/Alertmanager |
| 2️⃣ Services | Pilih komponen yang ingin diaktifkan |
| 3️⃣ Alerts | Token Telegram Bot, Slack Webhook, SMTP Email |
| 4️⃣ Security | Username/password Grafana, retensi data |
| 5️⃣ Deploy | Review config → klik Deploy → selesai |

---

## 📡 Akses Setelah Deploy

| Service | URL |
|---|---|
| 🌐 Dashboard | `http://localhost/` |
| 📊 Grafana | `http://localhost/grafana/` |
| 🔥 Prometheus | `http://localhost:9090` |
| 🔔 Alertmanager | `http://localhost:9093` |
| 📝 Loki | `http://localhost:3100` |
| 🔧 Backend API | `http://localhost:8000/docs` |

---

## 🛠️ Management

```bash
bash manage.sh status      # Cek status semua container
bash manage.sh logs        # Lihat logs
bash manage.sh restart     # Restart stack
bash manage.sh wizard      # Buka Setup Wizard kembali
bash manage.sh add-server  # Tambah server remote
bash manage.sh backup      # Backup semua data
```

---

## 🏗️ Tech Stack

| Komponen | Teknologi |
|---|---|
| Metrics | Prometheus + Node Exporter + cAdvisor |
| Logs | Loki + Promtail |
| Dashboard | Grafana |
| Alerts | Alertmanager |
| Backend API | FastAPI (Python) |
| Reverse Proxy | Nginx |
| Wizard | Python (no external deps) |
| Container | Docker + Docker Compose |

---

## 📁 Struktur Project

```
lightmon/
├── install.sh          ← Jalankan pertama kali
├── manage.sh           ← Management sehari-hari
├── wizard/
│   └── wizard.py       ← Setup Wizard (web UI)
├── prometheus/         ← Config digenerate otomatis
├── grafana/            ← Provisioning digenerate otomatis
├── backend/            ← FastAPI backend
├── frontend/           ← Dashboard UI
└── nginx/              ← Reverse proxy config
```

---

## 🤝 Kontribusi

Pull request dan issue sangat disambut! Proyek ini open source di bawah lisensi MIT — bebas dimodifikasi dan didistribusikan.

---

## 📄 Lisensi

[MIT License](LICENSE) © 2026 Alyaa

---

<div align="center">

Dibuat dengan ❤️ untuk komunitas open source

⭐ Jangan lupa kasih star kalau project ini membantu!

</div>
