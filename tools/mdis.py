import capstone,struct,sys
D=open('work/iso/EBOOT.dec','rb').read()
BASE_OFF=0x60; VADDR=0x08804000
import struct
phoff=struct.unpack('<I',D[0x1c:0x20])[0]; seg=struct.unpack('<8I',D[phoff:phoff+32]); BASE_OFF=seg[1]
md=capstone.Cs(capstone.CS_ARCH_MIPS,capstone.CS_MODE_MIPS32+capstone.CS_MODE_LITTLE_ENDIAN); md.skipdata=True
def v2o(v): return v-VADDR+BASE_OFF
def dis(v,n):
    o=v2o(v)
    for i in md.disasm(D[o:o+4*n],v): print('%08x: %s %s'%(i.address,i.mnemonic,i.op_str))
if __name__=='__main__': dis(int(sys.argv[1],16),int(sys.argv[2]))
