import re
PUNCT_MAP={'“':'「','”':'」','‘':'『','’':'』','~':'～','ー':'―','—':'―','…':'…','‥':'・・'}
def encode(text,enc):
    out=bytearray()
    text=text.replace('・','·')
    intag=False
    for ch in text:
        if ch=='<': intag=True
        if ch=='>': intag=False
        if ch==' ' and not intag: out.append(0xa5); continue
        if ch in enc: out+=enc[ch]; continue
        o=ord(ch)
        if o<0x80: out.append(o); continue
        ch2=PUNCT_MAP.get(ch,ch)
        if ch2 in enc: out+=enc[ch2]; continue
        b=ch2.encode('cp932')
        if len(b)==1: raise ValueError('halfwidth kana not allowed: %r'%ch)
        out+=b
    return bytes(out)
def hangul_chars(text):
    return {c for c in text if 0xac00<=ord(c)<=0xd7a3}

_TBL=None
def encode_dbcs(text,enc):
    """Like encode() but never emits single-byte kana codes (for EBOOT/BIN strings)."""
    global _TBL
    if _TBL is None:
        import fontgen; _TBL=fontgen.sb_table()
    b=encode(text,enc)
    out=bytearray(); i=0
    while i<len(b):
        c=b[i]
        if 0x81<=c<0xa0 or 0xe0<=c<0xfd: out+=b[i:i+2]; i+=2; continue
        if c==0xa5: out.append(0x20); i+=1; continue
        if 0xa0<=c<0xe0:
            code=_TBL[c]; out+=bytes([code>>8,code&255]); i+=1; continue
        out.append(c); i+=1
    return bytes(out)
