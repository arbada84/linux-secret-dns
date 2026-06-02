# Linux Mint 유틸리티 모음

> Linux Mint 환경에서 직접 구현한 유틸리티 스크립트 모음입니다.

| 유틸리티 | 폴더 | 설명 |
|----------|------|------|
| SecretDNS | `/` | DoH + SNI 파편화로 ISP 감청 차단 |
| Transmission 필터 | `transmission/` | 토렌트 광고/스팸 파일 자동 제외 및 삭제 |
| Celluloid 플레이리스트 | `celluloid/` | 폴더 추가 시 자막 파일 자동 제거 |

---

# SecretDNS

> 길호넷 시크릿DNS 동등 기능을 Linux Mint에서 네이티브로 구현  
> ISP의 DNS 감청과 DPI 기반 사이트 감지를 동시에 차단합니다.

---

## 보호 원리

ISP(통신사)가 방문 사이트를 알 수 있는 두 가지 경로를 모두 차단합니다.

```
문제 ①: DNS 평문 전송
  사용자 → "youtube.com 알려줘" → ISP DNS → 응답
                   ↑ 평문, ISP가 기록/차단 가능

해결: DNS over HTTPS (dnscrypt-proxy)
  사용자 → dnscrypt-proxy → HTTPS/443 → Cloudflare
                              ↑ 일반 웹 트래픽과 구별 불가

---

문제 ②: SNI 평문 노출
  사용자 → HTTPS 시작 → ClientHello(SNI="youtube.com") → 서버
                          ↑ TLS 암호화 전, 평문 노출

해결: SNI 파편화 (tpws)
  ClientHello → TCP 패킷 분할 → ISP DPI가 SNI 조합 못 함
```

---

## 기능 비교

| 기능 | 시크릿DNS (Windows) | 본 프로젝트 (Linux) |
|------|-------------------|-------------------|
| DNS over HTTPS | ✅ | ✅ dnscrypt-proxy |
| SNI 파편화 | ✅ 핵심 기능 | ✅ zapret/tpws |
| 도메인 선택 적용 | ✅ | ✅ tpws 도메인 목록 |
| 실시간 DNS 로그 | ✅ | ✅ `/var/log/dnscrypt-proxy/query.log` |
| 켜기/끄기 토글 | ✅ | ✅ `secretdns on/off` |
| 시작 메뉴 등록 | ✅ | ✅ `.desktop` 파일 |
| DNS over TLS | — | ✅ 비활성 시 fallback |
| OS | Windows 전용 | **Linux Mint 네이티브** |

---

## 설치

### 원클릭 설치

```bash
git clone https://github.com/arbada84/linux-secret-dns.git
cd linux-secret-dns
bash install-secretdns.sh
```

### 수동 설치 순서

**1. 의존 패키지**

```bash
sudo apt-get install -y dnscrypt-proxy libcap-dev build-essential
```

**2. tpws 빌드**

```bash
git clone --depth=1 https://github.com/bol-van/zapret.git
cd zapret/tpws && make
sudo cp tpws /usr/local/bin/tpws
sudo useradd -r -s /usr/sbin/nologin tpws
```

**3. 설정 파일**

```bash
# DoH 설정 (dnscrypt-proxy)
sudo cp config/dnscrypt-proxy.toml /etc/dnscrypt-proxy/dnscrypt-proxy.toml

# DNS 라우팅 (systemd-resolved → dnscrypt-proxy)
sudo cp config/20-doh.conf /etc/systemd/resolved.conf.d/20-doh.conf

# SNI 파편화 도메인 목록
sudo mkdir -p /etc/zapret
sudo cp config/tpws-domains.txt /etc/zapret/tpws-domains.txt

# tpws systemd 서비스
sudo cp config/tpws.service /etc/systemd/system/tpws.service
```

**4. 서비스 시작**

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now dnscrypt-proxy.socket dnscrypt-proxy tpws
sudo systemctl restart systemd-resolved
```

**5. 토글 스크립트**

```bash
mkdir -p ~/bin
cp secretdns ~/bin/secretdns
chmod +x ~/bin/secretdns
```

---

## 사용법

```bash
# 상태 확인
secretdns status

# 켜기 (DoH + SNI 파편화 동시 활성)
secretdns on

# 끄기 (기본 DNS로 복원)
secretdns off

# 토글
secretdns toggle
```

### 상태 출력 예시

```
======================================
  Linux SecretDNS 상태
======================================

  [1] DNS over HTTPS (DoH)   : 🟢 켜짐 (DoH 활성)
      → dnscrypt-proxy → Cloudflare/Google/Quad9
        ISP에 DNS 쿼리가 노출되지 않음

  [2] SNI 파편화 (tpws)      : 🟢 켜짐 (SNI 파편화 활성)
      → TCP 80/443 패킷 분할
        ISP DPI 장비가 방문 사이트를 감지하지 못함

  ✅ 완전 보호 중: DNS 쿼리 + SNI 모두 차단됨
```

---

## 시작 메뉴 등록

시작 메뉴에서 **"SecretDNS"** 또는 **"보안"** 으로 검색하면 나타납니다.

수동 등록:
```bash
cp desktop/secretdns.desktop ~/.local/share/applications/
update-desktop-database ~/.local/share/applications/
```

---

## 파일 구조

```
linux-secret-dns/
├── README.md                    ← 이 문서
├── install-secretdns.sh         ← 원클릭 설치 (DoH + SNI 파편화)
├── install.sh                   ← 구버전 설치 (DoT 전용)
├── secretdns                    ← 통합 켜기/끄기 스크립트
├── dns-dot-toggle               ← DoT 전용 토글 (구버전)
├── config/
│   ├── dnscrypt-proxy.toml      ← DoH 설정 (dnscrypt-proxy)
│   ├── 20-doh.conf              ← resolved → dnscrypt-proxy 라우팅
│   ├── 10-dot.conf              ← DoT 설정 (DoH 꺼질 때 fallback)
│   ├── tpws-domains.txt         ← SNI 파편화 적용 도메인 목록
│   └── tpws.service             ← tpws systemd 서비스
└── desktop/
    └── secretdns.desktop        ← 시작 메뉴 등록 파일
```

---

## 시스템 구성도

```
┌─────────────────────────────────────────────────────┐
│                   Linux Mint                         │
│                                                      │
│  브라우저/앱                                          │
│      │ DNS 쿼리 (UDP 53)                             │
│      ▼                                              │
│  systemd-resolved (127.0.53:53)                     │
│      │                                              │
│      ▼                                              │
│  dnscrypt-proxy (127.0.2.1:53)  ← DoH 프록시        │
│      │ HTTPS (TCP 443)          ← 일반 트래픽과 동일 │
│      ▼                                              │
│  Cloudflare 1.1.1.1 / Google / Quad9               │
│                                                      │
│  브라우저/앱                                          │
│      │ HTTPS (TCP 443)                              │
│      ↓ iptables REDIRECT                            │
│  tpws (127.0.0.1:988)  ← SNI 파편화 프록시          │
│      │ SNI 분할 전송                                 │
│      ▼                                              │
│  실제 서버 (ISP DPI 우회 성공)                       │
└─────────────────────────────────────────────────────┘
```

---

## 문제 해결

### DoH 동작 확인

```bash
# dnscrypt-proxy 쿼리 로그 확인
sudo tail -f /var/log/dnscrypt-proxy/query.log

# DNS 응답 확인
dig @127.0.2.1 google.com +short
```

### 서비스 상태 확인

```bash
systemctl status dnscrypt-proxy
systemctl status tpws
```

### SNI 파편화 동작 여부 확인

```bash
# iptables 규칙 확인
sudo iptables -t nat -L OUTPUT | grep REDIRECT
```

---

## 보안 고려사항

- DoH는 TCP 443 사용 → ISP가 포트 차단 불가
- DoT(853)는 DoH 비활성 시 자동 fallback으로 동작
- tpws는 TCP 80/443만 처리 → 일반 트래픽 영향 없음
- iptables는 OUTPUT 체인만 → 로컬 트래픽만 처리
- SNI 도메인 목록(`tpws-domains.txt`)으로 선택적 적용 가능

---

## 참고 자료

- [zapret GitHub](https://github.com/bol-van/zapret)
- [dnscrypt-proxy GitHub](https://github.com/DNSCrypt/dnscrypt-proxy)
- [Cloudflare DoH](https://developers.cloudflare.com/1.1.1.1/encryption/dns-over-https/)
- [길호넷 시크릿DNS](https://secretdns.kilho.net/)

---

*Linux Mint + systemd-resolved + NetworkManager 환경 기준*

---

# Transmission 필터

> 토렌트 추가 시 광고·스팸 파일을 자동으로 제외하고, 다운로드 완료 후 잔여 파일을 삭제합니다.

## 파일

| 파일 | 역할 |
|------|------|
| `transmission/transmission-filter-unwanted-files.py` | 토렌트 추가 시 제외 파일 표시 |
| `transmission/transmission-cleanup-unwanted-files.py` | 다운로드 완료 후 제외 파일 삭제 |

## 제외 조건

`transmission-filter-unwanted-files.py`의 `should_skip()` 함수 기준:

- 파일 경로에 `996gg.cc` 포함 (광고 영상)
- `.url` 확장자 (광고 링크 파일)
- 파일명이 `offkab@sukebei.txt`

## 설치

```bash
# 스크립트 설치
cp transmission/transmission-filter-unwanted-files.py ~/.local/bin/
cp transmission/transmission-cleanup-unwanted-files.py ~/.local/bin/
chmod +x ~/.local/bin/transmission-filter-unwanted-files.py
chmod +x ~/.local/bin/transmission-cleanup-unwanted-files.py
```

Transmission 설정 → 편집 → **토렌트 추가 시 스크립트 실행** 에 `transmission-filter-unwanted-files.py` 등록  
**다운로드 완료 시 스크립트 실행** 에 `transmission-cleanup-unwanted-files.py` 등록

또는 RPC로 등록:

```bash
SESSION=$(curl -s -X POST http://127.0.0.1:9091/transmission/rpc 2>&1 | grep -o 'X-Transmission-Session-Id: [^<]*' | cut -d' ' -f2)
curl -s -X POST http://127.0.0.1:9091/transmission/rpc \
  -H "Content-Type: application/json" \
  -H "X-Transmission-Session-Id: $SESSION" \
  -d '{
    "method": "session-set",
    "arguments": {
      "script-torrent-added-enabled": true,
      "script-torrent-added-filename": "/home/사용자명/.local/bin/transmission-filter-unwanted-files.py",
      "script-torrent-done-enabled": true,
      "script-torrent-done-filename": "/home/사용자명/.local/bin/transmission-cleanup-unwanted-files.py"
    }
  }'
```

## 동작 원리

비트토렌트는 피스(조각) 단위로 다운로드하므로, 제외 표시만으로는 피스 경계에 걸친 파일이 부분적으로 생성됩니다.  
`transmission-cleanup-unwanted-files.py`가 다운로드 완료 후 이 잔여 파일을 자동 삭제합니다.

로그 확인:
```bash
tail -f ~/.config/transmission/filter-unwanted-files.log
```

---

# Celluloid 플레이리스트 자막 필터

> 폴더를 플레이리스트에 추가할 때 자막 파일(.srt, .ass 등)이 영상과 함께 섞여 들어가는 문제를 해결합니다.

## 파일

| 파일 | 역할 |
|------|------|
| `celluloid/filter-subtitles-from-playlist.lua` | 플레이리스트에서 자막 파일 자동 제거 |

## 설치

```bash
mkdir -p ~/.config/celluloid/scripts
cp celluloid/filter-subtitles-from-playlist.lua ~/.config/celluloid/scripts/
```

Celluloid 재시작 후 적용됩니다.

## 제거되는 자막 확장자

`.srt` `.ass` `.ssa` `.sub` `.vtt` `.smi` `.idx` `.sup` `.lrc`

> 자막 파일은 플레이리스트에서만 제거되며, 영상 재생 시 자동으로 불러와집니다.
