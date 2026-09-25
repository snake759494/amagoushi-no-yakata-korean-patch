import sys,json,uuid
sys.path.insert(0,'tools')
from ppsspp_rpc import Debugger
d=Debugger()
addr=int(sys.argv[1],16); n=int(sys.argv[2]); regsel=sys.argv[3].split(',')
press=sys.argv[4] if len(sys.argv)>4 else None
d.call('cpu.breakpoint.add',address=addr,enabled=True)
if press:
    t=str(uuid.uuid4()); d.w.send(json.dumps({'event':'input.buttons.press','button':press,'duration':8,'ticket':t}))
d.w.settimeout(float(__import__("os").environ.get("BPT","15")))
got=0
try:
  while got<n:
    r=json.loads(d.w.recv())
    if r.get('event')=='cpu.stepping':
        st=d.call('cpu.getAllRegs'); regs={}
        for cat in st['categories']:
            if cat['name']=='GPR':
                for nn,v in zip(cat['registerNames'],cat['uintValues']): regs[nn]=v
        print(' '.join('%s=%x'%(k,regs[k]) for k in regsel)); got+=1
        d.w.send(json.dumps({'event':'cpu.resume'}))
except Exception as e: print('stop',e)
d.call('cpu.breakpoint.remove',address=addr)
d.call('cpu.resume')
