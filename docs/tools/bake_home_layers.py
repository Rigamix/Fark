# Bakes the home-screen depth layers from Art/Assets/Homescreen/{bg,zdepth}.png.
# Rerun whenever bg.png or zdepth.png change:  python docs/tools/bake_home_layers.py
from PIL import Image, ImageFilter
import os
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
bake(lambda v:max(0,min(255,(v-150)*4)),0,'hs_layer_near.png')
bake(lambda v:max(0,min(255,255-abs(v-105)*4)) if v>35 else 0,0,'hs_layer_mid.png')
bake(lambda v:v,2.5,'hs_layer_dofNear.png')
bake(lambda v:255-v,9,'hs_layer_dofFar.png')
