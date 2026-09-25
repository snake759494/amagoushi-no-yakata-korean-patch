"""Floor maps (MAPBG1/2) room labels and tooltip sprites (MAP1/MAP3)."""
import os,numpy as np
from PIL import Image,ImageDraw,ImageFont
import mapimg,imgtext,labelfix
EXT=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'work','ext')
MAP1=[((0,1,20,15),'츠바키'),((22,0,69,15),'응접실'),((71,0,117,14),'거실'),((119,1,165,15),'오락실'),((167,1,186,14),'뱀'),
 ((0,25,45,39),'서재'),((47,25,93,39),'식당'),((95,24,141,39),'부엌'),((143,25,189,39),'욕실'),
 ((0,49,45,64),'탈의실'),((47,49,93,63),'수납C'),((95,49,140,63),'온실'),((142,48,189,63),'마다라이'),
 ((0,73,69,88),'히오리&나고무'),((71,72,142,87),'열리지 않는 방'),((143,73,189,87),'나스'),
 ((0,97,69,112),'빈방'),((71,97,117,112),'쿠라이시'),((119,97,191,111),'르로이 백작'),
 ((0,121,45,135),'시즈나'),((47,121,93,135),'스즈나'),((95,121,141,135),'수납A'),((143,121,189,135),'수납B'),
 ((0,144,45,158),'미사사기'),((47,145,93,160),'우물'),((95,145,154,160),'마법사'),((0,169,69,184),'문투성이')]
MAP3=[((0,0,57,14),'보일러'),((0,24,57,38),'본채 지하'),((0,49,57,63),'궤짝 방'),((0,73,57,87),'온실 지하')]
def sprite(name,items):
    b=open(os.path.join(EXT,name+'.MPB'),'rb').read()
    H,a=mapimg.compose(b); a=np.array(a)
    for (x0,y0,x1,y1),t in items: a[y0:y1+1,x0:x1+1]=0
    im=Image.fromarray(a,'RGBA')
    for (x0,y0,x1,y1),t in items:
        f=ImageFont.truetype(imgtext.FONTS['B'],12)
        bb=f.getbbox(t); w=bb[2]+1; h=y1-y0+1
        tt=Image.new('RGBA',(w,h),(0,0,0,0)); d=ImageDraw.Draw(tt)
        gb=f.getbbox('한'); d.text((0,(h-(gb[3]-gb[1]))//2-gb[1]),t,font=f,fill=(8,8,8,255))
        W=x1-x0+1
        if w>W: tt=tt.resize((W,h),Image.LANCZOS)
        im.alpha_composite(tt,(x0,y0))
    return mapimg.rebuild(b,np.array(im)),im
D=(45,40,40)
def o(**k): r=dict(fill='bg',color=D,shadow=None,font='B',size=10); r.update(k); return r
FLOOR={
'MAPBG1':[(292,24,327,38,'크로프츠',o()),(188,27,228,42,'주차장',o(size=11)),(329,30,367,42,'아시모프',o()),(227,89,262,103,'녹스',o()),
          (192,96,229,109,'르루',o()),(103,100,141,114,'오르치',o()),(104,126,134,136,'오르치',o(size=8)),(271,148,287,164,'정원',o(overflow=14,size=11)),
          (166,158,194,171,'라이스',o()),(105,161,134,174,'해리스',o()),(314,204,345,216,'실',o()),(132,212,167,226,'스타우트',o())],
'MAPBG2':[(261,22,294,38,'(통층)',o()),(337,27,366,39,'밀른',o()),(183,67,223,80,'로슨',o()),(231,62,262,75,'앨런',o()),(264,65,304,84,'퀸',o()),
          (236,94,260,108,'포',o()),(202,104,231,117,'다인',o()),(129,107,157,120,'도일',o()),(177,142,197,154,'로스',o()),(127,150,158,163,'애거사',o()),
          (171,164,201,179,'모리스',o(size=8)),(127,204,151,217,'카',o()),(158,207,196,221,'카터',o())],
}
def texts(): return [t for _,t in MAP1+MAP3]+[s[4] for v in FLOOR.values() for s in v]
def hook(enc):
    r={'MAP1.MPB':sprite('MAP1',MAP1)[0],'MAP3.MPB':sprite('MAP3',MAP3)[0]}
    for n,spec in FLOOR.items(): r[n+'.MPB']=labelfix.patch(n,spec)[0]
    print('maps',len(r)); return r
