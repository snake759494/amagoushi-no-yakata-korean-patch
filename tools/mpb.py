import struct,sys,os
sys.path.insert(0,os.path.dirname(__file__))
import imy
import numpy as np
def parse(b):
    assert b[:3]==b'MAP', b[:4]
    hs=struct.unpack('<I',b[4:8])[0]
    return hs
def decode_all(b):
    """returns list of (offset, meta, image array (palette idx), palette)"""
    out=[]; o=struct.unpack('<I',b[4:8])[0]
    while o+0x20<=len(b) and b[o:o+4]==b'IMY\0':
        m,pix,end=imy.decode(b[o:])
        stride=m['stride']; h=m['h']
        if m['bpp']==4:
            img=imy.to_img4(imy.unswizzle(pix,stride,h),stride,h) if h%8==0 else imy.to_img4(pix,stride,h)
        elif m['bpp']==8:
            img=np.frombuffer(imy.unswizzle(pix,stride,h) if h%8==0 else pix,np.uint8).reshape(h,stride)
        elif m['bpp']==32:
            img=np.frombuffer(pix,np.uint8).reshape(h,stride//4,4)
        else:
            img=np.frombuffer(pix,np.uint8).reshape(h,stride)
        pal=np.frombuffer(m['pal'],np.uint8).reshape(-1,4) if m['npal'] else None
        out.append((o,m,img,pal))
        o+= 0x20+4*m['npal']+end if False else o_next(b,o,m,end)
        o=((o+3)&~3)
    return out
def o_next(b,o,m,end):
    return o+0x20+4*m['npal']+end - o if False else o+0x20+4*m['npal']+end
def to_rgba(img,pal):
    if pal is None: return img if img.ndim==3 else None
    return pal[img]
