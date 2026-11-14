"""Apply a display-only Korean patch to the pinned Herdr v0.9.5 checkout."""
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parent.parent
assert (root / 'Cargo.toml').read_text().split('version = ', 1)[1].startswith('"0.9.5"')
pairs = '''settings|설정
keybinds|단축키
reload config|설정 다시 읽기
update ready|업데이트 준비됨
what's new|새 소식
detach|연결 해제
Rename|이름 변경
Close|닫기
New worktree|새 워크트리
Open worktree...|워크트리 열기...
Delete worktree checkout...|워크트리 폴더 삭제...
Close group|그룹 닫기
Expand|펼치기
Collapse|접기
New tab|새 탭
Rename pane|창 이름 변경
Clear pane name|창 이름 지우기
Swap with focused pane|선택한 창과 맞바꾸기
Split right|오른쪽으로 분할
Split down|아래로 분할
Zoom|확대
Use Herdr right-click menu|Herdr 우클릭 메뉴 사용
Send right-clicks to pane|창으로 우클릭 전달
Close pane|창 닫기
rename workspace|작업공간 이름 변경
new workspace|새 작업공간
new tab|새 탭
rename tab|탭 이름 변경
rename pane|창 이름 변경
 settings| 설정
agent status indicators|에이전트 상태 표시
choose color dots or distinct symbols for each state|상태를 나타낼 색상 점 또는 기호를 선택하세요
color dots  ● ● ● ○ ·|색상 점  ● ● ● ○ ·
distinct symbols  × ◐ ✓ ○ ·|상태 기호  × ◐ ✓ ○ ·
sound alerts|소리 알림
play sounds when agents change state in background|백그라운드 에이전트의 상태가 바뀌면 소리로 알립니다
on|켜기
off|끄기
notification popups|팝업 알림
choose where background popup notifications should appear|백그라운드 알림을 표시할 위치를 선택하세요
inside herdr|Herdr 안에 표시
via terminal|터미널 알림
via system|시스템 알림
 ↵ install | ↵ 설치 
 ↵ apply | ↵ 적용 
 esc close | esc 닫기 
 ↑↓ select  tab section| ↑↓ 선택  tab 항목 전환
agent integrations|에이전트 연동
enable session restore and, where supported, direct status updates|세션 복원과 지원되는 에이전트의 상태 보고를 활성화합니다
 loading integrations…| 연동 목록 불러오는 중…
 no integration targets available| 연동할 수 있는 에이전트가 없습니다
installed|설치됨
update available|업데이트 가능
available|설치 가능
not found|찾을 수 없음
 installing…| 설치 중…
what's new in this release|이번 버전의 새 소식
 scroll | 스크롤 
close|닫기
product announcement preview|제품 안내 미리보기
product announcement|제품 안내
 ↵ continue | ↵ 계속 
 ↵ save | ↵ 저장 
 ^c clear | ^c 지우기 
 esc cancel | esc 취소 
 Go to | 이동 
blocked|응답 필요
working|작업 중
idle|대기
done|완료
 / search agents and terminals| / 에이전트와 터미널 검색
terminal|터미널
terminals|터미널
 No matching agents or terminals| 일치하는 에이전트나 터미널이 없습니다
 search type · move ↑↓/ctrl+n/p · open enter · back esc| 입력 검색 · ↑↓/ctrl+n/p 이동 · enter 열기 · esc 뒤로
 ↑↓/j/k rows · ←→ workspace · / search · a/b/w/i/d filter · enter open · esc close| ↑↓/j/k 이동 · ←→ 작업공간 · / 검색 · a/b/w/i/d 필터 · enter 열기 · esc 닫기
 no matching keybinds| 일치하는 단축키가 없습니다
 esc back | esc 뒤로 
 / press / to filter by command or shortcut| / 명령이나 단축키로 검색하려면 /를 누르세요
 edit ←→/home/end · kill ^u/^k · yank ^y · scroll ↑↓ · back esc| ←→/home/end 편집 · ^u/^k 삭제 · ^y 붙이기 · ↑↓ 스크롤 · esc 뒤로
 search / · scroll j/k/↑↓/pgup/pgdn · close esc/enter| / 검색 · j/k/↑↓/pgup/pgdn 스크롤 · esc/enter 닫기
 ↵ confirm | ↵ 확인 
unset|미지정
 ERROR | 오류 
 PREFIX | 접두키 
 cancel  | 취소  
 send prefix  | 접두키 전송  
 workspace nav  | 작업공간 이동  
 keybinds| 단축키
 NAVIGATE | 이동 
 esc back  | esc 뒤로  
 workspace  | 작업공간  
 pane  | 창  
 RESIZE | 크기 조절 
 width  | 너비  
 height  | 높이  
 done| 완료
 COPY | 복사 
  enter search  esc cancel|  enter 검색  esc 취소
selecting|선택 중
select|선택
 exit| 나가기
 clear  q exit| 지우기  q 나가기
 move  | 이동  
 search  | 검색  
 repeat{match_status}  | 반복{match_status}  
 copy  | 복사  
 update ready| 업데이트 준비됨
 spaces| 작업공간
 new| 새로
menu|메뉴
theme|테마
indicators|상태 표시
sound|소리
toasts|팝업 알림
integrations|연동
copied to clipboard|클립보드에 복사됨
new worktree|새 워크트리
 branch| 브랜치
 checkout| 폴더
 creating…| 만드는 중…
 ↵ create and open | ↵ 만들고 열기 
open worktree|워크트리 열기
 / filter worktrees| / 워크트리 검색
{} checkouts|폴더 {}개
{}/{} checkouts|폴더 {}/{}개
 no matching worktrees| 일치하는 워크트리가 없습니다
 opening…| 여는 중…
 ↵ open | ↵ 열기 
 delete worktree checkout?| 워크트리 폴더를 삭제할까요?
 This removes the checkout folder:| 다음 워크트리 폴더를 삭제합니다:
 The branch is not deleted. The Herdr workspace will close.| 브랜치는 유지되며 Herdr 작업공간은 닫힙니다.
 Dirty or untracked files will be permanently deleted.| 수정한 파일과 미추적 파일도 영구 삭제됩니다.
 removing…| 삭제 중…
 ↵ delete anyway | ↵ 강제 삭제 
 ↵ remove | ↵ 삭제 
global|공통
prefix mode|접두키 모드
open notification target|알림 대상 열기
navigation|이동
back|뒤로
workspace list|작업공간 목록
move focus|선택 이동
cycle pane|창 순환
open workspace|작업공간 열기
switch workspace|작업공간 전환
workspaces / tabs|작업공간 / 탭
workspace navigation|작업공간 이동
session navigator|세션 탐색
delete worktree checkout|워크트리 폴더 삭제
close workspace|작업공간 닫기
previous workspace|이전 작업공간
next workspace|다음 작업공간
switch workspace 1-9|작업공간 1-9 전환
previous agent|이전 에이전트
next agent|다음 에이전트
focus agent 1-9|에이전트 1-9 선택
previous tab|이전 탭
next tab|다음 탭
move tab left|탭을 왼쪽으로
move tab right|탭을 오른쪽으로
switch tab 1-9|탭 1-9 전환
close tab|탭 닫기
panes|창
split vertical|좌우 분할
split horizontal|상하 분할
close pane|창 닫기
edit scrollback|스크롤 기록 편집
clear pane|창 지우기
copy mode|복사 모드
zoom pane|창 확대
resize mode|크기 조절 모드
resize pane left|창 왼쪽 크기 조절
resize pane down|창 아래쪽 크기 조절
resize pane up|창 위쪽 크기 조절
resize pane right|창 오른쪽 크기 조절
toggle sidebar|사이드바 표시 전환
focus pane left|왼쪽 창 선택
focus pane down|아래 창 선택
focus pane up|위 창 선택
focus pane right|오른쪽 창 선택
cycle pane next|다음 창 순환
cycle pane previous|이전 창 순환
last pane|마지막 창
custom|사용자 지정
custom command|사용자 지정 명령
  terminal workspace manager for coding agents|  코딩 에이전트를 위한 터미널 작업공간
  this is a mouse-first terminal.|  마우스로 편리하게 조작하는 터미널입니다.
  click the sidebar to switch workspaces, drag pane|  사이드바로 작업공간 전환, 창 테두리 드래그로
  borders to resize, right-click for context menus.|  크기 조절, 우클릭으로 메뉴를 열 수 있습니다.
 enters prefix mode · | 접두키 모드 · 
 shows keybinds and settings| 단축키와 설정 보기
  next: install optional agent integrations for more reliable state|  다음: 정확한 상태 표시를 위해 에이전트 연동을 설치하세요
agents|에이전트
 agents| 에이전트
 no matching agents| 일치하는 에이전트가 없습니다
grouped|작업공간순
priority|우선순위순
 machines| 컴퓨터
 new · {}| 새로 · {}
● menu|● 메뉴
! auth|! 인증
! error|! 오류
 no workspace| 작업공간 없음
switch|전환
connecting|연결 중
online|연결됨
reconnecting|다시 연결 중
attention|확인 필요
disabled|비활성
tab {label}|탭 {label}
tab {label} · {}/{}|탭 {label} · {}/{}
 no agents| 에이전트 없음
 all idle| 모두 대기 중
 switch| 전환
machines|컴퓨터
agents · {label}|에이전트 · {label}
  no matching agents|  일치하는 에이전트가 없습니다
spaces|작업공간
  + new workspace|  + 새 작업공간
tabs|탭
  + new tab|  + 새 탭
tab {}|탭 {}
1 pane|창 1개
{pane_count} panes|창 {pane_count}개
{} workspaces, {panes}|작업공간 {}개, {panes}
Close worktree group?|워크트리 그룹을 닫을까요?
Close workspace?|작업공간을 닫을까요?
Close target changed; try closing it again|닫을 대상이 바뀌었습니다. 다시 시도하세요'''
translations = dict(line.split('|', 1) for line in pairs.splitlines())
files = ['src/client/shell/' + name + '.rs' for name in (
    'global_menu', 'context_menu', 'settings_overlay', 'overlays', 'render',
    'sidebar', 'state', 'worktree_overlays', 'agent_sidebar', 'endpoint_sidebar',
    'mobile', 'overlay_input')]
files += ['src/input/keybind_help.rs', 'src/ui/onboarding.rs', 'src/ui/widgets.rs']
literal = re.compile(r'"((?:[^"\\]|\\.)*)"')
count = 0
for name in files:
    path = root / name
    source = path.read_text()
    def replace(match):
        global count
        text = match.group(1)
        if text not in translations:
            return match.group(0)
        # Keep Rust formatting arguments intact, including repeated placeholders.
        translated = translations[text]
        assert sorted(re.findall(r'\{[^}]*\}', text)) == sorted(re.findall(r'\{[^}]*\}', translated)), text
        count += 1
        return json.dumps(translated, ensure_ascii=False)
    path.write_text(literal.sub(replace, source))
print(f'Translated {count} display literals in {len(files)} files')
