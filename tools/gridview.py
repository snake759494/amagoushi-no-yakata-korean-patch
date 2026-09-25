import sys
from PIL import Image,ImageDraw
n,x0,y0,x1,y1,sc=sys.argv[1],*map(int,sys.argv[2:7])
im=Image.open('work/comp/%s.png'%n).convert('RGBA'); bg=Image.new('RGBA',im.size,(255,0,255,255)); bg.alpha_composite(im)
c=bg.crop((x0,y0,x1,y1)).resize(((x1-x0)*sc,(y1-y0)*sc),Image.NEAREST); d=ImageDraw.Draw(c)
for x in range(x0 - x0%10, x1, 10):
    X=(x-x0)*sc; d.line([(X,0),(X,c.height)],fill=(0,255,0,90) if x%50 else (255,255,0,160)); 
    if x%50==0: d.text((X+1,1),str(x),fill=(255,255,0))
for y in range(y0 - y0%10, y1, 10):
    Y=(y-y0)*sc; d.line([(0,Y),(c.width,Y)],fill=(0,255,0,90) if y%50 else (255,255,0,160))
    if y%50==0: d.text((1,Y+1),str(y),fill=(255,255,0))
c.save(sys.argv[7] if len(sys.argv)>7 else 'work/grid.png')
