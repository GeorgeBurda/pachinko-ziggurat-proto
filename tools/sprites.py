# procedural premium sprites: chrome/lapis/gold balls, gold peg stud, gold coin (rendered with numpy shading)
import numpy as np
from PIL import Image
OUT = '../pages/assets/'
def sphere(n, base, env_top, env_bot, spec=1.0, rim=(1, 1, 1), gem=False, sss=None):
    y, x = np.mgrid[0:n, 0:n].astype(np.float32); c = (n - 1) / 2; r = n / 2 - 1
    dx, dy = (x - c) / r, (y - c) / r; d2 = dx * dx + dy * dy; inside = d2 <= 1
    nz = np.sqrt(np.clip(1 - d2, 0, 1)); nx, ny = dx, dy
    L = np.array([-0.45, -0.6, 0.66]); L /= np.linalg.norm(L)
    diff = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    # reflection vector for environment (sky above, ground below)
    ry = 2 * nz * ny  # rough
    t = np.clip((ry + 1) / 2, 0, 1)[..., None]
    env = np.array(env_top) * (1 - t) + np.array(env_bot) * t
    H = np.array([-0.3, -0.5, 1.0]); H /= np.linalg.norm(H)
    sp = np.clip(nx * H[0] + ny * H[1] + nz * H[2], 0, 1) ** 60 * spec
    sp2 = np.clip(nx * 0.5 + ny * 0.6 + nz * 0.62, 0, 1) ** 12 * 0.25 * spec
    fres = (1 - nz) ** 2.5
    col = np.array(base) * (0.25 + 0.75 * diff[..., None])
    col = col * 0.55 + env * 0.45 if not gem else col * 0.8 + env * 0.2
    if sss is not None: col += np.array(sss) * (np.clip(-(nx * L[0] + ny * L[1]) , 0, 1) ** 2)[..., None] * 0.5
    col += np.array(rim) * fres[..., None] * 0.35
    col += (sp + sp2)[..., None] * 1.0
    col = np.clip(col, 0, 1)
    a = np.clip((1 - np.sqrt(d2)) * r * 1.2, 0, 1)
    img = np.dstack([col * 255, a * 255]).astype(np.uint8)
    return Image.fromarray(img, 'RGBA')
def save(im, name, q=92): im.save(OUT + name, 'WEBP', quality=q, method=6)
save(sphere(64, (0.78, 0.8, 0.86), (1.0, 0.98, 0.95), (0.25, 0.28, 0.4)), 'ball_silver.webp')
save(sphere(64, (0.1, 0.25, 0.85), (0.55, 0.7, 1.0), (0.02, 0.05, 0.25), gem=True, sss=(0.2, 0.5, 1.0), rim=(0.5, 0.7, 1)), 'ball_lapis.webp')
save(sphere(64, (1.0, 0.72, 0.22), (1.0, 0.93, 0.6), (0.45, 0.25, 0.05), rim=(1, 0.85, 0.5)), 'ball_gold.webp')
save(sphere(64, (0.85, 0.12, 0.18), (1.0, 0.6, 0.6), (0.25, 0.0, 0.05), gem=True, sss=(1, 0.3, 0.3), rim=(1, 0.6, 0.6)), 'ball_ruby.webp')
# peg: domed gold stud with a dark base ring
def stud(n):
    y, x = np.mgrid[0:n, 0:n].astype(np.float32); c = (n - 1) / 2; r = n / 2 - 1
    dx, dy = (x - c) / r, (y - c) / r; d = np.sqrt(dx * dx + dy * dy)
    dome = d < 0.78; nz = np.sqrt(np.clip(1 - (d / 0.78) ** 2, 0, 1))
    nx, ny = dx / 0.78, dy / 0.78
    diff = np.clip(-0.45 * nx - 0.6 * ny + 0.66 * nz, 0, 1)
    sp = np.clip(-0.3 * nx - 0.5 * ny + 1.0 * nz, 0, 1) ** 40
    gold = np.array([1.0, 0.76, 0.3]); col = gold * (0.3 + 0.8 * diff[..., None]) + sp[..., None] * 1.2
    ring = (d >= 0.78) & (d < 1.0); col[ring] = np.array([0.35, 0.22, 0.05]) * (1 - (d[ring] - 0.78) * 2)[..., None]
    a = np.clip((1 - d) * r * 1.5, 0, 1) * np.where(d < 1, 1, 0) + 0
    a = np.where(d < 0.78, 1, np.clip((1 - d) / 0.22, 0, 1) * 0.75)
    return Image.fromarray(np.dstack([np.clip(col, 0, 1) * 255, a * 255]).astype(np.uint8), 'RGBA')
save(stud(32), 'peg.webp')
# coin face: gold disc with raised rim and an 8-point star (Shamash) emblem
def coin(n):
    y, x = np.mgrid[0:n, 0:n].astype(np.float32); c = (n - 1) / 2; r = n / 2 - 1
    dx, dy = (x - c) / r, (y - c) / r; d = np.sqrt(dx * dx + dy * dy); ang = np.arctan2(dy, dx)
    h = np.where(d > 0.82, 1 - (d - 0.82) * 3, 0.55)
    star = (d < 0.55 * (0.55 + 0.45 * np.abs(np.cos(ang * 4)) ** 3)); h = np.where(star, 0.85, h)
    gy, gx = np.gradient(h); shade = np.clip(0.75 - (gx * -0.45 + gy * -0.6) * 18, 0.2, 1.4)
    col = np.array([1.0, 0.78, 0.28]) * shade[..., None]
    sp = np.clip(1 - np.abs(dx + dy + 0.4) * 2.5, 0, 1) ** 3 * 0.35; col += sp[..., None]
    a = np.clip((1 - d) * r * 1.2, 0, 1)
    return Image.fromarray(np.dstack([np.clip(col, 0, 1) * 255, a * 255]).astype(np.uint8), 'RGBA')
save(coin(64), 'coin.webp')
print('ok')
