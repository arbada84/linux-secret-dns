#!/usr/bin/env bash
# linux-secret-dns 원클릭 설치 스크립트
# 사용법: bash install.sh

set -e
export LANG=ko_KR.UTF-8

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
BIN_DIR="$HOME/bin"
APPLICATIONS_DIR="$HOME/.local/share/applications"
DOT_CONF_DIR="/etc/systemd/resolved.conf.d"

echo "========================================"
echo " Linux Secret DNS (DoT) 설치"
echo "========================================"
echo ""

# 1. ~/bin 디렉토리 확인
mkdir -p "$BIN_DIR" "$APPLICATIONS_DIR"

# 2. 토글 스크립트 설치
echo "[1/3] 토글 스크립트 설치..."
cp "$REPO_DIR/dns-dot-toggle" "$BIN_DIR/dns-dot-toggle"
chmod +x "$BIN_DIR/dns-dot-toggle"
echo "      → $BIN_DIR/dns-dot-toggle"

# 3. DoT 설정 파일 설치 (root 필요)
echo "[2/3] DNS over TLS 설정 적용 (관리자 권한 필요)..."
sudo mkdir -p "$DOT_CONF_DIR"
sudo cp "$REPO_DIR/config/10-dot.conf" "$DOT_CONF_DIR/10-dot.conf"
sudo systemctl restart systemd-resolved
echo "      → $DOT_CONF_DIR/10-dot.conf"
echo "      → systemd-resolved 재시작 완료"

# 4. 시작 메뉴 등록
echo "[3/3] 시작 메뉴 등록..."
# desktop 파일의 Exec 경로를 현재 사용자 홈으로 치환
sed "s|/home/arbada|$HOME|g" "$REPO_DIR/desktop/dns-dot-toggle.desktop" \
    > "$APPLICATIONS_DIR/dns-dot-toggle.desktop"
chmod +x "$APPLICATIONS_DIR/dns-dot-toggle.desktop"
# 메뉴 캐시 갱신
update-desktop-database "$APPLICATIONS_DIR" 2>/dev/null || true
echo "      → $APPLICATIONS_DIR/dns-dot-toggle.desktop"

echo ""
echo "========================================"
echo " 설치 완료!"
echo ""
echo " 시작 메뉴에서 'DNS' 또는 '보안'으로 검색하세요."
echo " 터미널에서: dns-dot-toggle status"
echo "========================================"
echo ""

# 현재 상태 출력
"$BIN_DIR/dns-dot-toggle" status
