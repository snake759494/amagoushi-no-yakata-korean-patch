import sys,base64,json
sys.path.insert(0,'tools')
from ppsspp_rpc import Debugger
d=Debugger()
out=bytearray()
start=0x08800000; size=0x01800000; ch=0x100000
d.call('cpu.stepping')
for a in range(start,start+size,ch):
    r=d.call('memory.read',address=a,size=ch)
    out+=base64.b64decode(r['base64'])
d.call('cpu.resume')
open(sys.argv[1],'wb').write(out)
print(len(out))
