from pathlib import Path
import json,unicodedata
root=Path(__file__).resolve().parent
target='한글 입력 테스트'
print('Ghostty 1.2.3 — 버전 비교 전용 창')
print('기존 설치본과 Herdr 작업은 유지됩니다.')
print('한글로 전환해서 붙여넣지 말고 직접 입력한 뒤 Enter: '+target)
try:
 value=input('> ')
 normalized=unicodedata.normalize('NFC',value).strip()
 (root/'input-result.json').write_text(json.dumps({'matches':normalized==target,'normalized_length':len(normalized),'expected_length':len(target)}))
 print('결과: '+('정상' if normalized==target else '입력 차이 있음'))
 print('화면 확인용 수신 내용: '+repr(value))
 input('Enter를 누르면 이 비교 창만 닫힙니다. ')
except (KeyboardInterrupt,EOFError):pass
