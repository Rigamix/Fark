# Bakes home-screen depth assets from Art/Assets/Homescreen/{bg,zdepth}.png.
# Rerun whenever bg.png or zdepth.png change:  python docs/tools/bake_home_layers.py
# Outputs:
#  - hs_home_data.js: bg + blurred bg + depth as data-URIs for the WebGL
#    displacement parallax (script tag loads fine under file://)
#  - hs_layer_near/dofNear/dofFar.png: DOM-parallax fallback plates
from PIL import Image, ImageFilter
import base64, io, os

HS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Art', 'Assets', 'Homescreen') + os.sep
bg0 = Image.open(HS + 'bg.png').convert('RGB')
d0 = Image.open(HS + 'zdepth.png').convert('L')

def jpg_uri(img, q):
    b = io.BytesIO()
    img.save(b, 'JPEG', quality=q)
    return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()

# GL textures
tex = bg0.resize((1080, round(1080 * bg0.height / bg0.width)))
texblur = tex.filter(ImageFilter.GaussianBlur(14))
dep = d0.resize((540, round(540 * d0.height / d0.width))).filter(ImageFilter.GaussianBlur(3)).convert('RGB')
js = 'window._HS_TEX="' + jpg_uri(tex, 82) + '";\n'
js += 'window._HS_TEXBLUR="' + jpg_uri(texblur, 75) + '";\n'
js += 'window._HS_DEPTH="' + jpg_uri(dep, 80) + '";\n'
open(HS + 'hs_home_data.js', 'w').write(js)
print('hs_home_data.js', round(len(js) / 1e6, 2), 'MB')

# DOM fallback plates
W = 768
H = round(W * bg0.height / bg0.width)
bg = bg0.resize((W, H))
d = d0.resize((W, H))

def bake(alpha_fn, blur, name):
    img = bg.filter(ImageFilter.GaussianBlur(blur)) if blur else bg.copy()
    img = img.convert('RGBA')
    img.putalpha(d.point(alpha_fn))
    img.save(HS + name)
    print(name, 'baked')

bake(lambda v: 255 if v >= 213 else (max(0, (v - 205)) * 32 if v >= 205 else 0), 0, 'hs_layer_near.png')
bake(lambda v: v, 2.5, 'hs_layer_dofNear.png')
bake(lambda v: 255 - v, 9, 'hs_layer_dofFar.png')
