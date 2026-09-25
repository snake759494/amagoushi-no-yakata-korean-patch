"""Alibi table word sprites (ARIH_MOJI_2) + prerendered tables (AR*) via template matching."""
import os,glob,numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
import mapimg,imgtext
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT=os.path.join(R,'work','ext')
A=[(17,'가든'),(30,'실'),(44,'우물'),(72,'스타우트'),(85,'라이스'),(98,'크로프츠'),(112,'르루'),(126,'아시모프'),(139,'녹스'),(153,'오르치'),(180,'해리스'),(208,'로스'),(221,'밀른')]
B=[(4,'퀸'),(18,'로슨'),(31,'다인'),(44,'카터'),(58,'카'),(72,'애거사'),(84,'포'),(98,'도일'),(112,'모리스'),(125,'앨런'),(166,'창고'),(180,'마법'),(193,'문'),(207,'뱀'),(221,'르로이')]
C=[(4,'BF실'),(17,'보일러'),(31,'사망 추정'),(44,'시간'),(55,'마다라이'),(69,'히오리'),(83,'쿠라이시'),(97,'츠바키'),(111,'나스'),(125,'미사사기'),(139,'스즈나'),(153,'시즈나')]
COLS=[(10,58,A),(74,122,B),(137,187,C)]
def slots():
    out=[]
    for x0,x1,L in COLS:
        for y,t in L:
            h=12 if (x0==137 and y>=55) else 9
            if x0==137 and y>=55: out.append((142,y-1,182,y+h,t)); continue
            out.append((x0,y-1,x1,y+h,t))
    return out
def draw_word(d,x0,y0,x1,y1,t,col=(0,0,0,255)):
    size=y1-y0
    while True:
        f=ImageFont.truetype(imgtext.FONTS['B'],size); w=f.getlength(t)
        if w<=x1-x0 or size<=6: break
        size-=1
    bb=f.getbbox('한'); ty=y0+((y1-y0+1)-(bb[3]-bb[1]))//2-bb[1]
    d.text((x0+(x1-x0-w)/2,ty),t,font=f,fill=col)
def moji():
    b=open(os.path.join(EXT,'ARIH_MOJI_2.MPB'),'rb').read()
    H,a=mapimg.compose(b); a=np.array(a)
    for x0,y0,x1,y1,t in slots(): a[y0-1:y1+3,x0:x1+1]=0
    im=Image.fromarray(a,'RGBA'); d=ImageDraw.Draw(im)
    for x0,y0,x1,y1,t in slots(): draw_word(d,x0,y0,x1,y1,t)
    return mapimg.rebuild(b,np.array(im)),im
LAB={0:'마다라이',1:'히오리',2:'쿠라이시',3:'츠바키',4:'나스',5:'미사사기',6:'스즈나',7:'시즈나',12:'카',25:'다인',27:'퀸',28:'로슨',29:'퀸|로슨',
 49:'르루',51:'아시모프',53:'오르치|로슨',65:'마다라이',66:'히오리',67:'쿠라이시',68:'츠바키',69:'나스',70:'미사사기',71:'스즈나',72:'시즈나',
 73:'밀른',74:'다인',75:'퀸',76:'애거사',77:'카',78:'로슨',82:'라이스',83:'카',88:'로슨',91:'로슨',93:'애거사',94:'카터',96:'퀸',101:'다인',102:'카',106:'로슨',108:'퀸|로슨'}
def tables():
    import json
    J=json.load(open(os.path.join(R,'work','alibi_clusters2.json')))
    keymap={J['keys'][i]:t for i,t in LAB.items()}
    by={}
    for n,x,y,w,h,k in J['occ']:
        if k in keymap: by.setdefault(n,[]).append((x,y,w,h,keymap[k]))
    res={}
    for n,items in by.items():
        b=open(os.path.join(EXT,n+'.MPB'),'rb').read()
        H,a=mapimg.compose(b); a=np.array(a)
        for x,y,w,h,t in items:
            X0,Y0,X1,Y1=x,y,x+w-1,y+h-1
            ring=np.concatenate([a[Y0-1,X0:X1+1],a[Y1+1,X0:X1+1]]).astype(int)
            parts=t.split('|')
            if len(parts)==1:
                seg=[(X0,X1)]
            else:
                mid=(X0+X1)//2; seg=[(X0,mid),(mid+1,X1)]
            for (s0,s1) in seg:
                sub=a[Y0-1:Y1+2,s0:s1+1].reshape(-1,4).astype(int)
                lum=sub[:,:3].max(axis=1); col=np.median(sub[lum>=np.percentile(lum,60)],axis=0).astype(np.uint8)
                a[Y0:Y1+1,s0:s1+1]=col
        im=Image.fromarray(a,'RGBA'); d=ImageDraw.Draw(im)
        for x,y,w,h,t in items:
            X0,Y0,X1,Y1=x,y,x+w-1,y+h-1
            parts=t.split('|')
            seg=[(X0,X1)] if len(parts)==1 else [(X0,(X0+X1)//2),((X0+X1)//2+1,X1)]
            if len(parts)==1 and Y1<45 and parts[0] in ('마다라이','히오리','쿠라이시','츠바키','나스','미사사기','스즈나','시즈나'):
                c=(X0+X1)//2; seg=[(c-17,c+17)]
            for (s0,s1),p in zip(seg,parts): draw_word(d,s0,Y0,s1,Y1,p,col=(30,30,30,255))
        res[n+'.MPB']=mapimg.rebuild(b,np.array(im))
    return res
def texts(): return [s[4] for s in slots()]+[p for t in LAB.values() for p in t.split('|')]
def hook(enc):
    r=tables(); r['ARIH_MOJI_2.MPB']=moji()[0]; print('alibi',len(r)); return r
