"""Redraw text images (CB_*, M*, TUT*, TU_*_MES*, OPMOJI ...) with Korean."""
import os,json,glob,re
import numpy as np
from PIL import Image
import mapimg,imgtext
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT=os.path.join(R,'work','ext')
def load():
    tr={}
    for p in sorted(glob.glob(os.path.join(R,'translation','img_out_*.json'))):
        tr.update(json.load(open(p,encoding='utf-8')))
    return tr
def texts():
    return [re.sub(r'</?r>','',l) for v in load().values() for l in v['ko']]
def color_of(a,l):
    sub=a[l['y0']:l['y1']+1,l['x0']:l['x1']+1].reshape(-1,4).astype(int)
    m=(sub[:,3]>60)&(sub[:,:3].max(axis=1)>90)
    px=sub[m][:,:3]
    if len(px)==0: return (255,255,255),None
    isred=(px[:,0]>150)&(px[:,1]<110)&(px[:,2]<110)
    main=px[~isred] if (~isred).sum()>5 else px
    lum=main.max(axis=1)
    sel=main[lum>=np.percentile(lum,80)]
    mc=tuple(int(x) for x in sel.mean(axis=0))
    rc=tuple(int(x) for x in px[isred].mean(axis=0)) if isred.sum()>8 else None
    return mc,rc
def redraw(name,ko,font='EB'):
    b=open(os.path.join(EXT,name+'.MPB'),'rb').read()
    H,a=mapimg.compose(b)
    a=np.array(a)
    L=imgtext.lines(a)
    assert len(ko)<=len(L),(name,len(ko),len(L))
    cols=[color_of(a,l) for l in L]
    red=next((c[1] for c in cols if c[1]),None)
    out=Image.new('RGBA',(a.shape[1],a.shape[0]),(0,0,0,0))
    for i,line in enumerate(ko):
        l=L[i]; h=l['y1']-l['y0']+1
        mc=cols[i][0]
        imgtext.draw_line(out,l['x0'],l['y0'],line,size=h+1,color=mc,red=red,font=font,maxw=a.shape[1]-l['x0']-2,valign_h=h)
    return mapimg.rebuild(b,np.array(out)), out
SKIP={'TUT01','TUT02','TUT03'}
def hook(enc):
    res={}
    for name,v in load().items():
        if name in SKIP: continue
        try:
            nb,_=redraw(name,v['ko'])
            res[name+'.MPB']=nb
        except Exception as e:
            print('IMG FAIL',name,e)
    print('images',len(res))
    return res

def title2():
    from PIL import ImageDraw,ImageFont
    b=open(os.path.join(EXT,'TITLE2.MPB'),'rb').read()
    H,a=mapimg.compose(b); a=np.array(a)
    a[38:125,110:126]=0          # remove kana ruby only
    im=Image.fromarray(a,'RGBA'); d=ImageDraw.Draw(im)
    f=ImageFont.truetype(imgtext.FONTS['EB'],10)
    for i,ch in enumerate('우격자의관'):
        y=42+i*16+(4 if i==4 else 0)
        w=f.getlength(ch)
        d.text((118-w/2+1,y+1),ch,font=f,fill=(0,0,0,200))
        d.text((118-w/2,y),ch,font=f,fill=(235,235,235,255))
    # subtitle 一柳和、最初の受難 -> vertical Korean in same box
    a2=np.array(im); a2[6:143,330:362]=0; im=Image.fromarray(a2,'RGBA'); d=ImageDraw.Draw(im)
    def col(chars,cx,y,size,step):
        f=ImageFont.truetype(imgtext.FONTS['EB'],size)
        for i,ch in enumerate(chars):
            w=f.getlength(ch); bb=f.getbbox(ch)
            yy=y+i*step-bb[1]
            d.text((cx-w/2+1,yy+1),ch,font=f,fill=(0,0,0,200)); d.text((cx-w/2,yy),ch,font=f,fill=(225,228,235,255))
    col('이치야나기',351,10,9,9)
    col('나고무,',340,10,9,9)
    col('최초',345,57,20,21)
    col('의수난',345,101,12,13)
    return mapimg.rebuild(b,np.array(im)),im
_old_hook=hook
def hook(enc):
    res=_old_hook(enc)
    res['TITLE2.MPB'],_=title2()
    return res
