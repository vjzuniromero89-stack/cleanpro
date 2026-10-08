import sys
from PIL import Image, ImageDraw
XS=[368,613,858,1103]; YS=[501,916,1331,1746]; S=209
rows=[l.rstrip('\n').split('\t') for l in open('raw/all_products.tsv')]
bypage={}
for r in rows: bypage.setdefault(int(r[0]),[]).append(r)
stats=[]
for p,items in sorted(bypage.items()):
    im=Image.open(f'raw/shots/p{p:02d}.png').convert('RGB')
    sheet=Image.new('RGB',(4*220,4*250),'white'); d=ImageDraw.Draw(sheet)
    for i,r in enumerate(items):
        x=XS[i%4]; y=YS[i//4]
        c=im.crop((x,y,x+S,y+S))
        pid=r[1].rsplit('_',1)[1]
        c.save(f'img/{pid}.jpg',quality=84,optimize=True)
        ext=c.getextrema(); flat=all(hi-lo<12 for lo,hi in ext)
        if flat: stats.append((p,i,pid))
        sheet.paste(c,((i%4)*220,(i//4)*250)); d.text(((i%4)*220+2,(i//4)*250+212),(r[3]+' '+r[6][:28]),fill='black')
    sheet.save(f'raw/sheet_{p:02d}.png')
print('flat crops:',stats)
