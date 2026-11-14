from pathlib import Path
import json,unicodedata
root=Path(__file__).resolve().parent
target='한글 입력 테스트'
def normalize(value):return unicodedata.normalize('NFC',value).strip()
assert normalize(target+' ')==target
assert normalize('한 입력 테스트')!=target
print('Ghostty 한글 조합 분리 테스트')
print('이번에는 조합 중 글자가 입력기 쪽에서 표시될 수 있습니다.')
print('한글 모드로 전환하고 붙여넣지 말고 직접 입력해주세요: '+target)
try:
 value=input('> ')
 result={'matches':normalize(value)==target,'received_length':len(value),'normalized_length':len(normalize(value)),'expected_length':len(target)}
 (root/'result.json').write_text(json.dumps(result))
 print('결과: '+('정상' if result['matches'] else '입력 차이 있음'))
 print('화면 확인용 수신 내용: '+repr(value))
 input('Enter를 누르면 이 테스트 창만 닫힙니다. ')
except (EOFError,KeyboardInterrupt):pass
