"""IMY image codec (Amagoushi no Yakata Portable).
header 0x20: 'IMY\0', u32 total_uncompressed(incl hdr+pal), u16 stride, u8 flags, u8 bpp,
u16 height, u16 palcount, then zeros. palette palcount*4 RGBA, then data.
flags bit0=raw. else LZ in 16-bit units (bit1 -> 32/24-bit units)."""
import struct
def parse(b):
    assert b[:4]==b'IMY\0'
    total,stride,flags,bpp,h,npal=struct.unpack('<IHBBHH',b[4:16])
    pal=b[0x20:0x20+4*npal]
    return dict(total=total,stride=stride,flags=flags,bpp=bpp,h=h,npal=npal,pal=pal,data=b[0x20+4*npal:])
def unit_of(flags,bpp):
    if flags&1: return 0
    if flags&2: return 3 if bpp==0x18 else 4
    return 2
def decode(b):
    m=parse(b); d=m['data']; stride=m['stride']; out_len=stride*m['h']
    if m['flags']&1: return m, d[:out_len], len(d)
    u=unit_of(m['flags'],m['bpp'])
    v=struct.unpack('<H',d[:2])[0]; p=2
    if v==0: v=struct.unpack('<I',d[2:6])[0]; p=6
    lit=p+v; cmd=p
    out=bytearray(out_len); o=0
    offs=[-u,-stride,-stride-u,-stride+u]
    while o<out_len:
        c=d[cmd]; cmd+=1
        if c<0x10:
            n=(c+1)*u; out[o:o+n]=d[lit:lit+n]; lit+=n; o+=n
        elif c<0xc0:
            k=c-0x10; s=lit-(k+1)*u; out[o:o+u]=d[s:s+u]; o+=u
        else:
            t=c-0xc0; src=o+offs[t>>4]; n=(t&0xf)+1
            for _ in range(n):
                out[o:o+u]=out[src:src+u]; o+=u; src+=u
    return m, bytes(out[:out_len]), lit
def encode(m, pix, raw=False, chunk_rows=None):
    """16-bit-unit LZ encoder. The game decodes into separate buffers of chunk_rows rows
    (MPB tile height), so no command may cross or reference across a chunk boundary."""
    stride=m['stride']; h=m['h']; assert len(pix)==stride*h
    flags=m['flags']
    if chunk_rows is None: chunk_rows=h
    if raw:
        flags|=1; body=pix
    else:
        flags&=~1; assert not flags&2
        u=2
        cmds=bytearray(); lits=bytearray()
        litidx={}   # value -> last literal unit index
        nlit=0
        csz=stride*chunk_rows
        for c0 in range(0,len(pix),csz):
            chunk=pix[c0:c0+csz]; n=len(chunk)
            o=0; pend=[]
            def flush():
                nonlocal nlit
                while pend:
                    k=min(16,len(pend)); cmds.append(k-1)
                    for x in pend[:k]:
                        lits.extend(x); litidx[x]=nlit; nlit+=1
                    del pend[:k]
            while o<n:
                best=0;bt=0
                for t,off in enumerate((-u,-stride,-stride-u,-stride+u)):
                    s_=o+off
                    if s_<0: continue
                    if off==-u and (o%stride)==0: pass
                    L=0
                    while L<16 and o+L*u<n and chunk[s_+L*u:s_+L*u+u]==chunk[o+L*u:o+L*u+u]: L+=1
                    if L>best: best=L;bt=t
                if best>=1:
                    flush(); cmds.append(0xc0+(bt<<4)+best-1); o+=best*u; continue
                cur=bytes(chunk[o:o+u])
                if not pend and cur in litidx and nlit-1-litidx[cur]<176:
                    cmds.append(0x10+(nlit-1-litidx[cur])); o+=u; continue
                pend.append(cur); o+=u
                if len(pend)==16: flush()
            flush()
        L=len(cmds)
        if 0<L<0x10000: body=struct.pack('<H',L)+bytes(cmds)+bytes(lits)
        else: body=struct.pack('<HI',0,L)+bytes(cmds)+bytes(lits)
    hdr=b'IMY'+bytes(1)+struct.pack('<IHBBHH',0x20+4*m['npal']+stride*h,stride,flags,m['bpp'],h,m['npal'])+bytes(16)
    return hdr+m['pal']+body

def unswizzle(buf, stride, h):
    import numpy as np
    a=np.frombuffer(buf,np.uint8).reshape(h//8, stride//16, 8, 16)
    return a.transpose(0,2,1,3).reshape(h,stride).tobytes()
def swizzle(buf, stride, h):
    import numpy as np
    a=np.frombuffer(buf,np.uint8).reshape(h//8, 8, stride//16, 16)
    return a.transpose(0,2,1,3).reshape(h,stride).tobytes()
def to_img4(buf,stride,h):
    import numpy as np
    a=np.frombuffer(buf,np.uint8)
    img=np.zeros(len(a)*2,np.uint8); img[0::2]=a&15; img[1::2]=a>>4
    return img.reshape(h,stride*2)
