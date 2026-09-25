import struct
def read(path):
    raw=open(path,'rb').read()
    n=struct.unpack('<I',raw[:4])[0]
    hdr=bytes((b-0x7f)&0xff for b in raw[8:0x14+20*n])
    ents=[]
    for i in range(n):
        o=0x14+20*i-8
        off=struct.unpack('<I',hdr[o:o+4])[0]; nm=hdr[o+4:o+20]
        ents.append([off,nm])
    files=[]
    for i,(off,nm) in enumerate(ents):
        end=ents[i+1][0] if i+1<n else len(raw)
        files.append((nm,raw[off:end]))
    return raw[:8],files
def write(head8,files):
    n=len(files)
    body=bytearray(12)
    off=0x14+20*n; blobs=[]
    for nm,data in files:
        body+=struct.pack('<I',off)+nm; off+=len(data)
    return head8+bytes((b+0x7f)&0xff for b in body)+b''.join(d for nm,d in files)
