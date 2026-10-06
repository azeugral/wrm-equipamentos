"""Gera as imagens otimizadas e o assets/js/catalogo.js a partir de ../_ref/assets.
Uso: python tools/processar.py

As listas PECAS, EQUIPAMENTOS e USINAGEM abaixo são a fonte do catálogo:
nome, categoria e modelos de britador vieram do site antigo e foram classificados pela LRGZ
(CONFIRMAR com a WRM)."""
import json, pathlib, re, unicodedata
from PIL import Image, ImageDraw, ImageFont

RAIZ = pathlib.Path(__file__).resolve().parents[1]
REF = RAIZ.parent / "_ref"
SAI = RAIZ / "assets" / "img"
FONTES = REF / "fontes"

GRAFITE = (31, 30, 31)
AZUL = (62, 64, 149)

# arquivo em _ref/assets/pecas (prefixo numérico), nome, categoria, modelos
PECAS = [
    ("01", "Polia", "Transmissão", []),
    ("02", "Coroa e pinhão", "Transmissão", []),
    ("03", "Tambor de elevador de caneca", "Elevadores de caneca", []),
    ("04", "Eixo excêntrico", "Eixos", ["Mandíbula"]),
    ("05", "Eixo de alimentador", "Eixos", []),
    ("06", "Caneca de elevador", "Elevadores de caneca", []),
    ("07", "Suporte", "Estrutura e proteção", []),
    ("08", "Eixo cônico", "Eixos", ["Girosférico"]),
    ("09", "Pinhão", "Transmissão", []),
    ("10", "Roda dentada e pinhão", "Transmissão", []),
    ("11", "Anel de trava", "Fixação", []),
    ("12", "Baquelites, feltros e filtros", "Lubrificação e controle", []),
    ("13", "Bombas de lubrificação", "Lubrificação e controle", []),
    ("14", "Contraporca", "Fixação", []),
    ("15", "Cunha de fixação", "Fixação", []),
    ("16", "Cunha", "Fixação", []),
    ("17", "Painel de alarme", "Lubrificação e controle", []),
    ("18", "Ponta de bronze e chaveta de trava", "Buchas e anéis", []),
    ("19", "Porca de fixação", "Fixação", []),
    ("20", "Porca de trava", "Fixação", []),
    ("21", "Prisioneiros", "Fixação", []),
    ("22", "Rolamento 10E18", "Rolamentos", ["Girosférico"]),
    ("23", "Rolamento 11D63", "Rolamentos", ["Girosférico"]),
    ("24", "Suporte da cunha", "Estrutura e proteção", []),
    ("25", "Tampa do robô", "Estrutura e proteção", []),
    ("26", "Anel rotativo BG-36", "Buchas e anéis", ["BG-36"]),
    ("27", "Anel rotativo BG-48", "Buchas e anéis", ["BG-48"]),
    ("28", "Buchas cônicas", "Buchas e anéis", ["Girosférico"]),
    ("29", "Buchas do BG-36", "Buchas e anéis", ["BG-36"]),
    ("30", "Buchas do BG-48", "Buchas e anéis", ["BG-48"]),
    ("31", "Buchas paralelas", "Buchas e anéis", ["Girosférico"]),
    ("32", "Cunhas de fixação", "Fixação", []),
    ("33", "Eixo cônico BG-36FC", "Eixos", ["BG-36"]),
    ("34", "Eixo excêntrico do BG-36", "Eixos", ["BG-36"]),
    ("35", "Eixo excêntrico do BG-48", "Eixos", ["BG-48"]),
    ("36", "Luva tensora", "Fixação", []),
    ("37", "Manômetro de glicerina", "Lubrificação e controle", []),
    ("38", "Molas 95G88B, 95G89B e 95G90B", "Molas", ["Girosférico"]),
    ("39", "Molas", "Molas", ["Girosférico"]),
    ("40", "Parafusos de britadores de mandíbula", "Fixação", ["Mandíbula"]),
    ("41", "Parafusos de britadores girosféricos", "Fixação", ["Girosférico"]),
    ("42", "Parafusos de fixação das cunhas", "Fixação", []),
    ("43", "Pinhão BG-36", "Transmissão", ["BG-36"]),
    ("44", "Pinhão BG-48", "Transmissão", ["BG-48"]),
    ("45", "Porca da manta BG-36FC", "Fixação", ["BG-36"]),
    ("46", "Porca e arruela de fixação BG-48", "Fixação", ["BG-48"]),
    ("47", "Porca e arruela de fixação BG-36", "Fixação", ["BG-36"]),
    ("48", "Porca e contraporca BG-44", "Fixação", ["BG-44"]),
    ("49", "Porca H4000", "Fixação", []),
    ("50", "Protetor dos braços", "Estrutura e proteção", ["Girosférico"]),
    ("51", "Queixo 25x40", "Estrutura e proteção", ["Mandíbula", "25x40"]),
    ("52", "Radiador", "Lubrificação e controle", []),
    ("53", "Rodas de misturadores", "Transmissão", []),
    ("54", "Rolamento 10S47", "Rolamentos", ["Girosférico"]),
    ("55", "Suporte do BG-36", "Estrutura e proteção", ["BG-36"]),  # no site antigo: "BG-367" (CONFIRMAR)
    ("56", "Conjunto cabeça esférica e eixo principal", "Eixos", ["Girosférico"]),
    ("57", "Válvulas de alívio", "Lubrificação e controle", []),
    # 58 "Modelo" ficou de fora: nome não identifica a peça (CONFIRMAR)
]

EQUIPAMENTOS = [
    ("01", "Britador de mandíbula 30x42", "Mandíbula"),
    ("02", "Britador de mandíbula 30x55", "Mandíbula"),
    ("03", "Britador de mandíbula 20x36", "Mandíbula"),
    ("04", "Britador girosférico BG-48", "Girosférico"),
    ("05", "Britador de mandíbula 30x42", "Mandíbula"),
    ("06", "Britador girosférico BG-36", "Girosférico"),
    ("07", "Britador girosférico BBG-489-S", "Girosférico"),
    ("08", "Britador de mandíbula 25x40", "Mandíbula"),
]

# peças usinadas (PNG recortado). O site antigo não dava nome: descrições pela foto (CONFIRMAR)
USINAGEM = [
    ("01", "Corpo roscado em bronze"),
    ("02", "Hastes com revestimento e rosca"),
    ("03", "Barra furada"),
    ("04", "Base usinada"),
    ("05", "Blocos com alça"),
    ("06", "Camisas em aço"),
    ("07", "Fusos em base"),
    ("08", "Suporte em chapa"),
    ("09", "Conjunto de fixação"),
    ("10", "Parafusos de cabeça sextavada"),
    ("11", "Carcaça recuperada"),
    ("12", "Bucha e flange"),
    ("13", "Eixos escalonados"),
    ("14", "Luva com anéis"),
    ("15", "Tubo flangeado"),
    ("16", "Bloco usinado"),
]

def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")

def achar(pasta, prefixo):
    return next((REF / "assets" / pasta).glob(prefixo + "-*"))

def webp(im, destino, larg, q=82):
    im = im.copy()
    if im.width > larg:
        im = im.resize((larg, round(im.height * larg / im.width)), Image.LANCZOS)
    destino.parent.mkdir(parents=True, exist_ok=True)
    im.save(destino, "WEBP", quality=q, method=6)
    return im.size

def recortar_branco(im, margem=18):
    """Fotos de peça vêm 800x600 com muito branco: recorta no objeto e devolve 4:3 centrado."""
    cinza = im.convert("L").point(lambda p: 255 if p < 238 else 0)
    bb = cinza.getbbox()
    if not bb:
        return im
    x0, y0, x1, y1 = bb
    w, h = x1 - x0, y1 - y0
    W = max(w, h * 4 / 3) + margem * 2
    H = W * 3 / 4
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    caixa = Image.new("RGB", (round(W), round(H)), (255, 255, 255))
    caixa.paste(im, (round(W / 2 - cx), round(H / 2 - cy)))
    return caixa

def main():
    cat = {"pecas": [], "equipamentos": [], "usinagem": []}
    for num, nome, categoria, modelos in PECAS:
        im = recortar_branco(Image.open(achar("pecas", num)).convert("RGB"))
        s = slug(nome)
        tam = webp(im, SAI / "pecas" / f"{s}.webp", 900)
        webp(im, SAI / "pecas" / f"{s}-p.webp", 440, 78)
        cod = re.findall(r"\b(\d{2}[A-Z]\d{2}[A-Z]?|BG-\d+\w*|H\d{4}|\d{2}x\d{2})\b", nome)
        cat["pecas"].append({"id": s, "nome": nome, "cat": categoria, "modelos": modelos, "cod": cod, "w": tam[0], "h": tam[1]})
    for num, nome, tipo in EQUIPAMENTOS:
        im = Image.open(achar("equipamentos", num)).convert("RGB")
        s = f"{slug(nome)}-{num}"
        tam = webp(im, SAI / "equipamentos" / f"{s}.webp", 900)
        webp(im, SAI / "equipamentos" / f"{s}-p.webp", 520, 78)
        cat["equipamentos"].append({"id": s, "nome": nome, "tipo": tipo, "w": tam[0], "h": tam[1]})
    for num, nome in USINAGEM:
        im = Image.open(achar("usinagem", num)).convert("RGBA")
        im = im.crop(im.split()[3].getbbox())
        s = f"{num}-{slug(nome)}"
        tam = webp(im, SAI / "usinagem" / f"{s}.webp", 800, 84)
        webp(im, SAI / "usinagem" / f"{s}-p.webp", 420, 80)
        cat["usinagem"].append({"id": s, "nome": nome, "w": tam[0], "h": tam[1]})
    # carreta e britador com placa WRM (do banner "Mineração" do site antigo)
    webp(Image.open(achar("equipamentos", "09")).convert("RGB"), SAI / "transporte.webp", 1200)
    mine = Image.open(REF / "assets" / "marca" / "mineracao.png").convert("RGB").crop((4, 4, 425, 270))
    webp(mine, SAI / "britador-placa-wrm.webp", 421, 86)

    js = "/* gerado por tools/processar.py — não editar à mão */\nwindow.CATALOGO = " + json.dumps(cat, ensure_ascii=False, separators=(",", ":")) + ";\n"
    (RAIZ / "assets" / "js" / "catalogo.js").write_text(js, encoding="utf-8")
    print({k: len(v) for k, v in cat.items()})
    marca()

def fonte(nome, tam, peso):
    f = ImageFont.truetype(str(FONTES / nome), tam)
    f.set_variation_by_name(peso)
    return f

def marca():
    logo = Image.open(REF / "assets" / "marca" / "logo-wrm-sem-sombra.png").convert("RGBA")
    neg = Image.open(REF / "assets" / "marca" / "logo-wrm-negativo.png").convert("RGBA")
    # ícone: só a moldura com "WRM" (sem as barras), negativo sobre grafite + barra azul
    moldura = neg.crop((100, 0, neg.width, neg.height))
    for lado, nome in ((512, "icone-512.png"), (192, "favicon-192.png"), (180, "apple-touch-icon.png")):
        ic = Image.new("RGBA", (512, 512), GRAFITE + (255,))
        m = moldura.copy(); m.thumbnail((420, 420), Image.LANCZOS)
        ic.alpha_composite(m, ((512 - m.width) // 2, (512 - m.height) // 2 - 20))
        ImageDraw.Draw(ic).rectangle((46, 380, 466, 404), fill=AZUL)
        ic.convert("RGB").resize((lado, lado), Image.LANCZOS).save(SAI / nome)
    ic = Image.open(SAI / "icone-512.png")
    ic.save(RAIZ / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    ic.resize((32, 32), Image.LANCZOS).save(SAI / "favicon-32.png")

    # og.jpg 1200x630
    og = Image.new("RGB", (1200, 630), GRAFITE)
    d = ImageDraw.Draw(og)
    for x in range(0, 1200, 40):
        d.line((x, 0, x, 630), fill=(40, 39, 40))
    for y in range(0, 630, 40):
        d.line((0, y, 1200, y), fill=(40, 39, 40))
    peca = Image.open(next((REF / "assets" / "usinagem").glob("16-*"))).convert("RGBA")
    peca = peca.crop(peca.split()[3].getbbox()); peca.thumbnail((400, 400), Image.LANCZOS)
    og.paste(peca, (1200 - peca.width - 40, (630 - peca.height) // 2), peca)
    n = neg.copy(); n.thumbnail((300, 120), Image.LANCZOS)
    og.paste(n, (64, 64), n)
    t = fonte("Unbounded.ttf", 46, b"Bold")
    for i, linha in enumerate(["Peças e manutenção", "para britadores", "Barber Greene"]):
        d.text((64, 250 + i * 66), linha, font=t, fill=(244, 243, 240))
    d.text((66, 470), "USINAGEM SOB DESENHO · SANTA BÁRBARA D'OESTE/SP · DESDE 2000",
           font=fonte("JetBrainsMono.ttf", 17, b"Medium"), fill=(150, 154, 230))
    og.save(SAI / "og.jpg", quality=86)
    print("marca ok")

if __name__ == "__main__":
    main()
