"""usage: python tools/check_batch.py NNN  -> validates translation/out/bNNN.json against batches/bNNN.json"""
import json,sys,re,os
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
n=sys.argv[1]
src=json.load(open(f'{R}/translation/batches/b{n}.json',encoding='utf-8'))
try: out=json.load(open(f'{R}/translation/out/b{n}.json',encoding='utf-8'))
except Exception as e: print('CANNOT READ OUTPUT',e); sys.exit(1)
bad=0
def vis(s): return len(re.sub(r'<[^>]*>','',s))
for b in src:
    k=str(b['id'])
    if k not in out: print('MISSING',k); bad+=1; continue
    ko=out[k]
    if not isinstance(ko,list) or len(ko)!=len(b['jp']): print('LINECOUNT',k,len(b['jp']),ko); bad+=1; continue
    for l in ko:
        if vis(l)>22: print('TOO LONG',k,l); bad+=1
        if re.search(r'[\u3040-\u30fa\u30fc-\u30ff\u4e00-\u9fff\uff61-\uff9f{}|\\]',l): print('FORBIDDEN',k,l); bad+=1
        if re.findall(r'<[^>]*>',l)!=[] and not all(re.fullmatch(r'<(fs ?\d*|co( \w+)?|w)>',t) for t in re.findall(r'<[^>]*>',l)): print('TAG',k,l); bad+=1
    if re.findall(r'<[^>]*>',''.join(b['jp']))!=re.findall(r'<[^>]*>',''.join(ko)): print('TAGMISMATCH',k,b['jp'],ko); bad+=1
extra=set(out)-{str(b['id']) for b in src}
if extra: print('EXTRA ids',list(extra)[:5]); bad+=1
print('ERRORS',bad,'of',len(src))
