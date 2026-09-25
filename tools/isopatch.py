"""Replace /PSP_GAME/USRDIR/DATA.DAT (last file in the image) and optionally EBOOT.BIN in-place."""
import struct,shutil,os
SEC=2048
def find_record(f, path_parts):
    f.seek(16*SEC); pvd=f.read(SEC)
    root=pvd[156:156+34]; lba=struct.unpack('<I',root[2:6])[0]; ln=struct.unpack('<I',root[10:14])[0]
    for i,part in enumerate(path_parts):
        f.seek(lba*SEC); data=f.read(ln); off=0; found=None
        while off<ln:
            rl=data[off]
            if rl==0: off=(off//SEC+1)*SEC; continue
            nlen=data[off+32]; name=data[off+33:off+33+nlen].decode('latin-1').split(';')[0]
            if name.upper()==part.upper(): found=(lba*SEC+off, data[off:off+rl]); break
            off+=rl
        assert found,part
        rec=found[1]; lba=struct.unpack('<I',rec[2:6])[0]; ln=struct.unpack('<I',rec[10:14])[0]
    return found[0],lba,ln
def set_size(f,recpos,size):
    f.seek(recpos+10); f.write(struct.pack('<I',size)+struct.pack('>I',size))
def build(src,dst,datadat=None,eboot=None):
    shutil.copyfile(src,dst)
    with open(dst,'r+b') as f:
        if eboot is not None:
            pos,lba,ln=find_record(f,['PSP_GAME','SYSDIR','EBOOT.BIN'])
            assert (len(eboot)+SEC-1)//SEC <= (ln+SEC-1)//SEC, 'EBOOT grew past its sectors'
            f.seek(lba*SEC); f.write(eboot+b'\0'*(((len(eboot)+SEC-1)//SEC)*SEC-len(eboot))); set_size(f,pos,len(eboot))
        if datadat is not None:
            pos,lba,ln=find_record(f,['PSP_GAME','USRDIR','DATA.DAT'])
            f.seek(0,2); end=f.tell()
            trail=end-(lba*SEC+((ln+SEC-1)//SEC)*SEC)
            assert 0<=trail<=64*SEC, 'DATA.DAT is not last'
            f.seek(lba*SEC); f.write(datadat); pad=(-len(datadat))%SEC; f.write(b'\0'*(pad+trail)); f.truncate()
            set_size(f,pos,len(datadat))
            tot=f.tell()//SEC
            f.seek(16*SEC+80); f.write(struct.pack('<I',tot)+struct.pack('>I',tot))
