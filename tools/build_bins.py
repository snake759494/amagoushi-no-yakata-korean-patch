"""KW.BIN keyword names and NAGOMEM memos."""
import os,json,struct
import kenc
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT=os.path.join(R,'work','ext')
T=json.load(open(os.path.join(R,'translation','bins_out.json'),encoding='utf-8'))
def texts():
    out=list(T['keywords'].values())
    for m in T['memos'].values(): out+= [m['title'],m['body']]
    return out
def hook(enc):
    res={}
    d=bytearray(open(os.path.join(EXT,'KW.BIN'),'rb').read())
    kw={k.encode('cp932'):v for k,v in T['keywords'].items()}
    for i in range(len(d)//300):
        o=i*300+0x104
        t=bytes(d[o:o+0x20]).split(b'\0')[0]
        if t in kw:
            b=kenc.encode_dbcs(kw[t],enc)
            assert len(b)<0x20,(kw[t],len(b))
            d[o:o+0x20]=b+b'\0'*(0x20-len(b))
    res['KW.BIN']=bytes(d)
    src=json.load(open(os.path.join(R,'translation','bins_src.json'),encoding='utf-8'))
    bykey={(m['title'],m['body']):T['memos'][m['id']] for m in src['memos']}
    for k in range(11):
        n='NAGOMEM%02d.BIN'%k
        d=bytearray(open(os.path.join(EXT,n),'rb').read()); cnt=struct.unpack('<I',d[:4])[0]
        for i in range(cnt):
            o=8+i*0x414
            title=bytes(d[o:o+0x28]).split(b'\0')[0].decode('cp932'); body=bytes(d[o+0x28:o+0x414]).split(b'\0')[0].decode('cp932')
            tr=bykey[(title,body)]
            tb=kenc.encode_dbcs(tr['title'],enc); bb=kenc.encode_dbcs(tr['body'],enc)
            assert len(tb)<0x28 and len(bb)<0x3ec
            d[o:o+0x28]=tb+b'\0'*(0x28-len(tb)); d[o+0x28:o+0x414]=bb+b'\0'*(0x3ec-len(bb))
        res[n]=bytes(d)
    return res
