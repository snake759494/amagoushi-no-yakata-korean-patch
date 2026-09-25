import os
import sys,json,time
sys.path.insert(0,'tools')
from ppsspp_rpc import Debugger
import websocket
d=Debugger()
addr=int(sys.argv[1],16); size=int(sys.argv[2],16)
print(d.call('memory.breakpoint.add',address=addr,size=size,enabled=True,log=False,read=(os.environ.get('RW','r')=='r'),write=(os.environ.get('RW','r')=='w'),change=False))
# press circle to advance text
import uuid
t=str(uuid.uuid4()); d.w.send(json.dumps({'event':'input.buttons.press','button':'circle','duration':8,'ticket':t}))
d.w.settimeout(20)
hits=[]
try:
    while len(hits)<1:
        r=json.loads(d.w.recv())
        if r.get('event')=='cpu.stepping':
            hits.append(r); print(r)
except Exception as e: print('timeout',e)
if hits:
    st=d.call('cpu.getAllRegs')
    regs={}
    for cat in st['categories']:
        if cat['name']=='GPR':
            for n,v in zip(cat['registerNames'],cat['uintValues']): regs[n]=v
    print({k:hex(v) for k,v in regs.items()})
d.call('memory.breakpoint.remove',address=addr,size=size)
d.call('cpu.resume')
