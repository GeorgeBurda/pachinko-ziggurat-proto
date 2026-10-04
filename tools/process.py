# turns the raw generated images (sd-turbo, /workspace/sd/out) into compressed game assets
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageEnhance
SRC = '/workspace/sd/out/'; OUT = '../pages/assets/'
def ld(n): return Image.open(SRC + n).convert('RGB')
def sv(im, n, q=74): im.save(OUT + n + '.webp', 'WEBP', quality=q, method=6); print(n, im.size)
def mirror_tile(im):  # seamless by 2x2 mirroring
    w, h = im.size; t = Image.new('RGB', (w * 2, h * 2)); t.paste(im, (0, 0)); t.paste(im.transpose(Image.FLIP_LEFT_RIGHT), (w, 0)); t.paste(im.transpose(Image.FLIP_TOP_BOTTOM), (0, h)); t.paste(im.rotate(180), (w, h)); return t
# backdrops: upscale + light sharpening
for t, n in enumerate(['bg0_1', 'bg1_1', 'bg2_1', 'bg3_0']):
    im = ld(n + '.png').resize((720, 1080), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.2, 60, 2)); sv(im, 'bg%d' % t, 70)
# lapis field bricks: darker, a bit desaturated so pegs/balls read on top
b = ld('bricks_2.png'); b = ImageEnhance.Color(b).enhance(0.85); b = ImageEnhance.Brightness(b).enhance(0.8)
sv(mirror_tile(b).resize((512, 512), Image.LANCZOS), 'bricks', 72)
# friezes: deepen the blue bricks of the dragon panel; gold separators at the panel edges
def deepen(im):
    a = np.asarray(im).astype(np.float32); r, g, bb = a[..., 0], a[..., 1], a[..., 2]; m = (bb > r + 25)[..., None]
    a = np.where(m, a * np.array([0.42, 0.55, 0.9]), a); return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
def edge(im):
    d = ImageDraw.Draw(im); w, h = im.size
    for x0 in (0, w - 6): d.rectangle([x0, 0, x0 + 5, h], fill=(120, 80, 20)); d.rectangle([x0 + 1, 0, x0 + 3, h], fill=(240, 200, 100))
    return im
sv(edge(ld('lion_0.png').resize((400, 200), Image.LANCZOS)), 'frieze_lion', 76)
sv(edge(deepen(ld('dragon_0.png')).resize((400, 200), Image.LANCZOS)), 'frieze_dragon', 76)
# gold texture tile
sv(mirror_tile(ld('goldtex_0.png')).resize((256, 256), Image.LANCZOS), 'gold', 74)
# carved sandstone (vertical seamless)
p = ld('pillar_0.png'); pp = Image.new('RGB', (p.width, p.height * 2)); pp.paste(p, (0, 0)); pp.paste(p.transpose(Image.FLIP_TOP_BOTTOM), (0, p.height)); sv(pp.resize((160, 640), Image.LANCZOS), 'pillar', 72)
# rosette medallion: circular cut-out with soft edge
r = ld('rosette_0.png'); n = r.width; y, x = np.mgrid[0:n, 0:n]; c = n / 2; rad = n * 0.455
d = np.sqrt((x - c) ** 2 + (y - c) ** 2); al = np.clip((rad - d) / 2.5, 0, 1)
ra = np.dstack([np.asarray(r), (al * 255).astype(np.uint8)]); sv(Image.fromarray(ra, 'RGBA').crop((int(c - rad), int(c - rad), int(c + rad), int(c + rad))).resize((192, 192), Image.LANCZOS), 'rosette', 80)
# gate portal (centre of the generated arch)
po = ld('portal_2.png'); sv(po.crop((96, 150, 416, 768)).resize((200, 386), Image.LANCZOS), 'portal', 76)
# jackpot plaques: crop the frame, paint a dark lapis cartouche in the centre for the text, rounded corners, recolour per tier
pq = ld('plaque_1.png'); a = np.asarray(pq).astype(np.float32)
sat = a.max(2) - a.min(2); rows = np.where((sat > 60).mean(1) > 0.3)[0]; cols = np.where((sat > 60).mean(0) > 0.3)[0]
y0, y1, x0, x1 = rows.min(), rows.max(), cols.min(), cols.max(); pq = pq.crop((x0, y0, x1, y1)); print('plaque crop', x0, y0, x1, y1)
w, h = pq.size; base = np.asarray(pq).astype(np.float32)
def variant(hue_from_blue):
    a = base.copy(); r, g, bb = a[..., 0], a[..., 1], a[..., 2]; blue = (bb > r + 20) & (bb > g)
    if hue_from_blue is not None: tgt = np.array(hue_from_blue, np.float32); lum = a.mean(2, keepdims=True); a = np.where(blue[..., None], lum / 110 * tgt, a)
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA'); d = ImageDraw.Draw(im)
    # inner cartouche for the text
    iw, ih = int(w * 0.66), int(h * 0.56); ix, iy = (w - iw) // 2, (h - ih) // 2
    cart = Image.new('RGBA', (iw, ih)); cd = ImageDraw.Draw(cart)
    col = (np.array(hue_from_blue if hue_from_blue is not None else (40, 80, 200)) * 0.35).astype(int)
    for yy in range(ih): k = 1 - abs(yy / ih - 0.45) * 0.9; cd.line([(0, yy), (iw, yy)], fill=tuple(int(v * k) for v in col) + (255,))
    m = Image.new('L', (iw, ih), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, iw - 1, ih - 1], radius=ih // 3, fill=255)
    im.paste(cart, (ix, iy), m); d.rounded_rectangle([ix, iy, ix + iw - 1, iy + ih - 1], radius=ih // 3, outline=(80, 50, 10, 255), width=4); d.rounded_rectangle([ix + 2, iy + 2, ix + iw - 3, iy + ih - 3], radius=ih // 3, outline=(245, 205, 110, 255), width=2)
    mk = Image.new('L', (w, h), 0); ImageDraw.Draw(mk).rounded_rectangle([0, 0, w - 1, h - 1], radius=int(h * 0.12), fill=255); im.putalpha(mk)
    return im.resize((480, int(480 * h / w)), Image.LANCZOS)
for t, hue in enumerate([(40, 200, 170), (50, 100, 240), (230, 40, 50), (170, 70, 230)]): sv(variant(hue), 'plaque%d' % t, 80)
# hanging vines with flowers: luminance key from the black background
v = ld('vines_0.png'); a = np.asarray(v).astype(np.float32); lum = a.max(2); al = np.clip((lum - 28) / 45, 0, 1)
va = np.dstack([a, al * 255]).astype(np.uint8); sv(Image.fromarray(va, 'RGBA').resize((512, 341), Image.LANCZOS), 'vines', 78)
