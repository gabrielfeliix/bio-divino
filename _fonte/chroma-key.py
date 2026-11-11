import sys, glob, numpy as np
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]
files = sorted(glob.glob(src+'/*.png'))
def key(a):
    a = a.astype(np.float32)
    r,g,b = a[...,0],a[...,1],a[...,2]
    d = g - np.maximum(r,b)            # dominância do verde
    alpha = 1 - np.clip((d-40)/(110-40),0,1)
    # despill: limita o verde ao maior entre r e b
    g2 = np.minimum(g, np.maximum(r,b)*1.02)
    out = np.dstack([r,g2,b,alpha*255]).clip(0,255).astype(np.uint8)
    return out
frames=[key(np.array(Image.open(f).convert('RGB'))) for f in files]
# caixa que contém o último quadro (e todos) com margem
al = np.max(np.stack([f[...,3] for f in frames]),axis=0)
ys,xs = np.where(al>20); m=8
y0,y1,x0,x1 = max(ys.min()-m,0),min(ys.max()+m,al.shape[0]),max(xs.min()-m,0),min(xs.max()+m,al.shape[1])
print('bbox',x0,y0,x1,y1)
for i,f in enumerate(frames):
    Image.fromarray(f[y0:y1,x0:x1]).save(f'{dst}/{i+1:04d}.png')
