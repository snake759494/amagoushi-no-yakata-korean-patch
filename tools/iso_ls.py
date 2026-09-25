import pycdlib,sys
iso=pycdlib.PyCdlib(); iso.open(sys.argv[1])
for root,dirs,files in iso.walk(iso_path='/'):
    for f in files:
        p=root.rstrip('/')+'/'+f
        r=iso.get_record(iso_path=p)
        print(r.extent_location(), r.data_length, p)
