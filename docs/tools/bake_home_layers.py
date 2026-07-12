# Bakes the home-screen depth layers from Art/Assets/Homescreen/{bg,zdepth}.png.
# Rerun whenever bg.png or zdepth.png change:  python docs/tools/bake_home_layers.py
# v2: the parallax plate is a HARD cutout (feathered masks ghost against the
# base); DoF layers stay continuous (blur blending is fine).
from PIL import Image, ImageFilter
HS='Art/Assets/Homescreen/'
bg=Image.open(HS+'bg.png').convert('RGB')
W=768;H=round(W*bg.height/bg.width)
bg=bg.resize((W,H))
d=Image.open(HS+'zdepth.png').convert('L').resize((W,H))
def bake(alpha_fn,blur,name):
    img=bg.filter(ImageFilter.GaussianBlur(blur)) if blur else bg.copy()
    img=img.convert('RGBA')
    img.putalpha(d.point(alpha_fn))
    img.save(HS+name)
    print(name,'baked')
# near plate: opaque from depth>=155, 15-step feather below, nothing else
bake(lambda v:255 if v>=155 else (max(0,(v-140))*17 if v>=140 else 0),0,'hs_layer_near.png')
bake(lambda v:v,2.5,'hs_layer_dofNear.png')
bake(lambda v:255-v,9,'hs_layer_dofFar.png')
