# WRM Equipamentos

Site novo da **WRM Indústria e Comércio de Equipamentos Ltda** (Santa Bárbara d'Oeste/SP, desde 2000):
peças, reforma e manutenção de britadores Barber Greene de mandíbula e girosféricos, e usinagem sob desenho.
Substitui o site antigo em wrmequipamentos.com.br.

HTML, CSS e JS puros, sem build. Prévia em GitHub Pages com `noindex` e `robots.txt` bloqueando até apontar o domínio.

## Estrutura

- `index.html`, `pecas.html`, `404.html`: **gerados**. Editar o `<main>` em `tools/paginas/*.html` e rodar
  `python tools/montar_paginas.py` (cabeçalho, rodapé, JSON-LD e `?v=` vêm de lá).
  Marcadores `<!--PECAS:...-->`, `<!--USINAGEM-->`, `<!--EQUIPAMENTOS-->` viram HTML estático a partir do catálogo.
- `tools/processar.py`: lê `../_ref/assets`, gera as imagens WebP (`assets/img/pecas|equipamentos|usinagem`,
  `-p` = miniatura), `assets/js/catalogo.js`, favicon, ícones e `og.jpg`. **Nome, categoria e modelos de cada peça
  estão nas listas `PECAS`, `EQUIPAMENTOS` e `USINAGEM` desse script.** Depois de mudar, rodar ele e o montar_paginas.
- `tools/vetorizar_logo.py`: gera `assets/img/logo-wrm.svg` e `logo-wrm-negativo.svg` a partir do PNG antigo.
- `assets/js/main.js`: `CONFIG` (WhatsApp de vendas e e-mail), menu, entradas, lupa, formulário de cotação.
- `assets/js/pecas.js`: busca, filtros (categoria e modelo, com `?modelo=`, `?cat=`, `?q=` na URL) e lista de cotação
  salva no navegador, enviada pronta para o WhatsApp de vendas.

A cada deploy que mude CSS/JS, subir `V` em `tools/montar_paginas.py` e remontar.

## Identidade

Conceito "folha de desenho técnico": grade fina de prancha, carimbo (quadro de legenda), marcas de corte e legendas "Fig."
- Cores do logo: grafite `#373435` (fundo escuro `#1c1b1c`) e azul `#3e4095`. Papel `#eceae5`.
- Fontes do padrão LRGZ: Unbounded (títulos), IBM Plex Sans (texto), JetBrains Mono (rótulos e códigos de peça).
- Botões retos com sombra dura que desliza; curva `cubic-bezier(.16,.84,.32,1)`.

## CONFIRMAR com a WRM

Campos pendentes aparecem com contorno tracejado (`.a-confirmar`).

1. Texto institucional: história, parque de máquinas, clientes (Início › Empresa). O aviso tracejado foi removido a pedido; acrescentar o texto quando vier.
2. Telefone fixo (19) 3455-1818 ainda ativo? (o (19) 3454-5892 do site antigo ficou de fora). Horário já veio do Google (06/10): seg e sex 7h30–16h30, ter a qui 7h30–17h30.
3. Classificação das peças por categoria e modelo (feita pela LRGZ) e os nomes das 16 peças usinadas (descritas pela foto).
4. "Suporte do BG-367" do site antigo virou "Suporte do BG-36"; a foto "Modelo" ficou de fora (não diz o que é).
5. Os 8 britadores da seção Equipamentos estão à venda ou só passaram pela oficina? (hoje: "passaram pela WRM").
6. Legenda da foto da carreta.
7. Fotos novas: as atuais são 800×600 do site antigo. Fábrica, máquinas e equipe valorizariam muito o site.
8. Logo em vetor original (o SVG atual é traçado do PNG de 500 px).
9. E-mail com domínio próprio e troca do domínio (tirar `noindex`, liberar `robots.txt`, criar `CNAME` e sitemap).
