import os,subprocess,time,json,shutil
from pathlib import Path
root=Path(__file__).resolve().parent
config=root/'config';config.mkdir(exist_ok=True);(config/'fcitx5').mkdir(exist_ok=True)
for name in ['profile','config']:
 src=Path('~/.config/fcitx5')/name
 if src.exists():shutil.copy2(src,config/'fcitx5'/name)
(config/'fcitx5/conf').mkdir(exist_ok=True);shutil.copy2('~/.config/fcitx5/conf/hangul.conf',config/'fcitx5/conf/hangul.conf')
env=os.environ.copy();
for k in ['SESSION_MANAGER','DESKTOP_STARTUP_ID','XDG_ACTIVATION_TOKEN','GNOME_DESKTOP_SESSION_ID']:env.pop(k,None)
env.update(XDG_CURRENT_DESKTOP='',DESKTOP_SESSION='',GTK_A11Y='none',XDG_CONFIG_HOME=str(config),XDG_CACHE_HOME=str(root/'cache'),XDG_DATA_HOME=str(root/'data'),XDG_RUNTIME_DIR=str(root/'runtime'),LIBGL_ALWAYS_SOFTWARE='1',GIO_USE_VFS='local',GTK_USE_PORTAL='0',GSETTINGS_BACKEND='memory',NO_AT_BRIDGE='1')
Path(env['XDG_RUNTIME_DIR']).mkdir(mode=0o700,exist_ok=True)
procs=[]
def run(argv,**kw):return subprocess.run(argv,env=env,capture_output=True,text=True,timeout=10,**kw)
try:
 r,w=os.pipe()
 log=(root/'display.log').open('wb')
 xvfb=subprocess.Popen(['Xvfb','-displayfd',str(w),'-screen','0','1280x800x24','-nolisten','tcp','-ac'],pass_fds=(w,),stdout=log,stderr=log);procs.append(xvfb);os.close(w)
 display=os.read(r,30).decode().strip();os.close(r);env['DISPLAY']=':'+display
 log2=(root/'fcitx.log').open('wb');fcitx=subprocess.Popen(['fcitx5'],env=env,stdout=log2,stderr=log2);procs.append(fcitx)
 wm_log=(root/'wm.log').open('wb');wm=subprocess.Popen(['/usr/bin/muffin','--sm-disable'],env=env,stdout=wm_log,stderr=wm_log);procs.append(wm)
 time.sleep(2)
 results=[]
 for module in ['fcitx']:
  env['GTK_IM_MODULE']=module
  result=root/(module+'-result.json')
  script=root/(module+'-input.py')
  script.write_text('import json,unicodedata\nfrom pathlib import Path\nx=input()\nPath('+repr(str(result))+').write_text(json.dumps({"received":x,"codepoints":[hex(ord(c)) for c in x],"normalized_match":unicodedata.normalize("NFC",x).strip()=="한글 입력 테스트"},ensure_ascii=False))\n')
  err=(root/(module+'-ghostty.log')).open('wb')
  ghostty=subprocess.Popen(['/usr/bin/ghostty','--config-default-files=false','--gtk-single-instance=false','--title=IME-'+module,'-e','/usr/bin/python3',str(script)],env=env,stdout=err,stderr=err);procs.append(ghostty)
  window=None
  for _ in range(150):
   p=run(['xdotool','search','--name','IME-'+module])
   if p.returncode==0 and p.stdout.strip():window=p.stdout.splitlines()[-1];break
   if ghostty.poll() is not None:break
   time.sleep(.1)
  if not window:
   results.append({'module':module,'status':'window_not_created','exit':ghostty.poll()});continue
  run(['xdotool','windowfocus','--sync',window]);time.sleep(.5)
  run(['fcitx5-remote','-s','hangul']);run(['fcitx5-remote','-o']);time.sleep(.4)
  run(['xdotool','type','--clearmodifiers','--delay','120','gksrmf dlqfur xptmxm'])
  run(['xdotool','key','Return'])
  for _ in range(30):
   if result.exists():break
   time.sleep(.1)
  results.append({'module':module,'status':'captured' if result.exists() else 'no_input_result','result':json.loads(result.read_text()) if result.exists() else None})
  if ghostty.poll() is None:ghostty.terminate();ghostty.wait(timeout=5)
 (root/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2));print(json.dumps(results,ensure_ascii=False))
finally:
 for p in reversed(procs):
  if p.poll() is None:
   p.terminate()
   try:p.wait(timeout=5)
   except subprocess.TimeoutExpired:p.kill();p.wait()
