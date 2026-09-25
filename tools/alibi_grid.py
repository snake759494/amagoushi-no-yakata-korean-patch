import os,re,json,hashlib,numpy as np,cv2
from PIL import Image,ImageDraw
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J=json.load(open(os.path.join(R,'work','alibi_clusters2.json')))
NAMEIDX=[0,1,2,3,4,5,6,7,65,66,67,68,69,70,71,72]
namekeys={J['keys'][i] for i in NAMEIDX}
TIMEKEYS=None
def geometry(n):
    heads=[(x,y,w,h) for nn,x,y,w,h,k in J['occ'] if nn==n and k in namekeys]
    if not heads: return None
    cx=sorted(set(int(x+w/2) for x,y,w,h in heads)); hy=max(y+h for x,y,w,h in heads)
    return cx,hy
def mask(a):
    a=a.astype(int); lum=a[...,:3].max(axis=2); return ((lum<110)&(a[...,3]>200)).astype(np.uint8)
def words(n):
    a=np.array(Image.open(os.path.join(R,'work','comp',n+'.png')).convert('RGBA'))
    g=geometry(n)
    if not g: return a,[]
    cx,hy=g; m=mask(a)
    vert=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((10,1),np.uint8))
    m2=m&(1-vert)
    hor=cv2.morphologyEx(m2,cv2.MORPH_OPEN,np.ones((1,20),np.uint8)); m2=m2&(1-hor)
    out=[]
    H=m.shape[0]
    step=(cx[1]-cx[0]) if len(cx)>1 else 46
    for c in cx:
        x0=max(0,c-int(step*0.72)); x1=min(m.shape[1]-1,c+int(step*0.72))
        col=m2[hy+2:,x0:x1+1]
        rows=np.where(col.sum(axis=1)>1)[0]
        if len(rows)==0: continue
        s=p=rows[0]
        for r in list(rows[1:])+[None]:
            if r is not None and r-p<=1: p=r; continue
            band=col[s:p+1]; cs=np.where(band.any(axis=0))[0]
            if 5<=p-s+1<=12 and cs[-1]-cs[0]>=8:
                bx0,bx1=x0+cs[0],x0+cs[-1]
                crop=m2[hy+2+s:hy+2+p+1,bx0:bx1+1]
                out.append((int(bx0),int(hy+2+s),int(bx1),int(hy+2+p),hashlib.md5(crop.tobytes()+bytes([bx1-bx0,p-s])).hexdigest()[:10]))
            if r is not None: s=p=r
    return a,out
if __name__=='__main__':
    fs=sorted({o[0] for o in J['occ']})
    occ=[];cl={}
    for n in fs:
        a,ws=words(n)
        for w in ws:
            occ.append((n,)+w); cl.setdefault(w[4],[0,(n,)+w[:4]]); cl[w[4]][0]+=1
    keys=sorted(cl,key=lambda k:-cl[k][0])
    json.dump({'occ':occ,'keys':keys,'cl':cl},open(os.path.join(R,'work','alibi_grid.json'),'w'))
    Wd=Image.new('RGB',(1200,30*((len(keys)+5)//6)),(255,255,255)); d=ImageDraw.Draw(Wd)
    for i,k in enumerate(keys):
        n,x0,y0,x1,y1=cl[k][1]
        im=Image.open(os.path.join(R,'work','comp',n+'.png')).convert('RGB').crop((x0-1,y0-1,x1+2,y1+2)); im=im.resize((im.width*2,im.height*2),Image.NEAREST)
        X=(i%6)*200;Y=(i//6)*30; d.text((X,Y+8),str(i),fill=(255,0,0)); Wd.paste(im,(X+26,Y+2))
    Wd.save(os.path.join(R,'work','alibi_gallery.png')); print(len(keys),len(occ))
