from pathlib import Path
import json
root=Path(__file__).resolve().parent
target='한글 입력 테스트'
print('Ghostty 한글 입력 테스트 · IBus 호환 연결')
print('기존 Herdr와 다른 창입니다. 기존 작업은 그대로 유지됩니다.')
print('한글 입력으로 전환하고 아래 문장을 붙여넣지 말고 직접 입력한 뒤 Enter를 누르세요.')
print('입력할 문장: '+target+'\n')
try:
 value=input('> ')
 result={'matches':value==target,'received_length':len(value),'expected_length':len(target)}
 (root/'result.json').write_text(json.dumps(result))
 print('\n결과: '+('정상 — 입력 문장이 일치합니다.' if result['matches'] else '불일치 — 한글 입력 문제가 남아 있거나 문장이 다릅니다.'))
 input('Enter를 누르면 이 테스트 창만 닫힙니다. ')
except (EOFError,KeyboardInterrupt):
 pass
