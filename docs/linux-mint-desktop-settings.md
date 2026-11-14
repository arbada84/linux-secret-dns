# Linux Mint 노트북의 터미널·한국어 설정 기록

확인일은 2026-11-15입니다. 아래 값은 노트북에서 읽은 값이며, MSI 데스크톱에 적용 완료했다는 뜻은 아닙니다. 공개 저장소에 필요한 항목만 기록했습니다. 전체 dconf, 홈 디렉터리, 연결 프로필, 인증 파일은 포함하지 않습니다.

## 현재 노트북 설정

| 항목 | 확인값 |
|------|--------|
| 배포판 | Linux Mint 22.3 Zena, Ubuntu Noble 기반 |
| Herdr | 0.9.5 비공식 한국어 UI 빌드 |
| Herdr 사용자 설정 | `~/.config/herdr/config.toml`의 `onboarding = false` |
| Ghostty | 1.3.1, 설치 패키지 `1.3.1-0~ppa2`, GTK 런타임 |
| Ghostty 언어 | `~/.config/ghostty/config.ghostty`의 `language = ko_KR` |
| 기본 터미널 alternative | `/usr/bin/gnome-terminal.wrapper` |
| `LANG` / `LANGUAGE` | `ko_KR.UTF-8` / `ko` |
| 이 작업 셸의 `LC_CTYPE`, `LC_MESSAGES` | `C.UTF-8` |
| 입력기 선택 | `~/.xinputrc`의 `run_im fcitx5` |
| 입력기 패키지 | fcitx5 `5.1.7-1build3`, fcitx5-hangul `5.1.1-1` |
| CJK 글꼴 패키지 | fonts-noto-cjk `1:20230817+repack1-3` |
| GNOME 입력 소스 설정 | `[('xkb', 'us'), ('xkb', 'kr+kr104')]` |
| Cinnamon 입력 소스 전환 키 | `['<Super>space', 'XF86Keyboard']` |
| GTK 테마 / 아이콘 테마 | `Mint-Y-Aqua` / `Mint-Y-Sand` |
| Cinnamon 창 테마 | `Mint-Y` |
| 인터페이스 글꼴 / 배율 | `Ubuntu 10` / `1.0` |

입력기 선택 파일, GNOME 입력 소스, 실행 중인 입력기는 서로 다른 정보입니다. `fcitx5-remote`는 확인 당시 `2`를 반환했지만, 실제 Herdr·Ghostty·XRDP 화면에서 한글 조합 입력이 정상이라는 증거로 사용하지 않았습니다.

`LANG`이 한국어여도 `LC_ALL`이나 개별 `LC_*`가 우선할 수 있습니다. 위 표처럼 작업 셸과 데스크톱 앱의 언어가 다를 수 있으므로 모든 앱이 한국어라고 가정하지 마십시오.

## 확인 명령

다음 명령은 설정을 읽습니다. 사용자 홈 전체를 내보내지 않습니다.

```bash
cat /etc/os-release
herdr --version
herdr status --json
ghostty --version
ghostty +validate-config
ghostty +show-config | rg '^language'
readlink /etc/alternatives/x-terminal-emulator
locale
gsettings get org.gnome.desktop.input-sources sources
gsettings get org.cinnamon.desktop.keybindings.wm switch-input-source
gsettings get org.cinnamon.desktop.interface gtk-theme
gsettings get org.cinnamon.desktop.interface icon-theme
gsettings get org.cinnamon.desktop.interface font-name
gsettings get org.cinnamon.desktop.interface text-scaling-factor
gsettings get org.cinnamon.desktop.wm.preferences theme
fcitx5-remote
```

이번 정리에서는 테마, 입력기, 기본 터미널, 부팅 대상, 절전, 네트워크와 원격 접속 설정을 변경하지 않았습니다. 기존 SSH·XRDP 기록은 [README의 원격 접속 절차](../README.md#ssh원격-데스크톱-설정)에 별도로 남아 있습니다. 해당 문서의 과거 확인 상태를 새 장치의 최신 상태로 간주하지 마십시오.

## Ghostty 한국어 메뉴 설정

기존 `~/.config/ghostty/config.ghostty`를 백업한 뒤 필요한 항목만 병합합니다. 이 저장소의 예시 파일로 기존 설정 전체를 덮어쓰지 마십시오.

```ini
language = ko_KR
```

`ghostty +validate-config`로 검사합니다. 노트북에는 `/usr/share/locale/ko_KR/LC_MESSAGES/com.mitchellh.ghostty.mo`가 존재합니다. 메뉴에 반영하려면 진행 중인 터미널 작업을 정리한 뒤 Ghostty를 완전히 종료하고 다시 실행합니다. 이번 작업에서는 강제 재시작하지 않았습니다.

Ghostty는 선택 사항입니다. Herdr를 사용하기 위해 기존 Mint 기본 터미널을 바꿀 필요가 없습니다. Ghostty 패키지 설치 후 기본 터미널이 바뀌었는지는 `readlink` 결과로 확인하십시오.

## 복원 자료와 공개 범위

Herdr 패치와 해시는 [Herdr 기록](../herdr/README.md), 새 장치의 빌드 및 이전 바이너리 복원 방법은 [빌드·복원 절차](../herdr/BUILD-AND-RESTORE.md)에 있습니다.

설정 예시는 필요한 항목만 수동 병합하는 자료입니다. 실제 Herdr 세션 파일, 대화 이력, SSH 개인키, API 토큰, 키링, Wi-Fi 비밀번호, 원격 접속 저장 비밀번호는 이 저장소에 포함하지 않았습니다. Linux Mint 노트북과 MSI 데스크톱의 역할·입력기·도구 버전이 다를 수 있으므로 자동 일괄 복원은 제공하지 않습니다.

## 참고

2026-11-15의 추가 원격 접속 설정은 [MSI 원격 접속 전 입력 초기화](remmina-msi-input-reset.md)에 기록했습니다. 노트북 아이콘 실행 직후 Caps Lock과 한글 입력을 해제하는 방법, Remmina 화면 설정, 검사 5개 결과, 남은 클립보드 경고와 복원 방법을 구분합니다. 이 추가 작업은 앞 절의 최초 조사 이후에 적용했습니다.

- [Ghostty language 설정](https://ghostty.org/docs/config/reference#language)
- [Herdr 원본 v0.9.5](https://github.com/herdrdev/herdr/tree/v0.9.5)
- [Herdr 설치 기록과 검증 범위](../herdr/manifest.json)
