"""Alibi table images: erase OCR'd cell words, draw Korean."""
import os,json,glob,numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
import mapimg,imgtext,alibi_grid,build_alibi
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT=os.path.join(R,'work','ext')
COLS=['斑井','日織','暗石','椿','那須','御陵','鈴奈','静奈']
def load():
    d={}
    for p in glob.glob(os.path.join(R,'translation','ar_out_*.json')): d.update(json.load(open(p,encoding='utf-8')))
    return d
def tmin(s):
    h,m=s.replace('：',':').split(':'); return int(h)*60+int(m)
def render(n,entries,a):
    g=alibi_grid.geometry(n)
    cx,hy=g
    if len(cx)!=8: return None
    step=cx[1]-cx[0]
    m=alibi_grid.mask(a)
    # time label rows: blobs left of first column
    vv=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((10,1),np.uint8)); hh=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((1,15),np.uint8))
    mm=m&(1-vv)&(1-hh)
    tcol=mm[hy+2:,max(0,cx[0]-step-8):max(1,cx[0]-step//2-2)]
    rows=np.where(tcol.sum(axis=1)>0)[0]
    ys=[]
    if len(rows):
        s=p=rows[0]
        for r in list(rows[1:])+[None]:
            if r is not None and r-p<=1: p=r; continue
            if 5<=p-s+1<=12: ys.append(hy+2+s)
            if r is not None: s=p=r
    if not ys: return None
    vert=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((10,1),np.uint8)); m2=m&(1-vert)
    times=sorted({tmin(e['time']) for e in entries})
    best=None
    for t0 in range(0,24*60,5):
        sc=0
        for e in entries:
            k=(tmin(e['time'])-t0)//5
            if not (0<=k<len(ys)): sc-=5; continue
            c=cx[COLS.index(e['col'])] if e['col'] in COLS else None
            if c is None: continue
            sc+=m2[ys[k]:ys[k]+8,c-8:c+9].sum()>3
        if best is None or sc>best[0]: best=(sc,t0)
    t0=best[1]
    out=a.copy()
    rects=[]
    for e in entries:
        if e['col'] not in COLS: continue
        k=(tmin(e['time'])-t0)//5
        if not (0<=k<len(ys)): continue
        c=cx[COLS.index(e['col'])]; y=ys[k]
        w=int(len(e['jp'].replace(' ',''))*10.5)+4
        x0,x1=c-w//2,c+w//2
        sub=out[y-1:y+9,x0:x1+1].reshape(-1,4).astype(int)
        lum=sub[:,:3].max(axis=1); bg=np.median(sub[lum>=np.percentile(lum,55)],axis=0).astype(np.uint8)
        out[y-1:y+9,x0:x1+1]=bg
        rects.append((x0,y-1,x1,y+8,e['ko']))
    # 時間 header left of first name column, above hy
    X1=max(1,cx[0]-step//2-3)
    reg=a[:hy+1,:X1].astype(int)
    lumr=reg[...,:3].max(axis=2)
    blue=(reg[...,2]>reg[...,0]+40)
    tm=(((lumr<110)|blue)&(reg[...,3]>200)).astype(np.uint8)
    tm=tm&(1-cv2.morphologyEx(tm,cv2.MORPH_OPEN,np.ones((1,12),np.uint8)))&(1-cv2.morphologyEx(tm,cv2.MORPH_OPEN,np.ones((12,1),np.uint8)))
    tm[:, :4]=0
    nl,lab,st,_=cv2.connectedComponentsWithStats(cv2.dilate(tm,np.ones((3,5),np.uint8)))
    cand=[st[i] for i in range(1,nl) if 6<=st[i][3]<=20 and st[i][2]>=10]
    if cand:
        bx0=min(c[0] for c in cand)+1; by0=min(c[1] for c in cand)+1
        bx1=max(c[0]+c[2] for c in cand)-2; by1=max(c[1]+c[3] for c in cand)-2
        pix=reg[by0:by1+1,bx0:bx1+1][tm[by0:by1+1,bx0:bx1+1]>0][:,:3]
        colb=(40,50,150) if (len(pix) and (pix[:,2]>pix[:,0]+30).mean()>0.3) else (30,30,30)
        sub=out[by0:by1+1,bx0:bx1+1].reshape(-1,4).astype(int); lum=sub[:,:3].max(axis=1)
        out[by0:by1+1,bx0:bx1+1]=np.median(sub[lum>=np.percentile(lum,60)],axis=0).astype(np.uint8)
        rects.append((int(bx0),int(by0),int(bx1),int(by1),('T',colb)))
    im=Image.fromarray(out,'RGBA'); d=ImageDraw.Draw(im)
    for x0,y0,x1,y1,t in rects:
        if isinstance(t,tuple): build_alibi.draw_word(d,x0,y0,x1,y1,'시간',col=t[1]+(255,))
        else: build_alibi.draw_word(d,x0,y0,x1,y1,t,col=(25,25,25,255))
    return np.array(im)
def hook(enc):
    res={}; D=load()
    base=build_alibi.tables()   # header names already replaced
    for n,entries in D.items():
        b=open(os.path.join(EXT,n+'.MPB'),'rb').read()
        src=base.get(n+'.MPB',b)
        H,a=mapimg.compose(src); a=np.array(a)
        o=render(n,entries,a)
        if o is None: print('AR skip',n); continue
        res[n+'.MPB']=mapimg.rebuild(b,o)
    print('artables',len(res)); return res
def texts(): return [e['ko'] for v in load().values() for e in v]
