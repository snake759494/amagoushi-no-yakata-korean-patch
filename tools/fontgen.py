"""Rebuild FONT.MPB/FONT.BIN: keep ASCII + fullwidth symbols/alnum, fill the rest with Hangul."""
import struct,sys,os
import numpy as np
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,os.path.dirname(__file__))
import imy
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
TTF=os.path.join(ROOT,'SeoulHangangB.ttf')
EXT=os.path.join(ROOT,'work','ext')
EBOOT_TBL_OFF=0xe5e68   # u16[256] byte->code table in decrypted EBOOT
# single-byte values whose codes we repurpose for Hangul (keep a0-a5 punctuation)
SB_BYTES=list(range(0xa6,0xe0))
def load_orig():
    d=open(os.path.join(EXT,'FONT.BIN'),'rb').read(); n=struct.unpack('<I',d[:4])[0]
    E=[struct.unpack('<HBB',d[4+4*i:8+4*i]) for i in range(n)]
    b=open(os.path.join(EXT,'FONT.MPB'),'rb').read()
    m,pix,_=imy.decode(b[0x40:])
    img=imy.to_img4(imy.unswizzle(pix,m['stride'],m['h']),m['stride'],m['h'])
    return E,b[:0x40],m,img
def sb_table():
    t=open(os.path.join(ROOT,'work','iso','EBOOT.dec'),'rb').read()[EBOOT_TBL_OFF:EBOOT_TBL_OFF+512]
    return [struct.unpack('<H',t[2*i:2*i+2])[0] for i in range(256)]
BAD_TRAIL={0x5c,0x7b,0x7c,0x7d,0x7f}
def dbcs_codes(reserved):
    for lead in list(range(0x88,0xa0))+list(range(0xe0,0xeb)):
        for tr in list(range(0x40,0x7f))+list(range(0x80,0xfd)):
            if lead==0x88 and tr<0x9f: continue
            if tr in BAD_TRAIL: continue
            c=(lead<<8)|tr
            if c in reserved: continue
            yield c
def keep_code(c):
    return c<0x80 or (0x8140<=c<0x8200) or (0x824f<=c<=0x829a)
def render_glyph(ch,font,size=16):
    im=Image.new('L',(size,size),0); dr=ImageDraw.Draw(im)
    bb=dr.textbbox((0,0),ch,font=font)
    w=bb[2]-bb[0]; h=bb[3]-bb[1]
    x=(size-w)//2-bb[0]; y=(size-h)//2-bb[1]
    dr.text((x,y),ch,font=font,fill=255)
    a=np.array(im)
    return a
def build(hangul_sb, hangul_db, out_dir, fontsize=15, space_w=None):
    """hangul_sb: list of syllables for single-byte slots (ordered, len<=len(SB_BYTES));
    hangul_db: syllables needing 2-byte codes. Returns (enc_map: syllable->bytes, files)"""
    E,mpbhdr,m,img=load_orig()
    tbl=sb_table()
    orig={c:(x,w,i) for i,(c,x,w) in enumerate(E)}
    entries={}   # code -> (x,w,glyph16x16 array)
    def orig_glyph(i):
        r,c=divmod(i,16); return img[r*16:r*16+16,c*16:c*16+16]
    sb_codes=[tbl[b] for b in SB_BYTES]
    for c,x,w in E:
        if keep_code(c) and c not in sb_codes:
            entries[c]=(x,w,orig_glyph(orig[c][2]))
    if space_w is not None:
        for sc in (0x20,0x8140,0x8145):
            x,w,g=entries[sc]; entries[sc]=(0,space_w,np.zeros_like(g))
    font=ImageFont.truetype(TTF,fontsize)
    enc={}
    def put(code,ch):
        a=render_glyph(ch,font)
        a4=(a.astype(np.int32)*15+127)//255
        cols=np.where(a4.max(axis=0)>0)[0]
        if len(cols)==0: x,w=0,8
        else: x=int(cols[0]); w=int(cols[-1]-cols[0]+1)
        entries[code]=(x,w,a4.astype(np.uint8))
    assert len(hangul_sb)<=len(SB_BYTES)
    for b,ch in zip(SB_BYTES,hangul_sb):
        put(tbl[b],ch); enc[ch]=bytes([b])
    reserved=set(entries)
    gen=dbcs_codes(reserved)
    for ch in hangul_db:
        c=next(gen); put(c,ch); enc[ch]=bytes([c>>8,c&255])
    codes=sorted(entries)
    assert len(codes)<=2560, len(codes)
    # FONT.BIN
    fb=struct.pack('<I',len(codes))+b''.join(struct.pack('<HBB',c,entries[c][0],entries[c][1]) for c in codes)
    # texture
    H=m['h']; W=m['stride']*2
    atlas=np.zeros((H,W),np.uint8)
    for i,c in enumerate(codes):
        r,cc=divmod(i,16); atlas[r*16:r*16+16,cc*16:cc*16+16]=entries[c][2]
    lin=(atlas[:,0::2] | (atlas[:,1::2]<<4)).astype(np.uint8).tobytes()
    sw=imy.swizzle(lin,m['stride'],H)
    body=imy.encode(m,sw,chunk_rows=64)
    mpb=mpbhdr+body
    Image.fromarray(atlas*17).save(os.path.join(out_dir,'font_atlas.png'))
    return enc, fb, mpb
