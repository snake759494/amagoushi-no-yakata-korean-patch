"""Robust PPSSPP driver: python ppx.py iso ACTIONS...  actions: start/circle/.. , wN (sleep), s:NAME (screenshot)"""
import websocket,json,sys,time,uuid,subprocess,base64,os
def conn():
    for _ in range(60):
        try: return websocket.create_connection('ws://127.0.0.1:49742/debugger',subprotocols=['debugger.ppsspp.org'],timeout=10)
        except Exception: time.sleep(1)
    raise SystemExit('no debugger')
def call(w,event,**a):
    t=str(uuid.uuid4()); w.send(json.dumps(dict(event=event,ticket=t,**a)))
    end=time.time()+10
    while time.time()<end:
        try: r=json.loads(w.recv())
        except websocket.WebSocketTimeoutException: break
        if r.get('ticket')==t or (event in('cpu.stepping','cpu.resume') and r.get('event')==event): return r
    return None
def press(w,b,dur=8): call(w,'input.buttons.press',button=b,duration=dur); time.sleep(0.9)
def shot(w,path):
    for _ in range(4):
        r=subprocess.run([sys.executable,os.path.join(os.path.dirname(__file__),'shot.py'),path],capture_output=True,timeout=60)
        if os.path.exists(path) and time.time()-os.path.getmtime(path)<30: return
        time.sleep(1)
    print('SHOT FAILED',path)
def main():
    args=sys.argv[1:]
    if args and args[0].endswith('.iso'):
        subprocess.run(['taskkill','/F','/IM','PPSSPPWindows64.exe'],capture_output=True); time.sleep(2)
        subprocess.Popen([r'D:\psp\ppsspp_win\PPSSPPWindows64.exe',os.path.abspath(args[0])])
        time.sleep(6); args=args[1:]
    w=conn()
    for a in args:
        if a.startswith('w'): time.sleep(float(a[1:]))
        elif a.startswith('s:'): shot(w,a[2:]); print('shot',a[2:],flush=True)
        else:
            n=1
            if '*' in a: a,n=a.split('*'); n=int(n)
            for _ in range(n): press(w,a)
    w.close()
if __name__=="__main__": main()
