import sys,time
sys.path.insert(0,'tools')
from ppsspp_rpc import Debugger
d=Debugger(); r=d.frame(sys.argv[1]); d.call('cpu.resume'); d.close(); print(r)
