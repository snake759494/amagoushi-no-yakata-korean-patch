"""python tools/check_eboot.py N  -> validates translation/eboot_out_N.json"""
import json,sys,re,os
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
n=sys.argv[1]
src=json.load(open(f'{R}/translation/eboot_src_{n}.json',encoding='utf-8'))
out=json.load(open(f'{R}/translation/eboot_out_{n}.json',encoding='utf-8'))
def nbytes(s): return sum(1 if ord(c)<0x80 else 2 for c in s)
bad=0
for x in src:
    k=x['off']
    if k not in out: print('MISSING',k,x['jp']); bad+=1; continue
    v=out[k]
    if v=='SKIP': continue
    if nbytes(v)>x['maxbytes']: print('TOO LONG',k,x['maxbytes'],nbytes(v),v); bad+=1
    if re.search(r'[\u3040-\u30fa\u30fc-\u30ff\u4e00-\u9fff\uff61-\uff9f\{}|]',v): print('FORBIDDEN',k,v); bad+=1
    if re.findall(r'%[0-9]*[sdxc]',x['jp'])!=re.findall(r'%[0-9]*[sdxc]',v): print('FORMAT',k,x['jp'],v); bad+=1
    if x['jp'].count('\n')!=v.count('\n'): print('NEWLINE',k,repr(x['jp']),repr(v)); bad+=1
print('ERRORS',bad,'of',len(src))
