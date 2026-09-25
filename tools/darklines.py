import numpy as np
from PIL import Image
def boxes(a,thr=80,colgap=25,rowgap=2,minh=5):
    a=a.astype(int); lum=a[...,:3].max(axis=2); m=(lum<thr)&(a[...,3]>200)
    H,W=m.shape; out=[]
    rows=np.where(m.any(axis=1))[0]
    if len(rows)==0: return out
    s=p=rows[0]
    for r in list(rows[1:])+[None]:
        if r is not None and r-p<=rowgap: p=r; continue
        if p-s+1>=minh:
            cols=np.where(m[s:p+1].any(axis=0))[0]
            cs=ce=cols[0]
            for c in list(cols[1:])+[None]:
                if c is not None and c-ce<=colgap: ce=c; continue
                if ce-cs>6: out.append((int(cs),int(s),int(ce),int(p)))
                if c is not None: cs=ce=c
        if r is not None: s=p=r
    return out
