"""Detect text lines in an image and redraw them with Korean."""
import numpy as np,re,os
from PIL import Image,ImageDraw,ImageFont
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS={'EB':os.path.join(R,'SeoulHangangEB.ttf'),'B':os.path.join(R,'SeoulHangangB.ttf'),'M':os.path.join(R,'SeoulHangangM.ttf'),'L':os.path.join(R,'SeoulHangangL.ttf')}
def text_mask(a,bg=None,lum=90):
    rgb=a[...,:3].astype(int); al=a[...,3].astype(int)
    if bg is None:
        L=rgb.max(axis=2)
        return (al>60)&(L>lum)
    d=np.abs(rgb-np.array(bg)).sum(axis=2)
    return d>120
def lines(a,bg=None,lum=90,gap=2,minh=5):
    m=text_mask(a,bg,lum)
    rows=np.where(m.any(axis=1))[0]
    out=[]
    if len(rows)==0: return out
    s=p=rows[0]
    for r in list(rows[1:])+[None]:
        if r is not None and r-p<=gap: p=r; continue
        if p-s+1>=minh:
            cols=np.where(m[s:p+1].any(axis=0))[0]
            out.append(dict(y0=int(s),y1=int(p),x0=int(cols[0]),x1=int(cols[-1])))
        if r is not None: s=p=r
    return out
def dominant_colors(a,ln,bg=None,lum=90):
    sub=a[ln['y0']:ln['y1']+1,ln['x0']:ln['x1']+1]
    m=text_mask(sub,bg,lum)
    px=sub[m][:,:3].astype(int)
    if len(px)==0: return (255,255,255),None
    red=px[(px[:,0]>150)&(px[:,1]<110)]
    main=px[~((px[:,0]>150)&(px[:,1]<110))]
    mc=tuple(int(x) for x in np.median(main,axis=0)) if len(main) else (255,255,255)
    rc=tuple(int(x) for x in np.median(red,axis=0)) if len(red)>5 else None
    return mc,rc
def parse_markup(s):
    segs=[];cur=''; red=False
    for part in re.split(r'(<r>|</r>)',s):
        if part=='<r>': red=True; continue
        if part=='</r>': red=False; continue
        if part: segs.append((part,red))
    return segs
def draw_line(img,x,y,text,size,color,red=None,font='EB',shadow=(0,0,0,170),maxw=None,valign_h=None):
    """y = top of JP ink box; place glyph box to cover same vertical band."""
    while True:
        f=ImageFont.truetype(FONTS[font],size)
        plain=re.sub(r'</?r>','',text)
        w=f.getlength(plain)
        if maxw is None or w<=maxw or size<=7: break
        size-=1
    d=ImageDraw.Draw(img)
    asc,desc=f.getmetrics()
    bb=f.getbbox('한')
    top_off=bb[1]; gh=bb[3]-bb[1]
    ty=y - top_off + ((valign_h-gh)//2 if valign_h else 0)
    cx=x
    for seg,isred in parse_markup(text):
        col=(red or (230,40,40)) if isred else color
        if shadow:
            d.text((cx+1,ty+1),seg,font=f,fill=shadow)
        d.text((cx,ty),seg,font=f,fill=tuple(col)+((255,) if len(col)==3 else ()))
        cx+=f.getlength(seg)
    return size,w
