import pickle,sys,re
sys.path.insert(0,'tools')
from mdis import *
ins=pickle.load(open('work/ins.pkl','rb'))
def o2v(o): return o-BASE_OFF+VADDR
def xref(target):
    hi=(target+0x8000)>>16; lo=target-(hi<<16)
    res=[]
    for k,(a,m,o) in enumerate(ins):
        if m=='lui' and o.endswith(', 0x%x'%hi):
            reg=o.split(',')[0]
            for j in range(k+1,min(k+40,len(ins))):
                a2,m2,o2=ins[j]
                if reg in o2 and m2 in('addiu','ori','lw','lh','lhu','lb','lbu','sw','sh','sb') and re.search(r'(-?0x[0-9a-f]+|\b-?\d+\b)\(%s\)|%s, (-?0x[0-9a-f]+|-?\d+)$'%(re.escape(reg),re.escape(reg)),o2):
                    m_=re.search(r'(-?0x[0-9a-f]+|-?\d+)(?=\(%s\))|(?<=%s, )(-?0x[0-9a-f]+|-?\d+)$'%(re.escape(reg),re.escape(reg)),o2)
                    if m_ and int(m_.group(0),0)==lo: res.append(a2)
    return res
if __name__=='__main__':
    t=int(sys.argv[1],16)
    if len(sys.argv)>2 and sys.argv[2]=='off': t=o2v(t)
    print(hex(t),[hex(x) for x in xref(t)])
