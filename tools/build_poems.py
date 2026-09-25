"""Hint poem pages: inpaint dark Japanese text, draw Korean."""
import os,numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
import mapimg,imgtext
EXT=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'work','ext')
Q1='“저주를 걸자  저주받으면 지는 거야”'; Q2='저주의 표식에 앉는 건  누구일까'
P={
'KAI_HINT01':[(179,8,22,Q1),(179,26,39,Q2),(265,58,70,'릭은 거짓말을 했다'),(265,76,89,'“나는 남쪽에 앉을래”'),
  (16,98,112,'심술궂은 마법사가 4명'),(265,98,112,'폴은 듣지 않았다'),(265,116,129,'“금색은 내 오른쪽으로 와”'),
  (16,135,149,'마법의 표식을 둘러싸고 놀지'),(265,145,158,'데이브는 알아챘다'),(265,163,177,'“어라, 폴이 남쪽에 있네”'),
  (16,172,186,'표식은 해 지는 쪽만 비춰'),(265,190,202,'키스는 믿었다'),(265,208,221,'“그럼 나는 빈 동쪽으로”'),
  (179,234,246,'저주받은 건 키스  불쌍한 키스'),(179,252,265,'키스는 속아서 저주받았다')],
'KAI_HINT02':[(95,9,22,Q1),(95,29,41,Q2),(95,53,66,'릭은 생각한다'),(95,72,85,'“나는 키스의 오른쪽에 앉을래”'),
  (95,99,111,'폴은 지시한다'),(95,116,129,'“데이브는 파란 녀석 맞은편으로 가”'),(95,143,155,'데이브는 고개를 끄덕인다'),
  (95,161,174,'“알았어, 폴의 왼쪽이구나”'),(95,187,200,'키스는 부탁했다'),(95,205,218,'“이번에야말로 동쪽에 앉게 해 줘”'),
  (95,232,244,'저주받은 건 데이브  슬픈 데이브'),(95,250,263,'데이브는 배신당해 저주받았다')],
'KAI_HINT03':[(15,8,21,Q1),(15,27,39,Q2),(15,52,65,'릭은 기분이 좋다'),(15,71,84,'“나는 검은 녀석 오른쪽에 앉겠어”'),
  (15,97,108,'폴은 으스댄다'),(15,115,128,'“키스를 내 옆에 오게 하지 마”'),(15,142,155,'데이브는 반항한다'),
  (15,160,173,'“싫어, 동쪽은 내가 앉을 거야”'),(15,186,198,'키스는 모르는 척'),(15,204,217,'“나는 빨간 녀석 맞은편으로”'),
  (15,231,243,'저주받은 건 폴  분한 폴'),(15,250,262,'폴은 버림받아 저주받았다'),
  (256,80,93,'심술궂은 마법사가 4명'),(256,115,128,'빛을 받은 표식은 저주의 표식'),(256,152,165,'저주의 표식에 앉은 건  누구일까')],
'HOU_HINT':[(-1,37,50,'『느긋한 기분이 되어,'),(-1,64,77,'머핀을 구운 뒤,'),(-1,95,107,'꽃을 따러 간다.'),
  (-1,155,168,'나는 목마를 치운 뒤,'),(-1,183,196,'은행나무를 올려다보고 나서,'),(-1,213,226,'초대받지 않은 손님을 대접했다.』')],
}
def render(name):
    b=open(os.path.join(EXT,name+'.MPB'),'rb').read()
    H,a=mapimg.compose(b); a=np.array(a)
    lum=a[...,:3].astype(int).max(axis=2)
    thr=175 if name=='HOU_HINT' else 95
    m=((lum<thr)&(a[...,3]>200)).astype(np.uint8)*255
    if name=='HOU_HINT': m[:,:20]=0; m[:,460:]=0
    m=cv2.dilate(m,np.ones((5,5) if name=='HOU_HINT' else (3,3),np.uint8),1)
    rgb=cv2.inpaint(np.ascontiguousarray(a[...,:3]),m,4,cv2.INPAINT_TELEA)
    out=a.copy(); out[...,:3]=rgb
    im=Image.fromarray(out,'RGBA'); d=ImageDraw.Draw(im)
    for x,y0,y1,t in P[name]:
        size=y1-y0+1
        while True:
            f=ImageFont.truetype(imgtext.FONTS['B'],size); w=f.getlength(t)
            lim=(470-(x if x>=0 else 0)) if x>=0 else 440
            if w<=lim or size<8: break
            size-=1
        bb=f.getbbox('한'); ty=y0+((y1-y0+1)-(bb[3]-bb[1]))//2-bb[1]
        tx=x if x>=0 else (480-w)/2
        d.text((tx,ty),t,font=f,fill=(25,25,25,255))
    return mapimg.rebuild(b,np.array(im)),im
def texts(): return [t for v in P.values() for *_,t in v]
def hook(enc):
    return {n+'.MPB':render(n)[0] for n in P}
