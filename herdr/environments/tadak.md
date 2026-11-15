# MSI의 타닥 Herdr 환경

2026-11-15에 노트북의 타닥 개발 자료를 MSI로 복사하고 Codex·Claude 두 창을 구성한 기록입니다. 자료 복사 완료와 에이전트의 실제 대화 재개 완료를 구분합니다. 이 문서는 공개용 설정 기록이며 실제 대화 파일, 대화 UUID, 인증 정보와 서버 접속 주소를 포함하지 않습니다.

## 현재 구성

| 항목 | 노트북 | MSI |
|------|--------|-----|
| Herdr | 0.9.5 비공식 한국어 UI | 기존 0.8.8 서버 유지 |
| 작업공간 | 타닥, Codex·Claude 두 창 | 타닥, 좌우 Codex·Claude 두 창 |
| 프로젝트 | `/mnt/win_d/Projects/tadak-keyboard` | `~/Projects/tadak-keyboard` |
| Codex 역할 | 기존 작성·구현 대화 | `tadak-codex`, 구현 담당으로 분기 시작 |
| Claude 역할 | 기존 독립 검토 대화 | `tadak-claude`, 기존 대화를 분기하여 검토 담당으로 시작 |
| 원본 보존 | 기존 프로젝트·대화·세션 유지 | 검증 보관본과 독립 작업본 분리 |

MSI의 Herdr 서버를 업그레이드하거나 교체하지 않았습니다. 노트북의 0.9.5 전용 한국어 UI 패치를 MSI의 0.8.8에 적용하지 않았으므로 UI·프로토콜까지 동일한 환경은 아닙니다.

당시 MSI 작업공간은 `w2`, 탭은 `w2:t1`, 왼쪽 Codex는 `w2:p1`, 오른쪽 Claude는 `w2:p2`였습니다. 이 ID는 해당 서버의 당시 값이며 다른 장치의 같은 ID와 무관합니다. 다시 구성할 때 조회 결과를 사용합니다.

## 디렉터리와 보존 범위

| 위치 | 용도 |
|------|------|
| `~/Projects/tadak-keyboard` | 새 독립 개발 작업본 |
| `~/.migration/20261115-tadak-laptop-copy` | 검증한 보존 복사본 |
| 보존본의 `payload/mnt/win_d/Projects/tadak-keyboard` | 노트북 프로젝트 복사본 |
| 보존본의 `payload/` | 원래 절대 경로에서 첫 `/`를 뺀 구조의 외부 SDK·모델·캐시·개발 데이터 |
| 보존본의 `exports/` | 프로젝트 관련 작업 이력 스냅샷과 인수인계 |
| 보존본의 `control/copy-result.json` | 전송·검증 완료 기록 |
| `~/.local/state/tadak-continuity-20261115/` | 에이전트 연결·경로 보완·초기 설정 대기 기록 |

별도 작업본은 `cp -a --reflink=auto --sparse=always`로 만들었습니다. 보존본과 작업본의 `.git/HEAD`는 다른 파일이며 내용이 일치하는 것을 확인했습니다. Git dirty·미추적 자료를 포함해 원본을 보존했습니다. 작업본을 만들기 위해 reset, clean, 전체 add나 일괄 커밋을 수행하지 않았습니다.

기존 자료 복사는 일반 파일 870,998개, 디렉터리 79,090개, 심볼릭 링크 735개를 포함합니다. 논리 용량은 301,056,758,682바이트입니다. 전체 내용 체크섬 대조에서 내용 불일치가 없었고, 원본·대상 각각 950,823개 항목의 메타데이터 검사를 통과했습니다. 변경된 한 이력 파일의 수정 시각은 내용 해시를 확인한 뒤 대상에 맞췄고, 원래 실패 기록과 보완 증거도 유지했습니다.

## 두 에이전트와 이력 연결

MSI의 기존 Codex·Claude 설치를 확인했습니다. 최초 상태 조회에서는 Claude 로그인이 표시됐지만, 후속 재조회에서는 `loggedIn: false`로 확인돼 현재 사용자 로그인이 필요합니다. Codex·Claude가 실제 대화에 응답한 상태는 아직 확인하지 않았습니다. 계정 인증 파일이나 SSH 개인키를 노트북에서 추가 복사하지 않았습니다.

타닥 관련 Codex 세션 121개를 `~/.codex/sessions/`에 복사했고, 현재 대화는 전송 이후 내용까지 스냅샷을 갱신했습니다. Claude의 타닥 프로젝트 대화 파일은 `~/.claude/projects/<MSI-작업폴더-키>/`에 복사했습니다. 대표 Codex·Claude 이력 파일의 양쪽 SHA-256이 일치하는 것을 확인했습니다. 원래 이력 내부의 과거 경로는 기록의 일부로 남겼습니다.

Codex는 `fork`, Claude는 `--resume`과 `--fork-session`으로 시작했습니다. 실제 대화 ID는 비공개 이관 기록에서 확인하며 공개 문서에 적지 않습니다. 아래는 사용한 명령 형식입니다. 재실행용 자동 설치 명령이 아닙니다.

```bash
codex fork "$CODEX_PARENT_SESSION_ID" --cd "$HOME/Projects/tadak-keyboard"
claude --resume "$CLAUDE_PARENT_SESSION_ID" --fork-session
```

Herdr에서는 `타닥` 작업공간을 만든 후 같은 경로의 창을 오른쪽으로 1:1 분할하고 `tadak-codex`, `tadak-claude`로 시작했습니다. 기존 홈 작업공간과 노트북 세션은 종료하지 않았습니다. 탭 이름은 `Codex · Claude`입니다.

두 에이전트의 첫 안내는 `MSI-AGENT-HANDOFF.md`와 `SESSION-SUMMARY.md` 상단을 읽고 상태를 확인한 후 대기하는 것입니다. 기존 개발 요청을 무조건 자동 재개하지 않습니다. Codex가 구현을 담당하고 Claude가 검토를 담당하며 같은 파일을 동시에 수정하지 않습니다.

## pstack과 REA

보존한 pstack 0.15.36의 스킬 58개를 프로젝트 `.agents/skills/`와 `.claude/skills/`에서 읽을 수 있도록 연결했습니다. 링크 이름은 `pstack-스킬이름` 형태입니다. 다른 프로젝트나 전역 provider·예산 설정은 바꾸지 않았습니다. 링크 대상은 보존본 안의 다음 경로입니다.

```text
payload/home/arbada/.codex/plugins/cache/cursor-plugins/pstack/0.15.36/skills
```

프로젝트 `.codex/config.toml`의 REA 실행 파일·스크립트·환경 경로는 MSI 보존본 안의 도구 경로로 보완했습니다. 기존 노트북 경로 설정은 `~/.local/state/tadak-continuity-20261115/config.toml.laptop-paths`에 보관했습니다.

Node 실행 파일, `rea.mjs`, `JAVA_HOME`, `REA_JADX_MCP_JAR` 네 경로가 존재하는 것을 확인했습니다. 이 확인은 MCP 연결·REA 역공학 기능·Android 빌드의 실행 성공을 의미하지 않습니다. 에이전트의 최초 설정을 마친 뒤 프로젝트 설정을 다시 읽고 MCP 연결을 검증해야 합니다.

외부 SDK·모델·가상환경의 절대 링크와 실행 스크립트는 여전히 노트북 경로를 포함할 수 있습니다. 이전 PID, ADB 포트, snapshot, 실행 소유권 epoch를 MSI에서 재사용하지 않습니다. 개발 서명을 새 키로 교체하지 않습니다.

## 실제 확인 상태

| 항목 | 2026-11-15 확인 결과 |
|------|-------------------|
| 원본 자료 전송·내용 체크섬·메타데이터 | 통과 |
| 독립 작업본·공동 인수인계 | 생성 완료 |
| 두 에이전트 프로세스와 Herdr 배치 | 생성 확인 |
| Codex·Claude 이력 파일 전송 | 대표 파일 해시 일치 |
| Codex 시작 화면 | 새 작업 폴더 신뢰 확인 대기 |
| Claude 시작 화면 | 최초 실행 테마 선택 대기. 후속 인증 조회는 로그인 미완료 |
| 이전 대화를 실제 로딩한 뒤 응답 | 아직 미확인 |
| REA MCP·Android 빌드·에뮬레이터 실행 | 이번 구성에서 미검증 |

Herdr 0.8.8의 `idle`·`interactive_ready` 표시는 최초 실행 화면에서도 관찰됐습니다. 준비 완료 판정은 해당 표시만으로 내리지 않고 실제 터미널 내용과 응답을 확인합니다. 승인·질문 화면을 임의로 선택하지 않았습니다. 사용자 확인 요청은 대기 상태로 남겼습니다.

## 개발 상태와 남은 확인

인수인계 기준 개발본은 Main107입니다. 빌드·정적 검증과 API35 기본 입력 100회, 기존 Main347/Test2 데이터·설정 복구 및 에뮬레이터 정상 정지 기록이 있습니다. 앱 전체 완료 판정은 아닙니다. 일반 AI 품질, 실물/OEM·실제 수신 앱, 전체 16ms 목표는 미완료입니다.

재개할 에이전트는 프로젝트의 `AGENTS.md`, `CLAUDE.md`가 있으면 읽고 `SESSION-SUMMARY.md`, `docs/product/RECOVERY-20261114-DEV107.md`, `.planning/quick/20261111-antigravity-completion/dev97-sticker-chain/CURRENT-WORK.json`을 대조합니다. 오래된 `next` 문장을 그대로 실행하지 말고 최신 종결 상태와 검증 증거를 확인합니다.

현재 남은 환경 확인은 최초 실행 선택과 Claude 사용자 로그인, 두 대화의 실제 분기 로딩, 현재 경로 인식, pstack 인식, REA 연결과 개발 도구 경로 점검입니다. Gemini·Antigravity 신규 호출·재시도, 새 유료 API·예산 변경, 운영 서비스·큐·DB 실행은 하지 않습니다. 이 기록을 앱 완성이나 MSI 주 작업본 전환 완료로 해석하지 않습니다.

## 관련 자료

- [Herdr 설정과 한국어 UI 기록](../README.md)
- [두 에이전트 협업 절차](../AGENT-WORKFLOW.md)
- [Mint 데스크톱 설정 기록](../../docs/linux-mint-desktop-settings.md)
