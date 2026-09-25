"""Tutorial screenshot images: replace boxed Japanese with Korean."""
import os,json
import labelfix
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P=os.path.join(R,'translation','tu_img_out.json')
def load(): return json.load(open(P,encoding='utf-8')) if os.path.exists(P) else {}
def spec(items):
    out=[]
    for it in items:
        x0,y0,x1,y1=it['box']
        out.append((x0,y0,x1,y1,it['ko'],dict(fill='bg',auto=True,size=max(7,y1-y0-1))))
    return out
def texts(): return [it['ko'] for v in load().values() for it in v]
def hook(enc):
    r={}
    for n,items in load().items():
        if not items: continue
        try: r[n+'.MPB']=labelfix.patch(n,spec(items))[0]
        except Exception as e: print('TU FAIL',n,e)
    print('tuimg',len(r)); return r
