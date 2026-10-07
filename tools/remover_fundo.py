"""Tira o fundo das fotos de peças e equipamentos (já geradas em assets/img) com rembg.

Uso: pip install rembg && python tools/remover_fundo.py [arquivo.jpg destino.webp]
Sem argumentos, processa assets/img/pecas e assets/img/equipamentos no lugar. Mantém o tamanho do quadro
(catalogo.js não muda) e regera a miniatura -p a partir da foto recortada. Fotos que já têm transparência são puladas.
"""
import pathlib, sys
from PIL import Image
from rembg import remove, new_session

RAIZ = pathlib.Path(__file__).resolve().parent.parent
IMG = RAIZ / "assets" / "img"
SESSAO = new_session("isnet-general-use")

def recortar(im):
    return remove(im.convert("RGB"), session=SESSAO, post_process_mask=True)

def salvar(im, destino, larg, q):
    if im.width > larg:
        im = im.resize((larg, round(im.height * larg / im.width)), Image.LANCZOS)
    im.save(destino, "WEBP", quality=q, method=6, exact=False)

def pasta(nome):
    for foto in sorted((IMG / nome).glob("*.webp")):
        if foto.stem.endswith("-p"):
            continue
        mini = foto.with_name(foto.stem + "-p.webp")
        im = Image.open(foto)
        if im.mode == "RGBA" and im.getextrema()[3][0] < 255:
            continue
        rec = recortar(im)
        salvar(rec, foto, 900, 84)
        salvar(rec, mini, Image.open(mini).width, 80)
        print(foto.name)

if __name__ == "__main__":
    if len(sys.argv) == 3:
        rec = recortar(Image.open(sys.argv[1]))
        salvar(rec.crop(rec.split()[3].getbbox()), pathlib.Path(sys.argv[2]), 900, 84)
    else:
        pasta("pecas")
        pasta("equipamentos")
