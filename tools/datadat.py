import struct,gzip,io,sys
sys.path.insert(0,__import__('os').path.dirname(__file__))
from pspfs import read_toc
CH=0x80000
def compress(u):
    chunks=[u[i:i+CH] for i in range(0,len(u),CH)] or [b'']
    gz=[gzip.compress(c,9,mtime=0) for c in chunks]
    n=len(gz); hdr=8+4*n; offs=[]; o=hdr
    for g in gz: offs.append(o); o+=len(g)
    return struct.pack('<II',n,CH)+struct.pack('<%dI'%n,*offs)+b''.join(gz)
def rebuild(orig_path, replacements):
    """replacements: name -> uncompressed bytes. Unchanged files keep their bytes/offsets; changed ones are
    written in place when they fit, else appended."""
    E=read_toc(orig_path); data=bytearray(open(orig_path,'rb').read())
    byname={e['name']:e for e in E}
    offs=sorted(set(e['off'] for e in E))+[len(data)]
    nxt={o:offs[i+1] for i,o in enumerate(offs[:-1])}
    for name,u in replacements.items():
        e=byname[name]
        blob=compress(u) if e['usize'] else u
        room=nxt[e['off']]-e['off']
        shared=sum(1 for x in E if x['off']==e['off'])>1
        if len(blob)<=room and not shared:
            data[e['off']:e['off']+room]=blob+b'\0'*(room-len(blob))
        else:
            while len(data)%0x800: data.append(0)
            e['off']=len(data); data+=blob
        e['size']=len(blob); e['usize']=len(u) if e['usize'] else 0
    while len(data)%0x800: data.append(0)
    for e in E:
        o=16+32*e['i']
        struct.pack_into('<3I',data,o+0x14,e['usize'],e['size'],e['off'])
    return bytes(data)
