# 🔒 Linux Secret DNS (DNS over TLS)

> 리눅스에서 통신사 DNS 감청을 차단하는 암호화 DNS 설정 가이드  
> 길호넷 시크릿DNS와 동일한 원리를 Linux Mint에서 직접 구현합니다.

---

## 📋 목차

1. [기획 배경](#1-기획-배경)
2. [기술 개요](#2-기술-개요)
3. [시스템 구성](#3-시스템-구성)
4. [설치 방법](#4-설치-방법)
5. [사용 방법](#5-사용-방법)
6. [시작 메뉴 등록](#6-시작-메뉴-등록)
7. [파일 구조](#7-파일-구조)
8. [문제 해결](#8-문제-해결)

---

## 1. 기획 배경

### 문제 인식

일반적인 인터넷 환경에서 DNS 조회는 **암호화 없이** 전송됩니다.

```
사용자 → [평문 DNS 쿼리: "youtube.com 알려줘"] → ISP DNS 서버
                      ↑
              통신사가 모두 볼 수 있음
              (방문 사이트 기록, 차단, 변조 가능)
```

### 목표

| 항목 | 기존 방식 | 도입 후 |
|------|----------|---------|
| DNS 통신 | 평문 (UDP 53) | 암호화 (TLS 853) |
| DNS 서버 | 통신사 (KT, SKT 등) | Cloudflare / Quad9 |
| 방문 기록 노출 | 통신사에 노출됨 | 노출 안 됨 |
| DNS 변조 위험 | 있음 | 없음 |
| 속도 영향 | - | 거의 없음 |

### 유사 서비스

- **길호넷 시크릿DNS** (KT 제공) — Windows 전용 클라이언트
- **Cloudflare 1.1.1.1 앱** — 모바일/Windows 전용
- **본 구현** — Linux Mint에서 네이티브로 직접 구현 ✅

---

## 2. 기술 개요

### DNS over TLS (DoT) 란?

```
[일반 DNS]
사용자 ──── UDP:53 ──── DNS 서버   (평문, 누구나 열람 가능)

[DNS over TLS]
사용자 ════ TLS:853 ════ DNS 서버  (암호화, 중간 열람 불가)
```

- **포트**: TCP 853
- **암호화**: TLS 1.3
- **인증**: 서버 인증서로 DNS 서버 신원 검증

### 사용 DNS 서버

| 서버 | IP | 도메인 | 특징 |
|------|-----|--------|------|
| Cloudflare | 1.1.1.1 / 1.0.0.1 | `cloudflare-dns.com` | 빠름, 로그 없음 |
| Quad9 | 9.9.9.9 / 149.112.112.112 | `dns.quad9.net` | 악성사이트 차단 |
| Google (대체) | 8.8.8.8 / 8.8.4.4 | `dns.google` | 폴백 전용 |

### Linux 구현 방식

```
앱/브라우저
    ↓
systemd-resolved (127.0.0.53:53)  ← 로컬 DNS 스텁
    ↓ TLS 암호화
Cloudflare 1.1.1.1:853
```

`systemd-resolved`의 `DNSOverTLS=yes` 설정으로 구현됩니다.

---

## 3. 시스템 구성

### 테스트 환경

- **OS**: Linux Mint (Ubuntu 24.04 기반)
- **오디오/DNS 관리**: PipeWire + systemd-resolved + NetworkManager
- **하드웨어**: Intel i5-1135G7 (LG gram 14Z95N)

### 설정 파일 위치

```
/etc/systemd/resolved.conf.d/
└── 10-dot.conf          ← DoT 활성 시
└── 10-dot.conf.disabled ← DoT 비활성 시 (toggle 스크립트가 관리)

~/bin/
└── dns-dot-toggle       ← 켜기/끄기 토글 스크립트

~/.local/share/applications/
└── dns-dot-toggle.desktop  ← 시작 메뉴 등록
```

---

## 4. 설치 방법

### 4-1. 사전 요구사항 확인

```bash
# systemd-resolved 실행 확인
systemctl status systemd-resolved

# 현재 DNS 상태 확인
resolvectl status | grep -E "DNS|Protocols"
```

### 4-2. DoT 설정 파일 생성

```bash
sudo mkdir -p /etc/systemd/resolved.conf.d

sudo tee /etc/systemd/resolved.conf.d/10-dot.conf > /dev/null << 'EOF'
[Resolve]
DNS=1.1.1.1#cloudflare-dns.com 1.0.0.1#cloudflare-dns.com 9.9.9.9#dns.quad9.net 149.112.112.112#dns.quad9.net
FallbackDNS=8.8.8.8#dns.google 8.8.4.4#dns.google
Domains=~.
DNSOverTLS=yes
DNSSEC=no
EOF

sudo systemctl restart systemd-resolved
```

> **설명**
> - `DNS=1.1.1.1#cloudflare-dns.com` — `#` 뒤 도메인으로 TLS 인증서 검증
> - `Domains=~.` — 모든 도메인을 이 DNS로 처리
> - `DNSOverTLS=yes` — TLS 강제 사용 (`opportunistic`으로 설정 시 실패 시 평문 허용)
> - `DNSSEC=no` — DNSSEC은 비활성 (Cloudflare DoT로 충분)

### 4-3. 토글 스크립트 설치

```bash
# 스크립트 다운로드 또는 직접 생성
curl -fsSL https://raw.githubusercontent.com/arbada84/linux-secret-dns/main/dns-dot-toggle \
    -o ~/bin/dns-dot-toggle
chmod +x ~/bin/dns-dot-toggle
```

### 4-4. 동작 확인

```bash
# 상태 확인
dns-dot-toggle status

# 암호화 사용 여부 확인
resolvectl query example.com
# "Data was acquired via local or encrypted transport: yes" 가 나오면 성공
```

---

## 5. 사용 방법

### 터미널 명령어

```bash
# 현재 상태 확인
dns-dot-toggle status

# DoT 켜기 (암호화 DNS 활성)
dns-dot-toggle on

# DoT 끄기 (ISP 기본 DNS로 복귀)
dns-dot-toggle off
```

### 상태 예시

```
=== DNS over TLS 상태 ===

  상태: 🟢 켜짐 (DNS over TLS 활성)

  현재 DNS 서버:
    - Cloudflare : 1.1.1.1 / 1.0.0.1 (암호화)
    - Quad9      : 9.9.9.9 (암호화)
    - Fallback   : 8.8.8.8 Google (암호화)

  → 모든 DNS 쿼리가 암호화되어 전송됩니다
    ISP(통신사)에 방문 도메인이 노출되지 않습니다
```

---

## 6. 시작 메뉴 등록

### 방법: `.desktop` 파일 등록

Linux 시작 메뉴에 앱을 등록하려면 `~/.local/share/applications/` 에  
`.desktop` 파일을 생성하면 됩니다.

```bash
cat > ~/.local/share/applications/dns-dot-toggle.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=DNS 보안 설정 (DoT)
GenericName=DNS over TLS 토글
Comment=DNS over TLS 켜기/끄기 및 상태 확인
Exec=xfce4-terminal --title="DNS 보안 설정" --command="bash -c '/home/arbada/bin/dns-dot-toggle; read -p \"엔터를 누르면 닫힙니다...\"'"
Icon=network-vpn
Terminal=false
Categories=Network;Settings;Security;
Keywords=DNS;DoT;TLS;보안;암호화;프라이버시;
EOF
```

등록 후 시작 메뉴 검색창에서 **"DNS"** 또는 **"보안"** 으로 검색하면 나타납니다.

### 설치 스크립트 한 번에 실행

```bash
# 이 저장소 클론 후 설치 스크립트 실행
git clone https://github.com/arbada84/linux-secret-dns.git
cd linux-secret-dns
bash install.sh
```

---

## 7. 파일 구조

```
linux-secret-dns/
├── README.md                  ← 이 문서
├── install.sh                 ← 원클릭 설치 스크립트
├── dns-dot-toggle             ← 켜기/끄기 토글 스크립트
├── config/
│   └── 10-dot.conf            ← systemd-resolved DoT 설정
└── desktop/
    └── dns-dot-toggle.desktop ← 시작 메뉴 등록 파일
```

---

## 8. 문제 해결

### DoT가 실제로 적용되었는지 확인

```bash
# 방법 1: resolvectl 확인
resolvectl status | grep -E "DNSOverTLS|Current DNS"
# 출력: +DNSOverTLS 와 1.1.1.1#cloudflare-dns.com 이 보이면 정상

# 방법 2: 쿼리 결과 확인
resolvectl query google.com
# "Data was acquired via local or encrypted transport: yes" → 암호화 사용 중

# 방법 3: 포트 확인
ss -tlnp | grep 853
# 또는
curl -s https://1.1.1.1/cdn-cgi/trace | grep tls
```

### 자주 묻는 질문

**Q: DoT를 켜면 속도가 느려지나요?**  
A: 처음 연결 시 TLS 핸드셰이크가 추가되지만, 연결이 유지되어 실사용에서는 차이를 느끼기 어렵습니다.

**Q: DNSSEC도 켜야 하나요?**  
A: DoT만으로도 충분합니다. DNSSEC은 일부 도메인과 충돌할 수 있어 `no`로 설정합니다.

**Q: VPN과 함께 써도 되나요?**  
A: VPN 사용 시 VPN이 DNS를 처리하므로 DoT 효과가 중복될 수 있습니다. VPN 없이 사용할 때 DoT가 효과적입니다.

**Q: 회사/학교 네트워크에서 작동하나요?**  
A: 일부 네트워크는 TCP 853 포트를 차단할 수 있습니다. 이 경우 `DNSOverTLS=opportunistic`으로 변경하면 실패 시 자동으로 평문 DNS를 사용합니다.

---

## 참고 자료

- [systemd-resolved 공식 문서](https://systemd.io/RESOLVED-VPNS/)
- [Cloudflare 1.1.1.1 DoT](https://developers.cloudflare.com/1.1.1.1/encryption/dns-over-tls/)
- [Quad9 DoT](https://www.quad9.net/service/service-addresses-and-features/)

---

*이 문서는 Linux Mint + systemd-resolved 환경 기준으로 작성되었습니다.*
