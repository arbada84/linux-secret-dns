# MSI 원격 접속 전에 노트북 입력을 영문으로 초기화하기

2026-11-15 노트북에서 MSI 데스크톱에 접속하는 설정을 기록합니다. 노트북은 Fcitx5, MSI의 XRDP 세션은 IBus Hangul을 사용합니다. 다른 입력기나 Wayland 환경에 그대로 적용하지 마세요.

## 적용한 동작

원격 데스크톱 아이콘은 Remmina를 열기 전에 노트북 Caps Lock을 끄고 `fcitx5-remote -c`로 한글 입력을 해제합니다. 비밀번호 입력창도 영문 소문자 상태에서 시작하도록 한 순서입니다. Shift를 누르면 대문자가 입력되며, 접속 후 한영 전환은 계속 사용할 수 있습니다.

Remmina의 `precommand`는 접속 직전에 같은 노트북 초기화를 다시 실행합니다. 이어서 기존 SSH 연결을 통해 MSI의 Caps Lock과 IBus 시작 모드를 초기화합니다. IBus의 `initial-input-mode`는 `latin`으로 저장합니다. 이미 Hangul 엔진이 실행 중이면 영문 엔진을 거쳐 Hangul 엔진을 다시 선택합니다.

이 스크립트는 Num Lock을 직접 변경하지 않습니다. RDP 자체의 키보드 상태 동기화는 별개입니다. Caps Lock과 한글을 항상 금지하는 기능이 아니며, 접속 시점에만 초기화합니다.

## 파일 설치하기

기존 파일이 있다면 먼저 백업하고 내용을 비교하세요. 공개 저장소에는 실제 연결 프로필, 저장 비밀번호, 키링, SSH 개인키를 넣지 않았습니다.

저장소 루트에서 실행합니다.

```bash
mkdir -p ~/.local/lib/msi-rdp
install -m 644 remmina/prepare_input.py ~/.local/lib/msi-rdp/prepare_input.py
install -m 644 remmina/test_prepare_input.py ~/.local/lib/msi-rdp/test_prepare_input.py
python3 ~/.local/lib/msi-rdp/test_prepare_input.py
```

필요한 도구는 Python 3, libX11, Fcitx5와 `fcitx5-remote`, OpenSSH 클라이언트, Remmina입니다. MSI에는 Python 3, Xorg, IBus Hangul과 `gsettings`가 필요합니다. 기존 `msi-vpn` SSH 별칭은 키 인증과 호스트 키 검증이 가능한 상태여야 합니다. 인증 비밀은 이 저장소에서 제공하지 않습니다.

MSI 초기화는 로그인한 사용자 소유의 Xorg 화면이 정확히 하나일 때만 실행합니다. 세션이 없거나 여러 개면 임의 화면을 고르지 않습니다. SSH 준비 실패는 오류를 출력하지만 RDP 인증 자체를 차단하지 않습니다. 원격 초기화에는 최대 15초 제한이 있습니다.

## 기존 연결과 아이콘에 연결하기

세 연결 프로필의 실제 위치는 다음과 같습니다.

- `~/.local/share/remmina/msi-lan.remmina`
- `~/.local/share/remmina/msi-vpn.remmina`
- `~/.local/share/remmina/remote-192-168-31-91.remmina`

기존 프로필의 비밀번호와 인증서 설정을 보존하고 아래 항목만 병합합니다. `/home/사용자명`은 노트북의 실제 홈 경로로 바꾸세요. `.remmina` 파일 안에서는 `~` 확장에 의존하지 않습니다.

```ini
colordepth=24
resolution_mode=0
resolution_width=1920
resolution_height=1080
quality=0
keyboard_grab=0
precommand=/usr/bin/python3 /home/사용자명/.local/lib/msi-rdp/prepare_input.py
```

기존 `precommand`가 있다면 덮어쓰지 말고 기존 동작과 함께 실행하도록 검토하세요. 변경할 때 Remmina를 정상 종료하면 메모리에 남은 옛 프로필이 다시 저장되는 일을 피할 수 있습니다. XRDP 로그아웃이나 서버 재시작은 필요하지 않습니다.

바탕화면 `.desktop` 파일의 `Exec`를 해당 프로필 이름에 맞춥니다.

```ini
Exec=/usr/bin/python3 /home/사용자명/.local/lib/msi-rdp/prepare_input.py --connect msi-lan
```

VPN 아이콘은 마지막 인자를 `msi-vpn`으로, 별도 Wi-Fi 아이콘은 `remote-192-168-31-91`로 바꿉니다. 스크립트는 이 세 이름만 받습니다. 아이콘은 기존 실행 권한과 신뢰 설정을 유지하세요. 이 연결 밖에서 Remmina를 빠른 접속 URI로 열면 초기화가 실행되지 않을 수 있습니다.

현재 MSI는 Wi-Fi를 사용합니다. 기존 LAN 프로필의 유선 주소는 접속되지 않아 현재 Wi-Fi 주소로 바꿨습니다. 이 주소는 DHCP로 달라질 수 있으므로 새 장치에서는 실제 주소를 확인하세요. 다른 공유기에서는 검증된 VPN 프로필을 사용합니다. 서버 IP와 비밀번호를 스크립트에 넣지 않습니다.

## 확인하기

다음 명령은 실제 노트북 입력 상태를 바꿉니다. 입력 중인 작업을 마친 뒤 실행하세요.

```bash
python3 ~/.local/lib/msi-rdp/prepare_input.py --local-input
fcitx5-remote
xset q
```

`fcitx5-remote`의 `1`은 입력기 비활성 상태를 뜻합니다. `xset q`의 `Caps Lock`은 `off`여야 합니다. 실제 문자를 자동 입력하거나 비밀번호를 수집하지 않습니다.

검증 결과는 다음과 같습니다.

- 검사 5개 통과. 화면 식별, 모호한 세션 거부, Caps Lock만 변경, 초기화 후 Remmina 실행 순서, 미허용 프로필 거부를 확인했습니다.
- 노트북 Fcitx5 비활성과 양쪽 Caps Lock 꺼짐을 확인했습니다.
- 연결 전 초기화 메시지 `LOCAL_AND_REMOTE_INPUT_RESET_OK`를 확인했습니다.
- 설정 보완 뒤 기존 MSI Xorg 세션으로 로그인 성공했고, 1920×1080을 유지했습니다. 실행 중이던 원격 앱을 종료하지 않았습니다.
- 마지막 아이콘 실행 순서 보완 뒤에는 해당 아이콘을 직접 눌러 비밀번호를 입력하는 시험을 추가로 하지 않았습니다.

## 남은 문제와 되돌리기

비밀번호 화면 멈춤의 직접 원인은 확정하지 못했습니다. 최근 로그인 성공을 모든 재발 해결의 증거로 사용하지 않습니다. CPU와 메모리 부족은 관찰되지 않았지만 체감 속도 개선은 계측하지 않았습니다.

Remmina 로그에는 GTK 경고와 클립보드 응답 6초 대기가 남았습니다. 복사·붙여넣기를 보존하려고 클립보드 공유를 임의로 끄지 않았습니다. TLS와 호스트 키 검증, 화면 잠금과 비밀번호 요구를 해제하지 않았습니다.

노트북의 기존 프로필 백업은 `~/.local/state/msi-rdp/20261115-before/`에 있습니다. 공개 저장소에는 올리지 않습니다. 되돌릴 때는 Remmina를 정상 종료한 뒤 필요한 프로필만 복원하고 아이콘의 `Exec`를 원래 `remmina --connect=프로필절대경로`로 돌립니다. IBus 시작 모드의 종전 값은 `hangul`이었습니다. 이를 복원하려면 MSI 사용자 환경에서 다음을 실행합니다.

```bash
gsettings set org.freedesktop.ibus.engine.hangul initial-input-mode hangul
```

## 참고

- [Remmina 연결 설정](https://remmina.gitlab.io/remminadoc.gitlab.io/md__builds__remmina_remmina_ci__remmina_wiki__remmina__config__file__options.html)
- [노트북의 기존 민트 설정 기록](linux-mint-desktop-settings.md)
