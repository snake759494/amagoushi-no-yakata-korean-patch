"""Speaker name plates in STS_DEF.TOB (table @0x10e90: u32 stroff,u32,u32 color; strings XOR 0xDA at 0x36f50)."""
import os,struct
import kenc
from sjdec import dec
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAMES={'地':'','和':'나고무','日織':'히오리','椿':'츠바키','那須':'나스','暗石':'쿠라이시','鈴奈':'스즈나','静奈':'시즈나','御陵':'미사사기','斑井':'마다라이',
 '男の声':'남자 목소리','男の声Ａ':'남자 목소리A','男の声Ｂ':'남자 목소리B','男の声Ｃ':'남자 목소리C','青年の声':'청년의 목소리','男性':'남성','体格のいい男':'체격 좋은 남자',
 '小太りの男':'뚱뚱한 남자','粗暴な男':'난폭한 남자','青年':'청년','少女の声':'소녀의 목소리','少女の声Ａ':'소녀의 목소리A','少女の声Ｂ':'소녀의 목소리B','少女Ａ':'소녀A','少女Ｂ':'소녀B',
 '女性':'여성','オーナー':'주인','ラジオ':'라디오','女性の声':'여자 목소리','テープ':'테이프','？？？':'???','ぴよ':'삐요','にょん':'뇽'}
EXTRA={'移動':'이동','話す':'말하기','推理':'추리','調べる':'조사','推理２':'추리2','情報':'정보','休憩':'휴식','メモ':'메모','システム':'시스템',
 'ななこカスタム':'나나코 커스텀','奈々子':'나나코','中に入る':'안으로 들어간다','駐車場':'주차장','庭':'정원','シール':'실','井戸':'우물','１Ｆホール':'1층 홀','スタウト':'스타우트',
 'ライス':'라이스','クロフツ':'크로프츠','ルルー':'르루','アシモフ':'아시모프','ノックス':'녹스','オルツィ':'오르치','１ＦＷＣ':'1층 화장실','ハリス':'해리스','２Ｆホール':'2층 홀',
 'ロス':'로스','ミルン':'밀른','予備部屋':'예비실','クイーン':'퀸','ロースン':'로슨','ダイン':'다인','カーター':'카터','カー':'카','アガサ':'애거사','ポー':'포','ドイル':'도일',
 'モーリス':'모리스','アラン':'앨런','２ＦＷＣ':'2층 화장실','母屋地下':'본채 지하','地下物置':'지하 창고','マホウ':'마법','トビラ':'문','ヘビ':'뱀','ルロイ':'르로이',
 '隠し通路':'숨겨진 통로','温室地下':'온실 지하','ボイラー':'보일러','地下道Ａ':'지하도A','地下道Ｂ':'지하도B','地下道Ｃ':'지하도C','地下道Ｄ':'지하도D','地下道Ｅ':'지하도E',
 '森':'숲','自宅':'자택','おまけ斑井':'보너스 마다라이','おまけ那須':'보너스 나스'}
EXTRA_ADDR=list(range(0x1149c,0x11500,12))+list(range(0x36a2c,0x36a38,8))+list(range(0x36a50,0x36e00,0x14))
def texts(): return list(NAMES.values())+list(EXTRA.values())
def hook(enc):
    d=bytearray(open(os.path.join(R,'work','ext','STS_DEF.TOB'),'rb').read())
    S=struct.unpack('<I',d[0x10:0x14])[0]
    x=bytes(b^0xda for b in d)
    tail=bytearray()
    size=struct.unpack('<I',x[S:S+4])[0]; end=S+size
    assert end==len(d)
    n=0
    for i in range(0x10e90,0x11490,12):
        v=struct.unpack('<I',d[i:i+4])[0]
        if not v: continue
        e=x.index(b'\0',S+v); jp=dec(x[S+v:e])
        if jp not in NAMES: continue
        b=kenc.encode_dbcs(NAMES[jp].replace(' ',''),enc)+b'\0'
        newoff=size+len(tail); tail+=b
        struct.pack_into('<I',d,i,newoff); n+=1
    for i in EXTRA_ADDR:
        v=struct.unpack('<I',d[i:i+4])[0]
        if not (4<=v<size): continue
        e=x.index(b'\0',S+v); jp=dec(x[S+v:e])
        if jp not in EXTRA: continue
        b=kenc.encode_dbcs(EXTRA[jp],enc)+b'\0'
        struct.pack_into('<I',d,i,size+len(tail)); tail+=b; n+=1
    while (size+len(tail))%4: tail.append(0)
    d+=bytes(c^0xda for c in tail)
    newsize=size+len(tail)
    xs=struct.pack('<I',newsize); d[S:S+4]=bytes(c^0xda for c in xs)
    struct.pack_into('<I',d,4,len(d))
    print('stsdef names',n)
    return {'STS_DEF.TOB':bytes(d)}
