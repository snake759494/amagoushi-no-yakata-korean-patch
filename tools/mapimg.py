"""Compose / decompose MPB 'MAP' tiled images."""
import struct,sys,os
sys.path.insert(0,os.path.dirname(__file__))
import mpb,imy,numpy as np
def header(b):
    hs=struct.unpack('<I',b[4:8])[0]
    ver=b[3]; ntex,cols,rows,tw,th,iw,ih=struct.unpack('<7H',b[0x0e:0x1c])
    m=[struct.unpack('<H',b[i:i+2])[0] for i in range(0x20,0x20+2*cols*rows,2)]
    return dict(hs=hs,ver=ver,bpp=b[0xd],ntex=ntex,cols=cols,rows=rows,tw=tw,th=th,iw=iw,ih=ih,map=m)
def compose(b,cell=None,off=None):
    H=header(b); L=mpb.decode_all(b); o,m,img,pal=L[0]
    rgba=mpb.to_rgba(img,pal)
    tw,th=H['tw'],H['th']
    if H['ver']==0:
        cw=tw; ox=0
    else:
        cw=cell or (tw+2); ox=1 if off is None else off
    per=rgba.shape[1]//cw
    out=np.zeros((H['rows']*th,H['cols']*tw,4),np.uint8)
    for i,t in enumerate(H['map']):
        if t==0: continue
        k=(t&0x7fff)-1
        cx,cy=(k%per)*cw+ox,(k//per)*(th+2*ox)+ox
        r,c=divmod(i,H['cols'])
        out[r*th:(r+1)*th,c*tw:(c+1)*tw]=rgba[cy:cy+th,cx:cx+tw]
    return H,out[:H['ih'],:H['iw']]
if __name__=='__main__':
    from PIL import Image
    b=open(sys.argv[1],'rb').read(); H,im=compose(b)
    bg=Image.new('RGBA',(im.shape[1],im.shape[0]),(40,40,40,255)); bg.alpha_composite(Image.fromarray(np.ascontiguousarray(im),'RGBA')); bg.save(sys.argv[2]); print(H)

def _quantize(rgba, ncolors=256):
    from PIL import Image
    im=Image.fromarray(np.ascontiguousarray(rgba),'RGBA')
    q=im.quantize(colors=ncolors,method=Image.Quantize.FASTOCTREE,dither=Image.Dither.NONE)
    pal=np.array(q.getpalette(rawmode='RGBA')[:ncolors*4] if True else [],np.uint8)
    pal=np.frombuffer(bytes(q.getpalette(rawmode='RGBA')),np.uint8).reshape(-1,4)
    idx=np.array(q,np.uint8)
    if len(pal)<ncolors: pal=np.vstack([pal,np.zeros((ncolors-len(pal),4),np.uint8)])
    return idx,pal[:ncolors]
def rebuild(b, rgba):
    """Re-encode MPB 'b' with new full image rgba (same size as compose output)."""
    H=header(b)
    o=H['hs']; m0=imy.parse(b[o:])
    bpp=m0['bpp']
    if True:
        tw,th=H['tw'],H['th']; pad=0 if H['ver']==0 else 1; cw=tw+2*pad; chh=th+2*pad
        flags=[t&0x8000 for t in H['map']]
        full=np.zeros((H['rows']*th,H['cols']*tw,4),np.uint8)
        full[:rgba.shape[0],:rgba.shape[1]]=rgba
        texw=m0['stride']*8//bpp
        per=texw//cw
        tiles=[];newmap=[]
        for i in range(H['cols']*H['rows']):
            r,c=divmod(i,H['cols'])
            t=full[r*th:(r+1)*th,c*tw:(c+1)*tw]
            if H['map'][i]==0: newmap.append(0); continue
            if t[...,3].max()==0 and H['ver']==1: newmap.append(0); continue
            key=t.tobytes()
            found=None
            for j,tt in enumerate(tiles):
                if tt==key: found=j;break
            if found is None: tiles.append(key); found=len(tiles)-1
            newmap.append(found+1)
        n=len(tiles); rows_needed=(n+per-1)//per
        texh=m0['h']
        while rows_needed*chh>texh: texh*=2
        tex=np.zeros((texh,texw,4),np.uint8)
        for j,key in enumerate(tiles):
            t=np.frombuffer(key,np.uint8).reshape(th,tw,4)
            p=np.pad(t,((pad,pad),(pad,pad),(0,0)),mode='edge') if pad else t
            x,y=(j%per)*cw,(j//per)*chh
            tex[y:y+chh,x:x+cw]=p
        H['map']=[(v|flags[i]) if v else 0 for i,v in enumerate(newmap)]; H['ntex']=n+1
    # encode texture
    h,w=tex.shape[:2]
    m=dict(m0)
    if bpp==8:
        idx,pal=_quantize(tex,256); m['npal']=256; m['pal']=pal.tobytes(); stride=w; raw=idx.tobytes()
    elif bpp==4:
        idx,pal=_quantize(tex,16); m['npal']=16; m['pal']=pal.tobytes(); stride=w//2
        raw=(idx[:,0::2]|(idx[:,1::2]<<4)).astype(np.uint8).tobytes()
    elif bpp==32:
        stride=w*4; raw=tex.astype(np.uint8).tobytes(); m['npal']=0; m['pal']=b''
    else: raise ValueError(bpp)
    m['stride']=stride; m['h']=h
    if h%8==0 and bpp in (4,8): raw=imy.swizzle(raw,stride,h)
    # chunk rows: tile height of texture pages; for ver0 tile th, else whole
    chunk=64
    if bpp==32:
        m['flags']=(m['flags']&~2)|1   # store raw for 32bpp
        body=imy.encode(m,raw,raw=True)
    else:
        body=imy.encode(m,raw,chunk_rows=chunk)
    hdr=bytearray(b[:o])
    struct.pack_into('<H',hdr,0x0e,H['ntex'])
    for i,t in enumerate(H['map']): struct.pack_into('<H',hdr,0x20+2*i,t)
    return bytes(hdr)+body
