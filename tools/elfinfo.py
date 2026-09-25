import struct,sys
d=open(sys.argv[1],'rb').read()
e_phoff=struct.unpack('<I',d[0x1c:0x20])[0]
seg=struct.unpack('<8I',d[e_phoff:e_phoff+32]); base_off=seg[1]; vaddr=seg[2]
def v2o(v): return v-vaddr+base_off
for mi_off in (seg[3], seg[3]+base_off):
    nm=d[mi_off+4:mi_off+32]
    if nm[:1].isalpha(): break
gp,ent_top,ent_end,stub_top,stub_end=struct.unpack('<5I',d[mi_off+32:mi_off+52])
print(nm.split(b'\0')[0], hex(gp))
o=v2o(stub_top)
while o<v2o(stub_end):
    nm_p,ver,flag,esz,vcnt,fcnt,nids,funcs=struct.unpack('<IHHBBHII',d[o:o+20])
    nm=d[v2o(nm_p):v2o(nm_p)+40].split(b'\0')[0].decode()
    print(nm, ' '.join('%08x@%x'%(struct.unpack('<I',d[v2o(nids)+4*k:v2o(nids)+4*k+4])[0],funcs+8*k) for k in range(fcnt)))
    o+=esz*4
