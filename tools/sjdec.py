import unicodedata
def dec(b):
    out='';i=0
    while i<len(b):
        c=b[i]
        if 0x81<=c<0xa0 or 0xe0<=c<0xfd:
            out+=b[i:i+2].decode('cp932','replace'); i+=2
        elif 0xa6<=c<=0xdd:
            k=bytes([c]).decode('cp932'); kk=unicodedata.normalize('NFKC',k)
            out+=chr(ord(kk)-0x60) if 'ァ'<=kk<='ン' else kk; i+=1
        elif 0xa1<=c<=0xa5 or c>=0xde and c<0xe0:
            out+=unicodedata.normalize('NFKC',bytes([c]).decode('cp932')); i+=1
        elif c<0x20 or c>=0x7f: out+='{%02x}'%c; i+=1
        else: out+=chr(c); i+=1
    return out
