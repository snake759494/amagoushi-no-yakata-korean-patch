import sys,time,json,uuid,subprocess,os
sys.path.insert(0,os.path.dirname(__file__))
import ppx
w=ppx.conn()
dur=float(sys.argv[1]); every=float(sys.argv[2]); prefix=sys.argv[3]; btn=sys.argv[4] if len(sys.argv)>4 else 'circle'
t0=time.time(); k=0; last=0
while time.time()-t0<dur:
    ppx.call(w,'input.buttons.press',button=btn,duration=3); time.sleep(0.25)
    if time.time()-last>every:
        last=time.time(); ppx.shot(w,'%s_%02d.png'%(prefix,k)); k+=1
w.close()
