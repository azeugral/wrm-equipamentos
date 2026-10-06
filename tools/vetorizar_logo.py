"""Vetoriza o logo raster do site antigo (500 px) em SVG, separando grafite e azul.
Uso: python tools/vetorizar_logo.py  ->  assets/img/logo-wrm.svg e logo-wrm-negativo.svg"""
import pathlib
import numpy as np
import potrace
from PIL import Image, ImageFilter

RAIZ = pathlib.Path(__file__).resolve().parents[1]
SRC = RAIZ.parent / "_ref" / "assets" / "marca" / "logo-wrm-sem-sombra.png"
ESC = 6  # amplia antes de traçar para suavizar as bordas

im = Image.open(SRC).convert("RGBA")
w, h = im.size
big = im.resize((w * ESC, h * ESC), Image.LANCZOS)
a = np.asarray(big).astype(int)
r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
opaco = al > 128
azul = opaco & (b - r > 40)
grafite = opaco & ~azul

def tracar(mask):
    m = Image.fromarray((mask * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(ESC * .6))
    bm = potrace.Bitmap(np.asarray(m) <= 127)
    plist = bm.trace(turdsize=40, alphamax=0.9, opticurve=True, opttolerance=0.2)
    d = []
    for curve in plist:
        s = curve.start_point
        d.append(f"M{s.x/ESC:.2f} {s.y/ESC:.2f}")
        for seg in curve.segments:
            if seg.is_corner:
                d.append(f"L{seg.c.x/ESC:.2f} {seg.c.y/ESC:.2f}L{seg.end_point.x/ESC:.2f} {seg.end_point.y/ESC:.2f}")
            else:
                d.append(f"C{seg.c1.x/ESC:.2f} {seg.c1.y/ESC:.2f} {seg.c2.x/ESC:.2f} {seg.c2.y/ESC:.2f} {seg.end_point.x/ESC:.2f} {seg.end_point.y/ESC:.2f}")
        d.append("Z")
    return "".join(d)

dg, da = tracar(grafite), tracar(azul)
for nome, cor in (("logo-wrm.svg", "#373435"), ("logo-wrm-negativo.svg", "#f4f3f0")):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="WRM">'
           f'<path fill="{cor}" fill-rule="evenodd" d="{dg}"/>'
           f'<path fill="#3e4095" fill-rule="evenodd" d="{da}"/></svg>')
    if "negativo" in nome:
        svg = svg.replace("#3e4095", "#7c80e0")
    (RAIZ / "assets" / "img" / nome).write_text(svg, encoding="utf-8")
    print(nome, len(svg), "bytes", w, h)
