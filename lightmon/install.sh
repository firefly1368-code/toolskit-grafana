#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# LightMon — Universal Installer v4.0
# Support:
#   Debian 11/12 | Ubuntu 20/22/24 | Kali Linux | Linux Mint
#   CentOS 7/8/9 | RHEL 8/9 | Rocky Linux | AlmaLinux
#   Fedora 38/39/40 | openSUSE Leap/Tumbleweed
#   Arch Linux | Manjaro
#   Raspberry Pi OS (ARM32/ARM64)
# ═══════════════════════════════════════════════════════════════════════════════

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

log()  { echo -e "${GREEN}[✓]${NC} $*"; }
warn() { echo -e "${YELLOW}[!]${NC} $*"; }
err()  { echo -e "${RED}[✗]${NC} $*"; exit 1; }
info() { echo -e "${CYAN}[i]${NC} $*"; }

echo -e "${BOLD}${CYAN}"
cat << 'BANNER'
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣤⣤⣤⣤⣄⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⠶⣻⠝⠋⠠⠔⠛⠁⡀⠀⠈⢉⡙⠓⠶⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠞⢋⣴⡮⠓⠋⠀⠀⢄⠀⠀⠉⠢⣄⠀⠈⠁⠀⡀⠙⢶⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠞⢁⣔⠟⠁⠀⠀⠀⠀⠀⠈⡆⠀⠀⠀⠈⢦⡀⠀⠀⠘⢯⢢⠙⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡼⠃⠀⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠸⠀⠀⠀⠀⠀⢳⣦⡀⠀⠀⢯⠀⠈⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⠆⡄⢠⢧⠀⣸⠀⠀⠀⠀⠀⠀⠀⢰⠀⣄⠀⠀⠀⠀⢳⡈⢶⡦⣿⣷⣿⢉⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⣯⣿⣁⡟⠈⠣⡇⠀⠀⢸⠀⠀⠀⠀⢸⡄⠘⡄⠀⠀⠀⠈⢿⢾⣿⣾⢾⠙⠻⣾⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⡿⣮⠇⢙⠷⢄⣸⡗⡆⠀⢘⠀⠀⠀⠀⢸⠧⠀⢣⠀⠀⠀⡀⡸⣿⣿⠘⡎⢆⠈⢳⣽⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢠⡟⢻⢷⣄⠀⠀⠀⠀⠀⠀⣾⣳⡿⡸⢀⣿⠀⠀⢸⠙⠁⠀⠼⠀⠀⠀⠀⢸⣇⠠⡼⡤⠴⢋⣽⣱⢿⣧⠀⢳⠈⢧⠀⢻⣿⣧⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢀⡿⣠⡣⠃⣿⠃⠀⠀⠀⠀⣸⣳⣿⠇⣇⢸⣿⢸⣠⠼⠀⠀⠀⡇⠀⡀⠉⠒⣾⢾⣆⢟⣳⡶⠓⠶⠿⢼⣿⣇⠈⡇⠘⢆⠈⢿⡘⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠈⢷⣍⣤⡶⣿⡄⠀⠀⠀⢠⣿⠃⣿⠀⡏⢸⣿⣿⠀⢸⠀⠀⢠⡗⢀⠇⠀⢠⡟⠀⠻⣾⣿⠀⠀⠀⠀⡏⣿⣿⡀⢹⡀⠈⢦⠈⢷⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢁⣤⣄⠁⠀⠀⠀⣼⡏⢰⣟⠀⣇⠘⣿⣿⣾⣾⣆⢀⣾⠃⣼⢠⣶⣿⣭⣷⣶⣾⣿⣤⠀⠀⠀⡇⡯⣍⣧⠀⣷⠄⠈⢳⡀⢻⡁⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠺⣿⡿⠀⠀⠀⠀⡿⢀⣾⣧⠀⡗⡄⢿⣿⡙⣽⣿⣟⠛⠚⠛⠙⠉⢹⣿⣿⣦⠀⢸⡿⠀⠀⠀⢰⡯⣌⢻⡀⢸⢠⢰⡄⠹⡷⣿⣦⣤⠤⣶⡇⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⠀⣇⣾⣿⢸⢠⣧⢧⠘⣿⡇⠸⣿⢿⡆⠀⠀⠀⠀⠘⣯⠇⣿⠂⣸⢰⠀⠀⢀⣸⡧⣊⣼⡇⢸⣼⣸⣷⢣⢻⣄⠉⠙⠛⠉⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣳⣤⣴⣿⣏⣿⣾⢸⣿⡘⣧⣘⢿⣀⡙⣞⠁⠀⠀⠀⠀⢀⡬⢀⣉⢠⣧⡏⠀⠀⡎⣿⣿⣿⣿⠃⣸⡏⣿⣿⡎⢿⡘⡆⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⣠⣼⣿⣿⣿⣼⣿⣧⢿⣿⣿⣯⡻⠟⠀⠀⠀⠀⠀⠐⢯⠣⡽⢟⣽⠀⠀⢘⡇⣿⣿⣿⡟⣴⣿⣷⣿⣿⣧⣿⣷⡽⠀⠀⠀⠀⠀⠀⠀
⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣼⣹⣿⣇⣸⣿⣿⣿⣻⣚⣿⡿⣿⣿⣦⣤⣀⡉⠃⠀⢀⣀⣤⡶⠛⡏⠀⢀⣼⢸⣿⣿⣿⣿⣿⣿⣿⢋⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀
⣿⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠒⠒⠒⢭⢻⣽⣿⣿⣿⣿⣿⣿⢿⠿⣿⡏⠀⡼⠁⣀⣾⣿⣿⣿⣿⡿⣿⣿⣟⡻⣿⣿⡿⠣⠟⠀⠀⠀⠀⠀⠀⠀⠀
⠸⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢧⢿⣯⡽⠿⠛⠋⣵⢟⣋⣿⣶⣞⣤⣾⣿⣿⡟⢉⡿⢋⠻⢯⡉⢻⡟⢿⡅⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⢻⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡞⣿⣆⡀⠀⡼⡏⠉⠚⠭⢉⣠⠬⠛⠛⢁⡴⣫⠖⠁⠀⠀⣩⠟⠁⣸⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠈⢷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⣽⣿⣿⣾⠳⡙⣦⡤⠜⠊⠁⠀⣀⡴⠯⠾⠗⠒⠒⠛⠛⠛⠛⠛⠓⠿⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠘⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢷⣻⣿⣿⠔⢪⠓⠬⢍⠉⣩⣽⢻⣤⣶⣦⠀⠀⠀⢀⣀⣤⣴⣾⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠹⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣾⡏⢦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣯⣿⣿⠀⠀⣇⠀⣠⠎⠁⢹⡎⡟⡏⣷⣶⠿⠛⡟⠛⠛⣫⠟⠉⢿⣿⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢻⡄⠀⠀⠀⠀⠀⠀⠀⠀⠹⣿⣷⠈⢷⡤⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⣾⣷⡀⣀⣀⣷⡅⠀⠀⠈⣷⢳⡇⣿⠀⠀⣸⠁⢠⡾⣟⣛⣻⣟⡿⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢯⢻⣏⡵⠿⠿⢤⣄⠀⢀⣿⢸⣹⣿⣀⣴⣿⣴⣿⣛⠋⠉⠉⡉⠛⣿⣧⡀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠘⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⡎⣿⣥⣶⠖⢉⣿⡿⣿⣿⡿⣿⣟⠿⠿⣿⣿⣿⡯⠻⣿⣿⣿⣷⡽⣿⡗⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠸⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⡘⣿⣩⠶⣛⣋⡽⠿⣷⢬⣙⣻⣿⣿⣿⣯⣛⠳⣤⣬⡻⣿⣿⣿⣿⣧⠀⠀⠀⠀⠀⠀⠀
⠀⣿⣛⣻⣿⡿⠿⠟⠗⠶⠶⠶⠶⠤⠤⢤⠤⡤⢤⣤⣤⣤⣤⣄⣀⣀⣀⣀⣀⣀⣀⣀⣣⢹⣷⣶⣿⣿⣦⣴⣟⣛⣯⣤⣿⣿⣿⣿⣿⣷⣌⣿⣿⣿⣿⣿⣿⣿⣤⣤⣤⣤⣤⣤⣄
⠀⠉⠙⠛⠛⠛⠛⠛⠻⠿⠿⠿⠷⠶⠶⢶⣶⣶⣶⣶⣤⣤⣤⣤⣤⣥⣬⣭⣭⣉⣩⣍⣙⣏⣉⣏⣽⣶⣶⣶⣤⣤⣬⣤⣤⣾⣿⠶⠾⠿⠿⠿⠿⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠃
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠉⠉⠉⠛⠛⠛⠛⠛⠛⠋⠉⠉⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
BANNER
echo -e "${NC}"

[[ "$EUID" -ne 0 ]] && err "Jalankan dengan sudo: sudo bash install.sh"

# ── Detect OS & Architecture ───────────────────────────────────────────────────
info "Mendeteksi sistem operasi..."

ARCH=$(uname -m)
case "$ARCH" in
    x86_64)         ARCH_LABEL="x86_64" ;;
    aarch64|arm64)  ARCH_LABEL="aarch64" ;;
    armv7l)         ARCH_LABEL="armv7" ;;
    *)              ARCH_LABEL="$ARCH" ;;
esac

# Baca os-release
if [[ -f /etc/os-release ]]; then
    source /etc/os-release
    OS_ID="${ID,,}"
    OS_ID_LIKE="${ID_LIKE:-}"
    OS_CODENAME="${VERSION_CODENAME:-}"
    OS_VERSION="${VERSION_ID:-}"
    OS_PRETTY="${PRETTY_NAME:-$OS_ID}"
else
    err "/etc/os-release tidak ditemukan. OS tidak didukung."
fi

info "OS     : ${OS_PRETTY}"
info "Arch   : ${ARCH_LABEL}"

# Tentukan package manager family
detect_family() {
    case "$OS_ID" in
        ubuntu|linuxmint|pop)
            FAMILY="debian"; PKG="apt"; DOCKER_OS="ubuntu"; DOCKER_CODENAME="$OS_CODENAME"
            # Linux Mint pakai Ubuntu codename
            if [[ "$OS_ID" == "linuxmint" ]]; then
                DOCKER_CODENAME=$(grep UBUNTU_CODENAME /etc/os-release 2>/dev/null | cut -d= -f2 || echo "jammy")
            fi
            ;;
        debian)
            FAMILY="debian"; PKG="apt"; DOCKER_OS="debian"; DOCKER_CODENAME="$OS_CODENAME"
            ;;
        kali)
            FAMILY="debian"; PKG="apt"; DOCKER_OS="debian"; DOCKER_CODENAME="bookworm"
            ;;
        raspbian)
            FAMILY="debian"; PKG="apt"; DOCKER_OS="raspbian"; DOCKER_CODENAME="$OS_CODENAME"
            ;;
        centos)
            FAMILY="rhel"; PKG="yum"
            [[ "${OS_VERSION%%.*}" -ge 8 ]] && PKG="dnf"
            ;;
        rhel|rocky|almalinux|ol)
            FAMILY="rhel"; PKG="dnf"
            ;;
        fedora)
            FAMILY="fedora"; PKG="dnf"
            ;;
        opensuse-leap|opensuse-tumbleweed|sles)
            FAMILY="suse"; PKG="zypper"
            ;;
        arch|manjaro|endeavouros|garuda)
            FAMILY="arch"; PKG="pacman"
            ;;
        *)
            # Coba deteksi dari ID_LIKE
            if echo "$OS_ID_LIKE" | grep -qi "debian\|ubuntu"; then
                FAMILY="debian"; PKG="apt"; DOCKER_OS="debian"; DOCKER_CODENAME="${OS_CODENAME:-bookworm}"
            elif echo "$OS_ID_LIKE" | grep -qi "rhel\|fedora\|centos"; then
                FAMILY="rhel"; PKG="dnf"
            elif echo "$OS_ID_LIKE" | grep -qi "suse"; then
                FAMILY="suse"; PKG="zypper"
            elif echo "$OS_ID_LIKE" | grep -qi "arch"; then
                FAMILY="arch"; PKG="pacman"
            else
                err "Distro '$OS_ID' tidak didukung. Buka issue di GitHub."
            fi
            ;;
    esac
}
detect_family
log "Family : $FAMILY | Package manager: $PKG"

# ── Fix repo bermasalah ────────────────────────────────────────────────────────
if [[ "$FAMILY" == "debian" ]]; then
    # Kali: disable Elasticsearch repo yang SHA1-nya expired
    for f in /etc/apt/sources.list.d/elastic*.list /etc/apt/sources.list.d/elastic*.sources; do
        [[ -f "$f" ]] && mv "$f" "${f}.bak" && warn "Disabled broken repo: $(basename $f)"
    done
fi

# ── Install dependencies ───────────────────────────────────────────────────────
info "Install dependencies..."

install_deps_debian() {
    apt-get update 2>&1 | grep -E "^(E:|Err:)" || true
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        ca-certificates curl gnupg wget python3 openssl \
        lsb-release apt-transport-https software-properties-common 2>&1 | tail -3
}

install_deps_rhel() {
    # Enable EPEL untuk CentOS/RHEL
    if [[ "$OS_ID" == "centos" || "$OS_ID" == "rhel" ]]; then
        $PKG install -y epel-release 2>/dev/null || true
    fi
    $PKG install -y \
        ca-certificates curl gnupg2 wget python3 openssl \
        yum-utils device-mapper-persistent-data lvm2 2>&1 | tail -3
}

install_deps_fedora() {
    $PKG install -y \
        ca-certificates curl gnupg2 wget python3 openssl \
        dnf-plugins-core 2>&1 | tail -3
}

install_deps_suse() {
    zypper refresh 2>&1 | tail -3 || true
    zypper install -y \
        ca-certificates curl wget python3 openssl 2>&1 | tail -3
}

install_deps_arch() {
    pacman -Sy --noconfirm \
        ca-certificates curl wget python openssl 2>&1 | tail -3
}

case "$FAMILY" in
    debian) install_deps_debian ;;
    rhel)   install_deps_rhel ;;
    fedora) install_deps_fedora ;;
    suse)   install_deps_suse ;;
    arch)   install_deps_arch ;;
esac

# ── Install Docker ─────────────────────────────────────────────────────────────
install_docker_debian() {
    DEBIAN_FRONTEND=noninteractive apt-get remove -y \
        docker docker-engine docker.io containerd runc 2>/dev/null || true

    install -m 0755 -d /etc/apt/keyrings
    rm -f /etc/apt/keyrings/docker.gpg

    curl -fsSL "https://download.docker.com/linux/${DOCKER_OS}/gpg" \
        | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg

    # Raspberry Pi: pakai armhf/arm64
    DEB_ARCH=$(dpkg --print-architecture)

    echo "deb [arch=${DEB_ARCH} signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/${DOCKER_OS} ${DOCKER_CODENAME} stable" \
        | tee /etc/apt/sources.list.d/docker.list > /dev/null

    apt-get update 2>&1 | grep -E "^(E:|Err:)" || true
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        docker-ce docker-ce-cli containerd.io \
        docker-buildx-plugin docker-compose-plugin 2>&1 | tail -5 || {
        warn "docker-ce gagal, fallback ke docker.io..."
        rm -f /etc/apt/sources.list.d/docker.list
        apt-get update 2>/dev/null | grep -E "^(E:|Err:)" || true
        DEBIAN_FRONTEND=noninteractive apt-get install -y docker.io 2>&1 | tail -3
    }
}

install_docker_rhel() {
    $PKG remove -y docker docker-client docker-client-latest \
        docker-common docker-latest docker-engine podman runc 2>/dev/null || true

    if [[ "$PKG" == "dnf" ]]; then
        dnf config-manager --add-repo \
            https://download.docker.com/linux/centos/docker-ce.repo 2>/dev/null || \
        dnf config-manager --add-repo \
            https://download.docker.com/linux/rhel/docker-ce.repo 2>/dev/null || true
        dnf install -y docker-ce docker-ce-cli containerd.io \
            docker-buildx-plugin docker-compose-plugin 2>&1 | tail -5
    else
        yum-config-manager --add-repo \
            https://download.docker.com/linux/centos/docker-ce.repo
        yum install -y docker-ce docker-ce-cli containerd.io 2>&1 | tail -5
    fi
}

install_docker_fedora() {
    dnf remove -y docker docker-client docker-client-latest \
        docker-common docker-latest docker-engine moby-engine 2>/dev/null || true
    dnf config-manager --add-repo \
        https://download.docker.com/linux/fedora/docker-ce.repo
    dnf install -y docker-ce docker-ce-cli containerd.io \
        docker-buildx-plugin docker-compose-plugin 2>&1 | tail -5
}

install_docker_suse() {
    # openSUSE: pakai repo komunitas Docker
    zypper addrepo https://download.docker.com/linux/sles/docker-ce.repo 2>/dev/null || true
    zypper refresh 2>/dev/null || true
    zypper install -y docker-ce docker-ce-cli containerd.io \
        docker-compose-plugin 2>&1 | tail -5 || {
        warn "Fallback: install docker dari repo openSUSE..."
        zypper install -y docker docker-compose 2>&1 | tail -3
    }
}

install_docker_arch() {
    pacman -S --noconfirm docker docker-compose 2>&1 | tail -5
}

DOCKER_OK=false
if command -v docker &>/dev/null; then
    systemctl start docker 2>/dev/null || service docker start 2>/dev/null || true
    sleep 2
    docker info &>/dev/null 2>&1 && DOCKER_OK=true && log "Docker sudah ada: $(docker --version)"
fi

if [[ "$DOCKER_OK" == "false" ]]; then
    info "Menginstall Docker..."
    case "$FAMILY" in
        debian) install_docker_debian ;;
        rhel)   install_docker_rhel ;;
        fedora) install_docker_fedora ;;
        suse)   install_docker_suse ;;
        arch)   install_docker_arch ;;
    esac

    systemctl start docker 2>/dev/null || service docker start 2>/dev/null || true
    sleep 3
    docker info &>/dev/null 2>&1 || err "Docker gagal start. Coba: sudo systemctl start docker"
fi

systemctl enable docker 2>/dev/null || true

# ── Docker Compose v2 ──────────────────────────────────────────────────────────
if ! docker compose version &>/dev/null 2>&1; then
    warn "Docker Compose plugin tidak ada, install binary langsung..."
    COMPOSE_VER="v2.27.0"
    case "$ARCH_LABEL" in
        x86_64)  COMPOSE_ARCH="x86_64" ;;
        aarch64) COMPOSE_ARCH="aarch64" ;;
        armv7)   COMPOSE_ARCH="armv7" ;;
        *)       COMPOSE_ARCH="x86_64" ;;
    esac

    PLUGIN_DIRS=(
        "/usr/local/lib/docker/cli-plugins"
        "/usr/lib/docker/cli-plugins"
        "$HOME/.docker/cli-plugins"
    )
    for dir in "${PLUGIN_DIRS[@]}"; do
        mkdir -p "$dir" 2>/dev/null && \
        curl -fsSL "https://github.com/docker/compose/releases/download/${COMPOSE_VER}/docker-compose-linux-${COMPOSE_ARCH}" \
            -o "$dir/docker-compose" && \
        chmod +x "$dir/docker-compose" && break || true
    done
fi

docker compose version &>/dev/null 2>&1 || err "Docker Compose gagal diinstall."
log "Docker  : $(docker --version)"
log "Compose : $(docker compose version --short 2>/dev/null)"

# ── Tambah user ke group docker ────────────────────────────────────────────────
ACTUAL_USER="${SUDO_USER:-}"
if [[ -n "$ACTUAL_USER" && "$ACTUAL_USER" != "root" ]]; then
    usermod -aG docker "$ACTUAL_USER" 2>/dev/null || true
    warn "User '$ACTUAL_USER' ditambahkan ke group docker."
    warn "Jalankan: newgrp docker  (atau logout & login kembali)"
fi

# ── System tuning ──────────────────────────────────────────────────────────────
info "System tuning..."
sysctl -w vm.max_map_count=262144 &>/dev/null || true
grep -q "vm.max_map_count" /etc/sysctl.conf 2>/dev/null || \
    echo "vm.max_map_count=262144" >> /etc/sysctl.conf

# SELinux (RHEL/Fedora/CentOS) — set permissive agar Docker bisa akses volume
if command -v getenforce &>/dev/null && [[ "$(getenforce)" == "Enforcing" ]]; then
    warn "SELinux Enforcing terdeteksi. Set ke Permissive untuk Docker..."
    setenforce 0 2>/dev/null || true
    sed -i 's/^SELINUX=enforcing/SELINUX=permissive/' /etc/selinux/config 2>/dev/null || true
fi

# Firewall
if command -v ufw &>/dev/null && ufw status 2>/dev/null | grep -q "active"; then
    for port in 80 3000 7777 8000 9090 9093 3100; do
        ufw allow "$port/tcp" comment "LightMon" &>/dev/null || true
    done
    warn "UFW: port LightMon dibuka"
elif command -v firewall-cmd &>/dev/null && systemctl is-active --quiet firewalld; then
    # firewalld (RHEL/Fedora/CentOS)
    for port in 80 3000 7777 8000 9090 9093 3100; do
        firewall-cmd --permanent --add-port="${port}/tcp" &>/dev/null || true
    done
    firewall-cmd --reload &>/dev/null || true
    warn "firewalld: port LightMon dibuka"
fi

# ── Detect IP (skip Docker bridge & loopback) ──────────────────────────────────
detect_ip() {
    # Cara 1: ip route — paling akurat
    local ip
    ip=$(ip route get 8.8.8.8 2>/dev/null | awk '/src/{for(i=1;i<=NF;i++) if($i=="src") print $(i+1)}' | head -1)
    if [[ -n "$ip" && "$ip" != 172.* && "$ip" != "127."* ]]; then
        echo "$ip"; return
    fi
    # Cara 2: scan semua interface, skip docker/lo
    ip -4 addr show 2>/dev/null | awk '/inet /{print $2}' | cut -d/ -f1 | \
        grep -v "^127\.\|^172\." | head -1
}
LOCAL_IP=$(detect_ip)
LOCAL_IP="${LOCAL_IP:-127.0.0.1}"

# ── Launch Wizard ──────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${GREEN}  ✅ Instalasi selesai! Siap menjalankan Setup Wizard.${NC}"
echo -e "${BOLD}${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  OS      : ${OS_PRETTY}"
echo -e "  Arch    : ${ARCH_LABEL}"
echo -e "  Docker  : $(docker --version | cut -d' ' -f3 | tr -d ',')"
echo -e "  Compose : $(docker compose version --short 2>/dev/null)"
echo -e "  IP      : ${CYAN}${LOCAL_IP}${NC}"
echo ""
echo -e "  ${BOLD}Buka browser dan akses Setup Wizard:${NC}"
echo ""
echo -e "  ${BOLD}${CYAN}  ➜  http://${LOCAL_IP}:7777${NC}"
echo -e "  ${CYAN}     http://localhost:7777${NC}"
echo ""
echo -e "  ${YELLOW}⚠  Jangan tutup terminal ini selama wizard berjalan.${NC}"
echo ""

info "Menjalankan Setup Wizard..."
exec python3 "$SCRIPT_DIR/wizard/wizard.py"
