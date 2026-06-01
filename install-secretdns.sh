#!/usr/bin/env bash
# Linux SecretDNS 원클릭 설치 스크립트 (DoH + SNI 파편화)
# 사용법: bash install-secretdns.sh

set -e
export LANG=ko_KR.UTF-8

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
BIN_DIR="$HOME/bin"
APPLICATIONS_DIR="$HOME/.local/share/applications"

echo "========================================"
echo " Linux SecretDNS 설치"
echo " DoH + SNI 파편화 통합 설치"
echo "========================================"
echo ""

mkdir -p "$BIN_DIR" "$APPLICATIONS_DIR"

# 1. 의존 패키지 설치
echo "[1/6] 의존 패키지 설치..."
sudo apt-get install -y dnscrypt-proxy libcap-dev build-essential 2>&1 | grep -E "^(설치|Installing|설정|Setting)" || true

# 2. tpws 빌드 및 설치
echo "[2/6] tpws 빌드 및 설치..."
if [ ! -f /usr/local/bin/tpws ]; then
    TMP_DIR=$(mktemp -d)
    git clone --depth=1 https://github.com/bol-van/zapret.git "$TMP_DIR/zapret"
    cd "$TMP_DIR/zapret/tpws"
    make
    sudo cp tpws /usr/local/bin/tpws
    sudo chmod +x /usr/local/bin/tpws
    cd "$REPO_DIR"
    rm -rf "$TMP_DIR"
    echo "      → tpws 설치 완료"
else
    echo "      → tpws 이미 설치됨"
fi

# tpws 시스템 사용자 생성
id tpws &>/dev/null || sudo useradd -r -s /usr/sbin/nologin tpws

# 3. 설정 파일 설치
echo "[3/6] 설정 파일 설치..."
sudo mkdir -p /etc/zapret /etc/dnscrypt-proxy /etc/systemd/resolved.conf.d
sudo cp "$REPO_DIR/config/dnscrypt-proxy.toml" /etc/dnscrypt-proxy/dnscrypt-proxy.toml
sudo cp "$REPO_DIR/config/tpws-domains.txt" /etc/zapret/tpws-domains.txt
sudo cp "$REPO_DIR/config/20-doh.conf" /etc/systemd/resolved.conf.d/20-doh.conf
# DoT 비활성화 (DoH 우선)
[ -f /etc/systemd/resolved.conf.d/10-dot.conf ] && \
    sudo mv /etc/systemd/resolved.conf.d/10-dot.conf /etc/systemd/resolved.conf.d/10-dot.conf.disabled || true
echo "      → 설정 파일 설치 완료"

# 4. systemd 서비스 등록
echo "[4/6] systemd 서비스 등록..."
sudo cp "$REPO_DIR/config/tpws.service" /etc/systemd/system/tpws.service
sudo systemctl daemon-reload
sudo systemctl enable dnscrypt-proxy.socket dnscrypt-proxy
sudo systemctl enable tpws
sudo systemctl restart dnscrypt-proxy.socket dnscrypt-proxy
sudo systemctl restart systemd-resolved
sudo systemctl start tpws
echo "      → 서비스 등록 및 시작 완료"

# 5. 토글 스크립트 설치
echo "[5/7] 통합 토글 스크립트 설치..."
cp "$REPO_DIR/secretdns" "$BIN_DIR/secretdns"
chmod +x "$BIN_DIR/secretdns"
sed "s|/home/arbada|$HOME|g" "$REPO_DIR/secretdns-toggle-notify" \
    > "$BIN_DIR/secretdns-toggle-notify"
chmod +x "$BIN_DIR/secretdns-toggle-notify"
echo "      → $BIN_DIR/secretdns"
echo "      → $BIN_DIR/secretdns-toggle-notify"

# 6. 비밀번호 없이 실행 권한 등록
echo "[6/7] sudoers 등록 (비밀번호 없이 토글)..."
SUDOERS_LINE="$(whoami) ALL=(root) NOPASSWD: $BIN_DIR/secretdns"
echo "$SUDOERS_LINE" | sudo tee /etc/sudoers.d/secretdns > /dev/null
sudo chmod 440 /etc/sudoers.d/secretdns
echo "      → /etc/sudoers.d/secretdns"

# 7. 시작 메뉴 등록
echo "[7/7] 시작 메뉴 등록..."
sed "s|/home/arbada|$HOME|g" "$REPO_DIR/desktop/secretdns.desktop" \
    > "$APPLICATIONS_DIR/secretdns.desktop"
update-desktop-database "$APPLICATIONS_DIR" 2>/dev/null || true
echo "      → $APPLICATIONS_DIR/secretdns.desktop"

echo ""
echo "========================================"
echo " 설치 완료!"
echo ""
echo " 시작 메뉴에서 'SecretDNS' 또는 '보안'으로 검색"
echo " 터미널에서: secretdns status"
echo "========================================"
echo ""

"$BIN_DIR/secretdns" status
