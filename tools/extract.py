"""Extract translation units (blocks of consecutive text lines) from all tob scripts."""
import struct,sys,os,json
sys.path.insert(0,os.path.dirname(__file__))
import tob
from sjdec import dec
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOBDIR=os.path.join(ROOT,'work','tob')
def file_order():
    import stsdat
    h8,files=stsdat.read(os.path.join(ROOT,'work','ext','STS.DAT'))
    return [nm.split(b'\0')[0].decode() for nm,d in files]
def blocks_of(t):
    """list of blocks: each {'kind':op,'ops':[op_index...],'end':terminating op}"""
    ops=t['ops']; out=[]; cur=None
    for k,(p,L,op,a) in enumerate(ops):
        if op==1: continue
        if op==0x48:
            if cur is None: cur={'kind':'msg','ks':[]}
            cur['ks'].append(k); continue
        if cur is not None:
            cur['end']=op; out.append(cur); cur=None
        if op in(0x63,0x5f,0x53):
            out.append({'kind':{0x63:'choice',0x5f:'yesno',0x53:'sub'}[op],'ks':[k],'end':op})
    if cur: cur['end']=-1; out.append(cur)
    return out
def extract():
    units=[]
    for fn in file_order():
        t=tob.load(os.path.join(TOBDIR,fn))
        refs={k:v for k,op,ap,v in tob.text_refs(t)}
        for bi,b in enumerate(blocks_of(t)):
            lines=[dec(tob.cstr(t['s'],refs[k])) for k in b['ks']]
            units.append({'file':fn,'kind':b['kind'],'ks':b['ks'],'end':b['end'],'jp':lines})
    return units
if __name__=='__main__':
    U=extract()
    json.dump(U,open(os.path.join(ROOT,'work','units.json'),'w',encoding='utf-8'),ensure_ascii=False)
    from collections import Counter
    print(len(U), Counter(u['kind'] for u in U), Counter(len(u['jp']) for u in U).most_common(8))
    uniq={}
    for u in U: uniq.setdefault((u['kind'],tuple(u['jp'])),0)
    print('unique blocks',len(uniq), 'chars',sum(len(''.join(k[1])) for k in uniq))
