"""Patch EBOOT strings in place and re-sign with the disc's tag (d9160bf0 = -t2)."""
import os,json,subprocess,shutil
import kenc
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEBOOT=r'D:\psp\디크립트 툴\PSP-ISO-Tools\EBOOT\_seboot.exe'
def load():
    tr={}
    for i in (0,1):
        p=os.path.join(R,'translation','eboot_out_%d.json'%i)
        if os.path.exists(p): tr.update(json.load(open(p,encoding='utf-8')))
    fx=os.path.join(R,'translation','tut_fix_out.json')
    if os.path.exists(fx):
        for k,v in json.load(open(fx,encoding='utf-8')).items(): tr[k]=v if v else 'SKIP'
    src=[]
    for i in (0,1):
        src+=json.load(open(os.path.join(R,'translation','eboot_src_%d.json'%i),encoding='utf-8'))
    return src,tr
def texts():
    src,tr=load(); return [v for v in tr.values() if v!='SKIP']
def hook(enc):
    src,tr=load()
    d=bytearray(open(os.path.join(R,'work','iso','EBOOT.dec'),'rb').read())
    n=0
    for x in src:
        v=tr.get(x['off'])
        if not v or v=='SKIP': continue
        o=int(x['off'],16); cap=x['maxbytes']
        orig=bytes(d[o:o+cap+1]).split(b'\0')[0]
        assert orig.decode('cp932')==x['jp'],(x['off'],)
        b=kenc.encode_dbcs(v.replace('\u3000',' '),enc)
        if len(b)>cap:
            print('EBOOT overflow',x['off'],len(b),cap); continue
        d[o:o+len(orig)]=b'\0'*len(orig)
        d[o:o+len(b)]=b; n+=1
    tmp=os.path.join(R,'work','eboot_kr.elf'); out=os.path.join(R,'work','eboot_kr.bin')
    open(tmp,'wb').write(d)
    if os.path.exists(out): os.remove(out)
    subprocess.run([SEBOOT,'-t2',tmp,out],check=True,capture_output=True)
    e=open(out,'rb').read()
    print('eboot strings',n,'signed',len(e))
    return {'__EBOOT__':e}
