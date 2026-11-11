# Tira o fundo verde do vídeo do Magnific.
# Nas bordas, separa a cor do desenho da cor do verde (unmix) em vez de só cortar o verde,
# senão a mistura creme+verde vira pontinhos escuros. Pixel quase transparente recebe a cor
# do vizinho opaco mais próximo (nunca preto), para o redimensionamento não puxar escuro.
import sys, glob, numpy as np
from PIL import Image, ImageFilter
src, dst = sys.argv[1], sys.argv[2]
files = sorted(glob.glob(src+'/*.png'))
K = np.array([6,244,4], np.float32)          # cor do fundo
def key(img):
    a = np.asarray(img, np.float32)
    r,g,b = a[...,0],a[...,1],a[...,2]
    d = g - np.maximum(r,b)
    al = 1 - np.clip((d-30)/(150-30),0,1)
    al[al<0.06] = 0
    # unmix: C = al*F + (1-al)*K  ->  F = (C-(1-al)K)/al
    F = (a - (1-al)[...,None]*K) / np.maximum(al,0.25)[...,None]
    F = np.clip(F,0,255)
    # trava qualquer verde que sobrou
    F[...,1] = np.minimum(F[...,1], np.maximum(F[...,0],F[...,2])*1.02)
    # encolhe o alfa 1 px (some com a franja)
    A = Image.fromarray((al*255).astype(np.uint8)).filter(ImageFilter.MinFilter(3))
    A = np.asarray(A, np.float32)/255*0.5 + al*0.5
    # cor dos pixels de borda/transparentes = cor do opaco mais próximo (dilatação)
    solid = al > 0.9
    rgb = Image.fromarray(np.where(solid[...,None], F, 0).astype(np.uint8))
    mask = Image.fromarray((solid*255).astype(np.uint8))
    fill, m = rgb, mask
    for _ in range(6):
        fill = Image.composite(fill, fill.filter(ImageFilter.MaxFilter(3)), m)
        m = m.filter(ImageFilter.MaxFilter(3))
    fill = np.asarray(fill, np.float32)
    out = np.where(solid[...,None], F, np.where((al>0.5)[...,None], (F+fill)/2, fill))
    return np.dstack([out, A*255]).clip(0,255).astype(np.uint8)
for i,f in enumerate(files):
    Image.fromarray(key(Image.open(f).convert('RGB'))).save(f'{dst}/{i+1:04d}.png')
print(len(files),'quadros')
