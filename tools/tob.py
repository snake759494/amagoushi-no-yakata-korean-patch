import struct
def load(path):
    return load_bytes(open(path,'rb').read(),path)
def load_bytes(d,path='?'):
    h=list(struct.unpack('<8I',d[:32])); so=h[4]
    end=h[7] if h[7] else h[1]
    s=bytes(b^0xda for b in d[so:end])
    ops=[]; p=h[5]+4
    while p<so:
        L=d[p]
        if L==0 and p+4>=so and not any(d[p:so]): break
        if L==0: raise ValueError("zero op at %x in %s"%(p,path))
        ops.append((p,d[p],d[p+1],d[p:p+2*L])); p+=2*L
    return dict(d=d,h=h,so=so,end=end,s=s,ops=ops)
def cstr(s,v):
    return s[v:s.index(b'\0',v)]

TEXT_OPS={0x48:2,0x63:6,0x5f:2,0x53:12}   # op -> byte offset of u16 (string offset/4)
def text_refs(t):
    """yield (op_index, op, argpos, str_offset)"""
    for k,(p,L,op,a) in enumerate(t['ops']):
        if op in TEXT_OPS and len(a)>=TEXT_OPS[op]+2:
            ap=TEXT_OPS[op]
            yield k,op,ap,struct.unpack('<H',a[ap:ap+2])[0]*4
def rebuild(t, newtext):
    """newtext: {(op_index): bytes}  (without NUL). Returns new file bytes.
    Strings referenced only by op 0x48 are released into a free pool that new strings reuse."""
    d=bytearray(t['d']); h=list(t['h']); so=t['so']; s=bytearray(t['s'])
    refs=list(text_refs(t))
    # offsets referenced by anything other than 0x48 must be preserved
    keep=set()
    for k,op,ap,v in refs:
        if op!=0x48: keep.add(v)
    for p,L,op,a in t['ops']:
        if op==0x30: keep.add(struct.unpack('<H',a[2:4])[0]*4)
        if op==0x66:
            for kk in range(2,len(a)-1,2): keep.add(struct.unpack('<H',a[kk:kk+2])[0]*4)
    # free pool: 0x48 targets that we replace and that are not kept
    replaced={k for k in newtext if not isinstance(k,tuple)}
    freeable={}
    for k,op,ap,v in refs:
        if op==0x48 and v not in keep: freeable.setdefault(v,[]).append(k)
    free=[]  # (start,end) byte ranges, 4-aligned start
    for v,ks in freeable.items():
        if all(k in replaced for k in ks):
            e=s.index(b'\0',v)
            end=(e+1+3)&~3
            free.append([v,end])
    # merge ranges; ensure we don't eat into strings that start right after (end computed to next 4-align;
    # next string starts on 4-alignment so fine), but only if the padding bytes are zero or we own them
    free.sort()
    merged=[]
    for a_,b_ in free:
        if merged and merged[-1][1]>=a_: merged[-1][1]=max(merged[-1][1],b_)
        else: merged.append([a_,b_])
    for a_,b_ in merged: s[a_:b_]=b'\0'*(b_-a_)
    cache={}
    def alloc(bs):
        need=len(bs)+1; need4=(need+3)&~3
        if bs in cache: return cache[bs]
        for r in merged:
            if r[1]-r[0]>=need4:
                off=r[0]; r[0]+=need4
                s[off:off+len(bs)]=bs; s[off+len(bs)]=0
                cache[bs]=off; return off
        off=len(s); s.extend(bs+b'\0'); 
        while len(s)%4: s.append(0)
        cache[bs]=off; return off
    for k,bs in newtext.items():
        if isinstance(k,tuple): k,ap=k
        else: ap=None
        p,L,op,a=t['ops'][k]
        off=alloc(bs)
        assert off%4==0 and off//4<0x10000, off
        if ap is None: ap=TEXT_OPS[op]
        struct.pack_into('<H',d,p+ap,off//4)
    # rebuild: header+code | strings | tail
    old_end=t['end']
    tail=bytes(d[old_end:])
    struct.pack_into('<I',s,0,len(s))
    out=bytearray(d[:so])+bytes(b^0xda for b in s)
    new_end=len(out)
    delta=new_end-old_end
    out+=tail
    h[1]+=delta
    if h[7]: h[7]=new_end
    struct.pack_into('<8I',out,0,*h)
    return bytes(out)
