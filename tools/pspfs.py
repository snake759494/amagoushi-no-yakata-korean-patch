import struct,sys
def read_toc(path):
    f=open(path,'rb'); h=f.read(16)
    assert h[:8]==b'PSPFS_V1',h
    n=struct.unpack('<I',h[8:12])[0]
    raw=f.read(32*n); ents=[]
    for i in range(n):
        e=raw[i*32:i*32+32]
        name=e[:0x14].split(b'\0')[0].decode('ascii')
        a,b,c=struct.unpack('<3I',e[0x14:0x20])
        ents.append(dict(i=i,name=name,usize=a,size=b,off=c))
    return ents
if __name__=='__main__':
    for e in read_toc(sys.argv[1]): print(e['i'],e['name'],hex(e['usize']),hex(e['size']),hex(e['off']))

import zlib,gzip
def unpack_entry(f,e):
    f.seek(e['off']); d=f.read(e['size'])
    if not e['usize']: return d
    n,chunk=struct.unpack('<II',d[:8])
    offs=list(struct.unpack('<%dI'%n,d[8:8+4*n]))+[len(d)]
    u=b''.join(gzip.decompress(d[offs[k]:offs[k+1]]) for k in range(n))
    assert len(u)==e['usize'],(e['name'],len(u),e['usize']); return u
