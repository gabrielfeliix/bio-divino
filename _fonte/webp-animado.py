import glob, sys, os, numpy as np
from PIL import Image
src, out, w, step, q, thr = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
allf=sorted(glob.glob(src+'/*.png')); files=allf[::step]
if files[-1]!=allf[-1]: files.append(allf[-1])
final=None; fr=[]; prev=None
arrs=[]
for f in files:
    im=Image.open(f).convert('RGBA'); h=round(im.height*w/im.width)
    a=np.array(im.resize((w,h),Image.LANCZOS)).astype(np.int16)
    a[a[...,3]<16]=0
    arrs.append(a)
# degradê nas laterais enquanto a Divi e o Nô entram (some quando a pose fecha)
# largura em fração da imagem: larga na entrada, estreita no fim, sem tocar a pose final (a 22/768 da borda)
n=len(arrs); W=arrs[0].shape[1]
src_idx=[allf.index(f) for f in files]
for k,a in enumerate(arrs):
    i=src_idx[k]
    t=min(max((i-44)/(56-44),0),1)          # 0 até o quadro 44, 1 a partir do 56
    t=t*t*(3-2*t)
    width=(0.05*(1-t)+0.02*t)*W
    x=np.arange(W,dtype=np.float32)
    d=np.minimum(x, W-1-x)
    r=np.clip(d/width,0,1); r=r*r*(3-2*r)
    a[...,3]=(a[...,3]*r[None,:]).astype(np.int16)
# estabiliza pelo quadro final: do fim para trás, o que já está igual ao final vira exatamente o final
fin=arrs[-1].copy()
for i in range(len(arrs)-1,-1,-1):
    d=np.abs(arrs[i]-fin).max(-1)<thr
    arrs[i][d]=fin[d]
# e de frente para trás, o que não mudou repete o anterior
for i in range(1,len(arrs)):
    d=np.abs(arrs[i]-arrs[i-1]).max(-1)<thr
    arrs[i][d]=arrs[i-1][d]
fr=[Image.fromarray(a.clip(0,255).astype(np.uint8)) for a in arrs]
dur=[round(1000*step/24)]*len(fr)
fr[0].save(out,save_all=True,append_images=fr[1:],duration=dur,loop=1,quality=q,method=4,minimize_size=True,allow_mixed=True)
fr[-1].save(out.replace('.webp','-final.webp'),quality=90,method=6)
print(out,len(fr),os.path.getsize(out)//1024,'KB')
