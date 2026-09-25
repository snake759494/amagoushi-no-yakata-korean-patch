"""Replace small text labels inside images: spec = [(x0,y0,x1,y1,'텍스트',{opts})]"""
import os,numpy as np
from PIL import Image,ImageDraw,ImageFont
import imgtext,mapimg
EXT=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'work','ext')
def sample2(a,x0,y0,x1,y1):
    Hh,Ww=a.shape[:2]; X0=max(x0-1,0);Y0=max(y0-1,0);X1=min(x1+1,Ww-1);Y1=min(y1+1,Hh-1)
    ring=np.concatenate([a[Y0,X0:X1+1],a[Y1,X0:X1+1],a[Y0:Y1+1,X0],a[Y0:Y1+1,X1]]).astype(int)
    bg=np.median(ring,axis=0)[:3]
    sub=a[y0:y1+1,x0:x1+1].reshape(-1,4).astype(int)
    dist=np.abs(sub[:,:3]-bg).sum(axis=1)
    fg=sub[dist>=np.percentile(dist,92)][:,:3]
    fgc=tuple(int(v) for v in fg.mean(axis=0))
    lum=lambda c: max(c)
    shc=(0,0,0,170) if lum(fgc)>lum(bg) and lum(bg)<120 else None
    return fgc,shc
def sample(a,x0,y0,x1,y1):
    sub=a[y0:y1+1,x0:x1+1].reshape(-1,4).astype(int)
    lum=sub[:,:3].max(axis=1); al=sub[:,3]
    fg=sub[(al>150)&(lum>=np.percentile(lum[al>150],85) if (al>150).any() else lum>0)]
    fgc=tuple(int(v) for v in fg[:,:3].mean(axis=0)) if len(fg) else (255,255,255)
    dk=sub[(al>100)&(lum<70)]
    shc=tuple(int(v) for v in dk[:,:3].mean(axis=0))+(200,) if len(dk)>5 else None
    return fgc,shc
def apply(a,spec):
    a=a.copy(); im=None
    items=[]
    for x0,y0,x1,y1,text,o in spec:
        fgc,shc=(sample2 if o.get('auto') else sample)(a,x0,y0,x1,y1)
        fgc=o.get('color',fgc); shc=o['shadow'] if 'shadow' in o else shc
        fill=o.get('fill')
        if fill=='bg':
            Hh,Ww=a.shape[:2]; X0=max(x0-1,0);Y0=max(y0-1,0);X1=min(x1+1,Ww-1);Y1=min(y1+1,Hh-1)
            ring=np.concatenate([a[Y0,X0:X1+1],a[Y1,X0:X1+1],a[Y0:Y1+1,X0],a[Y0:Y1+1,X1]]).astype(int)
            a[y0:y1+1,x0:x1+1]=np.median(ring,axis=0).astype(np.uint8)
        elif fill=='dark':
            sub=a[y0:y1+1,x0:x1+1].astype(int); lum=sub[...,:3].max(axis=2)
            dk=sub[(sub[...,3]>200)&(lum<60)]
            col=np.median(dk,axis=0).astype(np.uint8) if len(dk) else np.array([0,0,0,255],np.uint8)
            m=(sub[...,3]>0)&(lum>=60)
            a[y0:y1+1,x0:x1+1][m]=col
        elif fill=='flat':
            sub=a[y0:y1+1,x0:x1+1].reshape(-1,4).astype(int)
            lum=sub[:,:3].max(axis=1); bgpx=sub[lum<=np.percentile(lum,50)]
            a[y0:y1+1,x0:x1+1]=np.median(bgpx,axis=0).astype(np.uint8)
        elif fill=='keep': pass
        elif fill is None: a[y0:y1+1,x0:x1+1]=0
        else: a[y0:y1+1,x0:x1+1]=fill
        items.append((x0,y0,x1,y1,text,o,fgc,shc))
    im=Image.fromarray(a,'RGBA'); d=ImageDraw.Draw(im)
    for x0,y0,x1,y1,text,o,fgc,shc in items:
        if o.get('squeeze') and text:
            f=ImageFont.truetype(imgtext.FONTS[o.get('font','EB')],o['size'])
            bb=f.getbbox(text); tw=bb[2]+2; th=y1-y0+1
            t=Image.new('RGBA',(tw,th),(0,0,0,0)); td=ImageDraw.Draw(t)
            gb=f.getbbox('한'); ty=(th-(gb[3]-gb[1]))//2-gb[1]
            td.text((1,ty),text,font=f,fill=tuple(fgc)[:3]+(255,),stroke_width=1,stroke_fill=(0,0,0,200))
            W=x1-x0+1
            if tw>W: t=t.resize((W,th),Image.LANCZOS)
            im.alpha_composite(t,(x0,y0)); continue
        size=o.get('size',y1-y0+1); fn=o.get('font','EB')
        while True:
            f=ImageFont.truetype(imgtext.FONTS[fn],size)
            w=f.getlength(text)
            if w<=(x1-x0+1+o.get('overflow',0)) or size<=6: break
            size-=1
        bb=f.getbbox('한'); gh=bb[3]-bb[1]
        ty=y0+((y1-y0+1)-gh)//2-bb[1]
        al=o.get('align','center')
        tx=x0 if al=='left' else (x1+1-w if al=='right' else x0+((x1-x0+1)-w)/2)
        if o.get('stroke'):
            d.text((tx,ty),text,font=f,fill=tuple(fgc)[:3]+(255,),stroke_width=o['stroke'],stroke_fill=(shc or (0,0,0,255))[:3]+(255,))
        else:
            if shc: d.text((tx+1,ty+1),text,font=f,fill=shc)
            d.text((tx,ty),text,font=f,fill=tuple(fgc)[:3]+(255,))
    return np.array(im)
def patch(name,spec):
    b=open(os.path.join(EXT,name+'.MPB'),'rb').read()
    H,a=mapimg.compose(b)
    out=apply(np.array(a),spec)
    return mapimg.rebuild(b,out),out
