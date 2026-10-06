"""Monta as páginas da raiz a partir de tools/paginas/*.html (só o <main>) + cabeçalho e rodapé comuns.
Cada arquivo começa com 3 linhas:  título | descrição | item do menu ativo (ou -)
Marcadores trocados aqui, a partir de assets/js/catalogo.js (gerado por tools/processar.py):
  <!--PECAS:todas-->   cards de todas as peças
  <!--PECAS:id,id-->   cards só dessas peças
  <!--USINAGEM-->  <!--EQUIPAMENTOS-->  <!--TOTAL_PECAS-->
Uso: python tools/montar_paginas.py"""
import html, json, pathlib, re

RAIZ = pathlib.Path(__file__).resolve().parents[1]
V = 3  # subir a cada deploy que mude CSS/JS
ATUAL = ' aria-current="page"'
MENU = [("pecas.html", "Peças"), ("index.html#usinagem", "Usinagem"), ("index.html#equipamentos", "Equipamentos"),
        ("index.html#empresa", "Empresa"), ("index.html#contato", "Contato")]

WA_VENDAS = "5519998360495"

CABECA = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>document.documentElement.classList.add("js")</script>
<title>{titulo}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#1f1e1f">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="WRM Equipamentos">
<meta property="og:title" content="{titulo}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="assets/img/og.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="favicon.ico" sizes="48x48">
<link rel="icon" href="assets/img/favicon-192.png" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&family=JetBrains+Mono:wght@500;600&family=Unbounded:wght@500;600;700&display=swap">
<link rel="stylesheet" href="assets/css/estilo.css?v={v}">
{extra}</head>
<body class="{classe}">
<a class="pular" href="#conteudo">Pular para o conteúdo</a>
<header class="topo" data-topo>
  <div class="wrap topo__in">
    <a class="marca" href="index.html" aria-label="WRM Equipamentos, início"><img src="assets/img/logo-wrm.svg" alt="WRM" width="484" height="156"></a>
    <nav class="nav" id="nav" aria-label="Principal">
      <ul class="menu">{menu}</ul>
      <a class="btn btn--azul btn--p nav__cta" href="https://wa.me/{wa}?text={wa_txt}" target="_blank" rel="noopener" data-wa>Pedir cotação</a>
    </nav>
    <button class="hamburguer" type="button" aria-expanded="false" aria-controls="nav" data-menu><span></span><span></span><span class="sr">Menu</span></button>
  </div>
</header>
<main id="conteudo">
"""

RODAPE = """</main>
<footer class="rodape">
  <div class="wrap">
    <div class="rodape__in">
      <div class="rodape__marca">
        <img src="assets/img/logo-wrm-negativo.svg" alt="WRM" width="484" height="156" loading="lazy">
        <p>Peças, reforma e manutenção de britadores de mandíbula e girosféricos. Usinagem sob desenho para a indústria.</p>
      </div>
      <div>
        <h2 class="rodape__tit">Site</h2>
        <ul>{paginas}</ul>
      </div>
      <div>
        <h2 class="rodape__tit">Contato</h2>
        <ul>
          <li><a href="https://wa.me/5519998360495" target="_blank" rel="noopener">Vendas · (19) 99836-0495</a></li>
          <li><a href="https://wa.me/5519996321129" target="_blank" rel="noopener">Administrativo · (19) 99632-1129</a></li>
          <li><a href="mailto:wrm.usinagem@gmail.com">wrm.usinagem@gmail.com</a></li>
        </ul>
      </div>
      <div>
        <h2 class="rodape__tit">Endereço</h2>
        <address>Rua Rafael Cervone, 151<br>Distrito Industrial I<br>Santa Bárbara d'Oeste/SP<br>CEP 13456-112</address>
        <p class="rodape__hora">Seg e sex · 7h30 às 16h30<br>Ter a qui · 7h30 às 17h30</p>
      </div>
    </div>
    <div class="rodape__fim">
      <span>© <span data-ano>2026</span> WRM Indústria e Comércio de Equipamentos Ltda · CNPJ 03.934.396/0001-32</span>
      <span>Site por <a href="https://lrgz.com.br" target="_blank" rel="noopener">L R G Z</a></span>
    </div>
  </div>
</footer>
<div class="lupa" data-lupa hidden>
  <div class="lupa__fundo" data-fechar></div>
  <figure class="lupa__caixa" role="dialog" aria-modal="true" aria-label="Imagem ampliada">
    <img alt="" data-lupa-img>
    <figcaption data-lupa-leg></figcaption>
    <button class="lupa__fechar" type="button" data-fechar aria-label="Fechar">×</button>
  </figure>
</div>
{scripts}<script src="assets/js/main.js?v={v}" defer></script>
</body>
</html>
"""

def ler_catalogo():
    txt = (RAIZ / "assets" / "js" / "catalogo.js").read_text(encoding="utf-8")
    return json.loads(re.search(r"window\.CATALOGO = (.*);\s*$", txt, re.S).group(1))

def e(s):
    return html.escape(s, quote=True)

def card_peca(p):
    cods = "".join(f'<span class="peca__cod">{e(c)}</span>' for c in p["cod"])
    mods = " ".join(p["modelos"])
    return f"""<article class="peca" data-peca="{e(p['id'])}" data-cat="{e(p['cat'])}" data-mod="{e(mods)}">
  <button class="peca__foto" type="button" data-amplia="assets/img/pecas/{p['id']}.webp" data-leg="{e(p['nome'])}" aria-label="Ampliar foto: {e(p['nome'])}">
    <img src="assets/img/pecas/{p['id']}-p.webp" alt="{e(p['nome'])}" width="440" height="330" loading="lazy" decoding="async">
  </button>
  <div class="peca__info">
    <p class="peca__cat">{e(p['cat'])}</p>
    <h3 class="peca__nome">{e(p['nome'])}</h3>
    <p class="peca__mods">{cods}{''.join(f'<span>{e(m)}</span>' for m in p['modelos'] if m not in p['cod'])}</p>
  </div>
  <button class="peca__add" type="button" data-add="{e(p['id'])}"><span class="peca__add-mais" aria-hidden="true">+</span><span data-add-txt>Adicionar à cotação</span></button>
</article>"""

def bloco_usinagem(cat):
    out = []
    for i, u in enumerate(cat["usinagem"], 1):
        out.append(f"""<li class="usi">
  <button type="button" class="usi__foto" data-amplia="assets/img/usinagem/{u['id']}.webp" data-leg="{e(u['nome'])}" data-escuro aria-label="Ampliar: {e(u['nome'])}">
    <img src="assets/img/usinagem/{u['id']}-p.webp" alt="{e(u['nome'])}" loading="lazy" decoding="async" width="420" height="{round(420 * u['h'] / u['w'])}">
  </button>
  <p class="usi__leg"><span>Fig. {i:02d}</span>{e(u['nome'])}</p>
</li>""")
    return "\n".join(out)

def bloco_equip(cat):
    out = []
    for q in cat["equipamentos"]:
        out.append(f"""<li class="equip">
  <button type="button" class="equip__foto" data-amplia="assets/img/equipamentos/{q['id']}.webp" data-leg="{e(q['nome'])}" aria-label="Ampliar: {e(q['nome'])}">
    <img src="assets/img/equipamentos/{q['id']}-p.webp" alt="{e(q['nome'])}" loading="lazy" decoding="async" width="520" height="390">
  </button>
  <p class="equip__tipo">{e(q['tipo'])}</p>
  <h3 class="equip__nome">{e(q['nome'])}</h3>
</li>""")
    return "\n".join(out)

def main():
    cat = ler_catalogo()
    por_id = {p["id"]: p for p in cat["pecas"]}
    for f in sorted((RAIZ / "tools" / "paginas").glob("*.html")):
        linhas = f.read_text(encoding="utf-8").split("\n")
        titulo, desc, ativo = (l.strip() for l in linhas[:3])
        corpo = "\n".join(linhas[3:])

        def pecas(m):
            ids = m.group(1)
            lista = cat["pecas"] if ids == "todas" else [por_id[i] for i in ids.split(",")]
            return "\n".join(card_peca(p) for p in lista)
        corpo = re.sub(r"<!--PECAS:([^>]+?)-->", pecas, corpo)
        corpo = corpo.replace("<!--USINAGEM-->", bloco_usinagem(cat)).replace("<!--EQUIPAMENTOS-->", bloco_equip(cat))
        corpo = corpo.replace("<!--TOTAL_PECAS-->", str(len(cat["pecas"])))

        menu = "".join(f'<li><a href="{h}"{ATUAL if h == ativo else ""}>{n}</a></li>' for h, n in MENU)
        paginas = "".join(f'<li><a href="{h}">{n}</a></li>' for h, n in [("index.html", "Início")] + MENU)
        scripts = ""
        extra = ""
        if "data-catalogo" in corpo:
            scripts = f'<script src="assets/js/catalogo.js?v={V}" defer></script>\n<script src="assets/js/pecas.js?v={V}" defer></script>\n'
        if f.name == "index.html":
            extra = '<script type="application/ld+json">' + json.dumps({
                "@context": "https://schema.org", "@type": "LocalBusiness",
                "name": "WRM Indústria e Comércio de Equipamentos Ltda", "alternateName": "WRM Equipamentos",
                "description": desc, "url": "https://www.wrmequipamentos.com.br/", "image": "assets/img/og.jpg",
                "telephone": "+55-19-99836-0495", "email": "wrm.usinagem@gmail.com", "foundingDate": "2000-07-03",
                "taxID": "03.934.396/0001-32",
                "openingHoursSpecification": [
                    {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Friday"], "opens": "07:30", "closes": "16:30"},
                    {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Tuesday", "Wednesday", "Thursday"], "opens": "07:30", "closes": "17:30"},
                ],
                "address": {"@type": "PostalAddress", "streetAddress": "Rua Rafael Cervone, 151 - Distrito Industrial I",
                            "addressLocality": "Santa Bárbara d'Oeste", "addressRegion": "SP", "postalCode": "13456-112", "addressCountry": "BR"},
            }, ensure_ascii=False) + "</script>\n"
        classe = "pg-" + f.stem
        wa_txt = "Ol%C3%A1%2C%20WRM!%20Gostaria%20de%20uma%20cota%C3%A7%C3%A3o."
        html_ = CABECA.format(titulo=titulo, desc=desc, menu=menu, v=V, extra=extra, classe=classe, wa=WA_VENDAS, wa_txt=wa_txt)
        html_ += corpo.rstrip() + "\n" + RODAPE.format(paginas=paginas, scripts=scripts, v=V)
        (RAIZ / f.name).write_text(html_, encoding="utf-8")
        print("ok", f.name)

if __name__ == "__main__":
    main()
