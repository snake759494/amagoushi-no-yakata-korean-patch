"""Hand-specified label replacements for UI images."""
import os
import labelfix
S={}
def rowspec(rects,words,**o):
    return [(r[0],r[1],r[2],r[3],w,dict(o)) for r,w in zip(rects,words)]
S['SYSWIN']=rowspec([(186,46,250,66),(180,72,256,92),(186,98,250,118),(186,124,250,144),(186,150,250,170),(186,176,250,196),(180,202,256,222)],
                    ['말하기','조사','이동','추리','정보','휴식','시스템'],size=14)+\
            rowspec([(278,45,346,68),(272,71,352,94),(278,97,346,120),(278,123,346,146),(278,149,346,172),(278,175,346,198),(272,202,352,224)],
                    ['말하기','조사','이동','추리','정보','휴식','시스템'],size=15)
K=(0,0,0,255)
S['DLOGWND']=[(108,10,140,26,'예',dict(fill='dark',size=14)),(98,55,158,72,'아니오',dict(fill='dark',size=14)),
              (104,102,148,119,'예',dict(fill='dark',size=14,color=(200,180,200))),(100,147,160,164,'아니오',dict(fill='dark',size=14,color=(200,180,200)))]
S['HELPBA']=[(41,6,100,22,'R3 버튼',dict(size=12,stroke=1)),(117,6,192,22,'왼쪽 스틱',dict(size=12,stroke=1)),
             (41,31,126,47,'START 버튼',dict(size=12,stroke=1)),(144,31,236,47,'SELECT 버튼',dict(size=12,stroke=1)),
             (9,162,42,175,'도움말',dict(fill='bg',size=11))]
S['MSWIN']=[(158,227,190,246,'',dict()),(158,235,173,243,'월',dict(fill='keep',size=10,stroke=1,color=(235,235,235),shadow=(40,30,30,255))),(174,235,190,243,'일',dict(fill='keep',size=10,stroke=1,color=(235,235,235),shadow=(40,30,30,255))),(344,123,378,143,'읽음',dict(size=13,stroke=1))]
S['OPTION1']=[(152,149,332,174,'초기 설정으로',dict(size=18,stroke=1,color=(40,40,40),shadow=(235,235,235,255)))]
S['OPTION2']=[(2,72,180,98,'초기 설정으로',dict(size=19,stroke=1,color=(215,120,20),shadow=(90,40,10,255)))]
P=dict(fill='bg',color=(28,28,28),shadow=None)
def pp(**k): d=dict(P); d.update(k); return d
S['KEYWBG']=[(163,5,317,28,'키워드 선택',pp(size=15))]
S['KEYWBG2']=[(163,5,317,28,'키워드 선택',pp(size=15))]
S['GAZOUBG']=[(185,38,274,52,'이미지 선택',pp(size=13))]
S['GAZOUBG2']=[(193,11,287,31,'이미지 선택',pp(size=15))]
S['SMEMOBG']=[(198,5,297,27,'서고 확인',pp(size=15))]
S['SMEMOBG2']=[(201,4,294,28,'서고 확인',pp(size=15))]
S['SCENEBG']=[(150,30,345,61,'장면 하이라이트',pp(size=15,color=(120,120,120)))]
S['ARIHHBG']=[(151,11,300,31,'알리바이표 편집',pp(size=15))]
S['JISYOBG']=[(214,4,275,26,'나고무 메모',pp(size=15,overflow=30))]
S['SATUBG']=[(178,5,318,30,'살해 순서 메모',pp(size=16))]+  [(x0,36,x1,55,t,pp(size=14)) for (x0,x1),t in zip([(93,150),(188,242),(280,335),(373,430)],['1일째','2일째','3일째','4일째'])]+  [(x0,154,x1,172,t,pp(size=14)) for (x0,x1),t in zip([(93,150),(186,242),(278,335)],['5일째','6일째','7일째'])]+  [(30,61,74,82,'이름',pp(size=14)),(30,92,74,113,'모방',pp(size=14)),(30,178,74,199,'이름',pp(size=14)),(30,209,74,230,'모방',pp(size=14)),
   (288,211,422,233,'구조가 오는 날!!',pp(size=14,color=(140,20,20)))]
S['ATTENT']=[(0,100,479,175,'',dict(fill='bg')),(24,106,470,124,'이 이야기는 픽션입니다.',dict(fill='keep',align='left',size=15,color=(20,20,20),shadow=None)),(24,150,470,168,'실존하는 개인, 기업, 단체와는 일절 관계가 없습니다.',dict(fill='keep',align='left',size=15,color=(20,20,20),shadow=None))]
def boxed(region,rows,size=None,color=None):
    x0,y0,x1,y1=region
    sp=[(x0,y0,x1,y1,'',dict(fill='flat'))]
    for (rx,ry0,ry1),t in rows:
        o=dict(fill='keep',align='left',size=size or (ry1-ry0+2),shadow=(0,0,0,160))
        if color: o['color']=color
        sp.append((rx,ry0,x1,ry1,t,o))
    return sp
W=(235,235,235)
S['BUKEI1']=boxed((36,64,326,176),[((40,72,88),'부주의한 판단은 큰 실수를'),((40,98,115),'불러일으킵니다.'),((40,126,142),'곳곳에 힌트가 있으니'),((40,152,169),'주의 깊게 살펴봅시다.')],color=(200,220,200))
S['TUT01']=boxed((82,80,400,184),[((96,82,95),'자기 방의 『추리』 커맨드에서는'),((96,104,117),'사건 현장 정보와 사진 열람,'),((96,126,139),'살해 순서 목록 재편집,'),((96,148,161),'알리바이표 편집 등을 할 수 있습니다.')],color=W)
S['TUT02']=boxed((82,79,400,184),[((94,80,93),'또한 서재에서 살해 순서 메모는'),((94,102,114),'한 번 결정하면 다음 날까지'),((94,124,137),'변경할 수 없습니다.'),((94,146,159),'아직 고민 중이라면 자기 방에서'),((94,168,181),'추리하는 것을 추천합니다.')],color=W)
S['TUT03']=boxed((82,79,400,184),[((95,80,93),'편집한 살해 순서 메모는 매일 서재에서'),((95,102,115),'히오리와 함께 확인하지 않으면 그날'),((95,124,137),'노려지는 인물에게 위험을 알릴'),((95,146,159),'수 없습니다.')],color=W)
def lefts(rows,**k):
    out=[]
    for (x0,y0,x1,y1),t in rows:
        o=dict(align='left',size=y1-y0-1,color=(240,240,240)); o.update(k)
        out.append((x0,y0,x1,y1,t,o))
    return out
ROLL=[((1,73,159,94),'기획·시나리오'),((1,96,211,120),'하시모토 미사  니시노미야 유키'),((1,120,92,143),'미술 감독'),
  ((1,144,113,167),'미야나가 고이치로'),((1,168,380,191),'오프닝      도미노 유키  우에하라 준코'),((1,193,46,215),'음악'),((1,217,92,239),'하시모토 미사'),
  ((1,241,226,262),'캐릭터 디자인'),((1,264,91,287),'니시노 고지'),((1,288,156,310),'프로듀서'),((1,312,188,335),'이노우에 게이이치  무네키요 노리유키'),
  ((1,336,316,358),'이그제큐티브 프로듀서'),((1,360,91,383),'기타즈미 고이치')]
S['OPROLL']=[(x0,y0,x1,y1,t,dict(align='left',size=y1-y0-3,color=(240,240,240),squeeze=True)) for (x0,y0,x1,y1),t in ROLL]
S['SMEMO1']=[(46,200,140,218,'낡은 책장―',dict(align='left')),(46,229,140,248,'하얀 책장―',dict(align='left')),
             (46,260,152,278,'갈색 책장―',dict(align='left')),(46,290,170,308,'책상 위 책장―',dict(align='left'))]
S['OMKMENU1']=[(0,3,86,28,'조사 일기',dict(size=18)),(93,3,180,28,'조사 일기',dict(size=18)),(0,40,86,65,'음악 감상',dict(size=18)),(93,40,180,65,'음악 감상',dict(size=18)),
               (0,77,48,101,'책장',dict(size=18)),(56,77,104,101,'책장',dict(size=18))]
D=(40,40,40); G=(200,200,200,255)
S['MAPBGB1']=[(79,9,101,26,'르로이',dict(fill=G,color=D,shadow=None,size=9)),(147,13,166,22,'뱀',dict(fill=G,color=D,shadow=None,size=10)),
              (80,57,105,73,'마법',dict(fill=G,color=D,shadow=None,size=10)),(126,57,151,73,'문',dict(fill=G,color=D,shadow=None,size=10))]
S['ARIH3']=[(15,10,44,23,'시간',dict(fill='bg',color=(61,70,150),shadow=None,size=12))]
S['ARIH3A']=[(15,8,44,21,'시간',dict(fill='bg',color=(61,70,150),shadow=None,size=12))]
def texts():
    return [s[4] for v in S.values() for s in v]
def hook(enc):
    res={}
    for n,spec in S.items():
        res[n+'.MPB'],_=labelfix.patch(n,spec)
    print('labels',len(res))
    return res
