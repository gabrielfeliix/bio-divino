# Cola só a boca retocada (máscara com borda suave) de volta em cada quadro original do vídeo.
import numpy as np
from PIL import Image, ImageFilter
B={41:(568,135),43:(568,140),45:(546,155),47:(514,160),49:(530,145)}
r=Image.open('boca/retocada-1200.png').convert('RGB')
m=Image.open('boca/mascara.png').convert('L').filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(4))
for k,(i,(x0,y0)) in enumerate(B.items()):
    ox,oy=(k%3)*400,(k//3)*400
    tile=r.crop((ox,oy,ox+400,oy+400)).resize((200,200),Image.LANCZOS)
    mt=m.crop((ox,oy,ox+400,oy+400)).resize((200,200),Image.LANCZOS)
    f=Image.open('fr/%04d.png'%i).convert('RGB')
    reg=f.crop((x0,y0,x0+200,y0+200))
    f.paste(Image.composite(tile,reg,mt),(x0,y0))
    f.save('fr/%04d.png'%i)
print('ok')
