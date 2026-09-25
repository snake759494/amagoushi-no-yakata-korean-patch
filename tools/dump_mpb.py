import sys,os,struct
sys.path.insert(0,os.path.dirname(__file__))
import mpb,numpy as np
from PIL import Image
out=sys.argv[2]; os.makedirs(out,exist_ok=True)
info=[]
for n in sorted(os.listdir(sys.argv[1])):
    if not n.upper().endswith('.MPB'): continue
    b=open(os.path.join(sys.argv[1],n),'rb').read()
    try: L=mpb.decode_all(b)
    except Exception as e: print('ERR',n,e); continue
    for i,(o,m,img,pal) in enumerate(L):
        rgba=mpb.to_rgba(img,pal)
        if rgba is None: continue
        Image.fromarray(np.ascontiguousarray(rgba),'RGBA').save(os.path.join(out,'%s_%d.png'%(n[:-4],i)))
        info.append((n,i,m['bpp'],rgba.shape[1],rgba.shape[0]))
print(len(info))
