import json,unicodedata
from pathlib import Path
x=input()
Path('/tmp/ghostty-ime-repro-14w19e0m/fcitx-result.json').write_text(json.dumps({"received":x,"codepoints":[hex(ord(c)) for c in x],"normalized_match":unicodedata.normalize("NFC",x).strip()=="한글 입력 테스트"},ensure_ascii=False))
