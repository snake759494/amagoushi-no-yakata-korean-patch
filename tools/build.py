"""Full Korean patch build: python tools/build.py [out.iso]"""
import sys,os,json,glob,struct,re,time
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import tob,stsdat,datadat,isopatch,fontgen,kenc,extract
from sjdec import dec
from collections import Counter
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIG=os.path.join(R,"Amagoushi no Yakata Portable - Ichiyanagi Nagomu, Saisho no Junan (Japan).iso")
MENU66=json.load(open(os.path.join(R,'translation','menu66_out.json'),encoding='utf-8'))
EXTRA_TEXT=list(MENU66.values())      # other modules append korean strings here for the font
EXTRA_FILES={}     # name -> bytes (DATA.DAT replacements)
EXTRA_HOOKS=[]     # callables(enc) -> dict name->bytes  (built after font)
def load_translations():
    blocks=json.load(open(os.path.join(R,'translation','blocks.json'),encoding='utf-8'))
    tr={}
    for f in glob.glob(os.path.join(R,'translation','out','b*.json')):
        tr.update(json.load(open(f,encoding='utf-8')))
    m={}
    for b in blocks:
        ko=tr.get(str(b['id']))
        if ko is None: continue
        m[(b['kind'],tuple(b['jp']))]=ko
    return m
def norm(l):
    l=l.replace('...','・・・') if False else l
    return l
def main(out_iso):
    import subprocess; subprocess.run(["taskkill","/F","/IM","PPSSPPWindows64.exe"],capture_output=True); time.sleep(2)
    t0=time.time()
    tmap=load_translations()
    units=extract.extract()
    texts=[l for v in tmap.values() for l in v]+EXTRA_TEXT
    def needs(ch):
        if ord(ch)<0x80 or ch in kenc.PUNCT_MAP: return False
        if 0xac00<=ord(ch)<=0xd7a3: return True
        try: return len(ch.encode('cp932'))!=2
        except UnicodeEncodeError: return True
    cnt=Counter(ch for l in texts for ch in l.replace('・','·') if needs(ch))
    import importlib
    # plug-in modules (eboot/bins/images) register via build_* files
    for mod in sorted(glob.glob(os.path.join(R,'tools','build_*.py'))):
        name=os.path.basename(mod)[:-3]
        M=importlib.import_module(name)
        if hasattr(M,'texts'):
            for l in M.texts(): cnt.update(ch for ch in l if needs(ch))
        if hasattr(M,'hook'): EXTRA_HOOKS.append(M.hook)
    order=[c for c,_ in cnt.most_common()]
    nsb=len(fontgen.SB_BYTES)
    sb=order[:nsb]; db=sorted(order[nsb:])
    enc,fb,mpb=fontgen.build(sb,db,os.path.join(R,'work'),fontsize=15,space_w=4)
    import pickle; pickle.dump(enc,open(os.path.join(R,'work','enc.pkl'),'wb'))
    print('hangul',len(order),'font ok',round(time.time()-t0,1))
    # scripts
    h8,files=stsdat.read(os.path.join(R,'work','ext','STS.DAT'))
    byfile={}
    for u in units: byfile.setdefault(u['file'],[]).append(u)
    newfiles=[]; miss=0; tot=0
    for nm,data in files:
        fn=nm.split(b'\0')[0].decode()
        t=tob.load_bytes(data,fn)
        new={}
        for u in byfile.get(fn,[]):
            ko=tmap.get((u['kind'],tuple(u['jp'])))
            tot+=1
            if ko is None or len(ko)!=len(u['ks']): miss+=1; continue
            for k,l in zip(u['ks'],ko):
                new[k]=kenc.encode(l,enc)
        s_=t['s']+bytes(1)
        for k,(p_,L_,op_,a_) in enumerate(t['ops']):
            if op_==0x66:
                for ap in range(2,len(a_)-1,2):
                    v=struct.unpack('<H',a_[ap:ap+2])[0]*4
                    jp=dec(tob.cstr(s_,v))
                    if jp in MENU66: new[(k,ap)]=kenc.encode_dbcs(MENU66[jp],enc)
        newfiles.append((nm,tob.rebuild(t,new) if new else data))
    sts=stsdat.write(h8,newfiles)
    print('scripts',tot,'missing',miss,'STS',len(sts),'orig',os.path.getsize(os.path.join(R,'work','ext','STS.DAT')))
    repl={'STS.DAT':sts,'FONT.BIN':fb,'FONT.MPB':mpb}
    repl.update(EXTRA_FILES)
    eboot=None
    for hk in EXTRA_HOOKS:
        r=hk(enc)
        if r:
            if '__EBOOT__' in r: eboot=r.pop('__EBOOT__')
            repl.update(r)
    dd=datadat.rebuild(os.path.join(R,'work','iso','DATA.DAT'),repl)
    isopatch.build(ORIG,out_iso,datadat=dd,eboot=eboot)
    print('built',out_iso,round(time.time()-t0,1),'s')
if __name__=='__main__':
    main(sys.argv[1] if len(sys.argv)>1 else os.path.join(R,'work','kr_test.iso'))
