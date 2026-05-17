# ⚡ LightMon
# di karenakan ini untuk kebutuhan bersama,jadi bebas di modifikasi toh ini ada bagian di mana di bantu AI.⠀⠀
# di unzip dulu ya!⠀⠀⠀⠀⠀⠀⠀⠀
# Stack monitoring **Grafana + Prometheus + Loki + Alertmanager** dengan Setup Wizard berbasis web.

## Platform
| OS | Status |
|---|---|
| Kali Linux Purple/Rolling | ✅ |
| Debian 12 (Bookworm) | ✅ |
| Ubuntu 20/22/24 | ✅ |

## Cara Install

```bash
unzip lightmon-v3.zip
cd lightmon
sudo bash install.sh
# Buka browser → http://localhost:7777
```

## Setelah Deploy

```bash
bash manage.sh status      # cek status
bash manage.sh logs        # lihat logs
bash manage.sh wizard      # buka wizard lagi
bash manage.sh add-server  # tambah server remote
bash manage.sh backup      # backup data
```

## Akses (setelah deploy)

| Service | URL |
|---|---|
| Dashboard | http://localhost/ |
| Grafana | http://localhost/grafana/ |
| Prometheus | http://localhost:9090 |
| Alertmanager | http://localhost:9093 |
| Loki | http://localhost:3100 |
| Backend API | http://localhost:8000/docs |
