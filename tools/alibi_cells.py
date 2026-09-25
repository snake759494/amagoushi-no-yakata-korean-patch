import os,re,numpy as np,hashlib,json,cv2
from PIL import Image,ImageDraw
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def cells(a):
    a=a.astype(int); lum=a[...,:3].max(axis=2); m=((lum<110)&(a[...,3]>200)).astype(np.uint8)
    vert=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((25,1),np.uint8))
    xs=np.where(vert.sum(axis=0)>40)[0]
    # group adjacent x
    lines=[]
    for x in xs:
        if lines and x-lines[-1][-1]<=2: lines[-1].append(x)
        else: lines.append([x])
    bounds=[(l[0],l[-1]) for l in lines]
    out=[]
    m2=m&(1-vert)
    for (a0,a1),(b0,b1) in zip(bounds,bounds[1:]):
        c0,c1=a1+1,b0-1
        if c1-c0<12: continue
        col=m2[:,c0:c1+1]
        # remove arrows: arrows are narrow (<=7px wide) centered; handled by width filter later
        rows=np.where(col.sum(axis=1)>0)[0]
        if len(rows)==0: continue
        s=p=rows[0]
        for r in list(rows[1:])+[None]:
            if r is not None and r-p<=1: p=r; continue
            band=col[s:p+1]; cols=np.where(band.any(axis=0))[0]
            if p-s+1>=6 and p-s+1<=16 and cols[-1]-cols[0]>=9:
                out.append((int(c0),int(s),int(c1),int(p),hashlib.md5(band.tobytes()+bytes([c1-c0,p-s])).hexdigest()[:10]))
            if r is not None: s=p=r
    return out
if __name__=='__main__':
    fs=[f[:-4] for f in sorted(os.listdir(os.path.join(R,'work','comp'))) if re.match(r'AR(KUR|NAS|SIA|SIB|SUA|SUB)\d|ARH_HYOU',f)]
    occ=[];cl={}
    for n in fs:
        a=np.array(Image.open(os.path.join(R,'work','comp',n+'.png')).convert('RGBA'))
        for c0,s,c1,p,k in cells(a):
            occ.append((n,c0,s,c1,p,k)); cl.setdefault(k,[0,(n,c0,s,c1,p)]); cl[k][0]+=1
    keys=sorted(cl,key=lambda k:-cl[k][0])
    json.dump({'occ':occ,'keys':keys,'cl':cl},open(os.path.join(R,'work','alibi_cells.json'),'w'))
    W=Image.new('RGB',(1200,34*((len(keys)+5)//6)),(255,255,255)); d=ImageDraw.Draw(W)
    for i,k in enumerate(keys):
        n,c0,s,c1,p=cl[k][1]
        im=Image.open(os.path.join(R,'work','comp',n+'.png')).convert('RGB').crop((c0,s-1,c1+1,p+2)); im=im.resize((im.width*2,im.height*2),Image.NEAREST)
        X=(i%6)*200;Y=(i//6)*34; d.text((X,Y+10),str(i),fill=(255,0,0)); W.paste(im,(X+26,Y+2))
    W.save(os.path.join(R,'work','alibi_gallery.png')); print(len(keys),len(occ))
