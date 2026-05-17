#!/bin/bash
# LightMon Management Script
DIR="$(cd "$(dirname "$0")" && pwd)"
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'
log()  { echo -e "${GREEN}[✓]${NC} $*"; }
warn() { echo -e "${YELLOW}[!]${NC} $*"; }
info() { echo -e "${CYAN}[i]${NC} $*"; }

cmd_start()   { info "Starting..."; cd "$DIR" && docker compose up -d; log "Done"; }
cmd_stop()    { warn "Stopping..."; cd "$DIR" && docker compose down; log "Stopped"; }
cmd_restart() { cmd_stop; sleep 2; cmd_start; }

cmd_status() {
    echo -e "${BOLD}${CYAN}═══ LightMon Status ═══${NC}"
    cd "$DIR" && docker compose ps
    echo ""
    echo -e "${BOLD}Resource Usage:${NC}"
    IDS=$(docker compose ps -q 2>/dev/null)
    [[ -n "$IDS" ]] && docker stats --no-stream --format \
        "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" $IDS 2>/dev/null || true
}

cmd_logs() {
    local svc="${2:-}"
    cd "$DIR"
    [[ -n "$svc" ]] && docker compose logs -f "$svc" || docker compose logs -f
}

cmd_wizard() {
    info "Membuka Setup Wizard di port 7777..."
    LOCAL_IP=$(ip route get 8.8.8.8 2>/dev/null | awk '/src/{for(i=1;i<=NF;i++) if($i=="src") print $(i+1)}' | head -1)
    echo -e "  Akses: ${CYAN}http://${LOCAL_IP:-localhost}:7777${NC}"
    cd "$DIR" && python3 wizard/wizard.py
}

cmd_add_server() {
    echo -e "${BOLD}═══ Tambah Server Remote ═══${NC}"
    read -rp "IP server target: " SERVER_IP
    [[ -z "$SERVER_IP" ]] && echo "IP kosong" && exit 1
    read -rp "Nama server (contoh: web-01): " SERVER_NAME
    [[ -z "$SERVER_NAME" ]] && echo "Nama kosong" && exit 1

    PROM_CFG="$DIR/prometheus/prometheus.yml"
    grep -q "\"$SERVER_NAME\"" "$PROM_CFG" 2>/dev/null && warn "Server '$SERVER_NAME' sudah ada" && return

    cat >> "$PROM_CFG" << EOF

  - job_name: "$SERVER_NAME"
    static_configs:
      - targets: ["${SERVER_IP}:9100"]
        labels:
          instance: "$SERVER_NAME"
EOF
    log "Server $SERVER_NAME ditambahkan"
    curl -sf -X POST "http://localhost:9090/-/reload" &>/dev/null && \
        log "Prometheus di-reload" || { warn "Reload gagal, restart..."; cd "$DIR" && docker compose restart prometheus; }

    echo ""
    info "Install Node Exporter di $SERVER_IP:"
    echo "  docker run -d --name node-exporter --pid=host --restart=unless-stopped \\"
    echo "    -v /:/host:ro,rslave -p 9100:9100 prom/node-exporter --path.rootfs=/host"
}

cmd_backup() {
    BACKUP_DIR="$DIR/backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    info "Backup ke $BACKUP_DIR..."
    for vol in prometheus_data grafana_data loki_data; do
        docker run --rm -v "${vol}:/data" -v "$BACKUP_DIR:/backup" alpine \
            tar czf "/backup/${vol}.tar.gz" /data 2>/dev/null && log "$vol ✓" || warn "$vol skip"
    done
    cp "$DIR/.env" "$BACKUP_DIR/" 2>/dev/null && log ".env ✓" || true
    log "Backup selesai: $BACKUP_DIR"
}

case "${1:-help}" in
    start)      cmd_start ;;
    stop)       cmd_stop ;;
    restart)    cmd_restart ;;
    status)     cmd_status ;;
    logs)       cmd_logs "$@" ;;
    wizard)     cmd_wizard ;;
    add-server) cmd_add_server ;;
    backup)     cmd_backup ;;
    *)
        echo -e "${BOLD}LightMon Manage${NC}"
        echo "  start          Mulai semua services"
        echo "  stop           Stop semua services"
        echo "  restart        Restart semua services"
        echo "  status         Status & resource usage"
        echo "  logs [svc]     Lihat logs"
        echo "  wizard         Buka Setup Wizard kembali"
        echo "  add-server     Tambah server remote"
        echo "  backup         Backup semua data"
        ;;
esac
