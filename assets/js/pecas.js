/* Catálogo: busca, filtros por categoria e modelo, e lista de cotação (salva no navegador) */
(() => {
  const raiz = document.querySelector("[data-catalogo]");
  if (!raiz) return;
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const pecas = Object.fromEntries(window.CATALOGO.pecas.map((p) => [p.id, p]));
  const norm = (s) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();

  /* ---------- filtros ---------- */
  const busca = $("[data-busca]");
  const modelo = $("[data-modelo]");
  const chips = $$("[data-chips] .chip");
  const cards = $$("[data-peca]");
  const contagem = $("[data-contagem]");
  const vazio = $("[data-vazio]");
  const indice = new Map(cards.map((c) => {
    const p = pecas[c.dataset.peca];
    return [c, norm([p.nome, p.cat, ...p.cod, ...p.modelos].join(" "))];
  }));

  const params = new URLSearchParams(location.search);
  const estado = { q: params.get("q") || "", cat: params.get("cat") || "", modelo: params.get("modelo") || "" };
  busca.value = estado.q;
  if ([...modelo.options].some((o) => o.value === estado.modelo)) modelo.value = estado.modelo; else estado.modelo = "";

  // modelo específico também mostra as peças gerais da mesma linha
  const familia = (m) => (m.startsWith("BG") ? "Girosférico" : m === "25x40" ? "Mandíbula" : null);

  function aplicar() {
    const termos = norm(estado.q).split(/\s+/).filter(Boolean);
    let n = 0;
    cards.forEach((c) => {
      const p = pecas[c.dataset.peca];
      const okTexto = termos.every((t) => indice.get(c).includes(t));
      const okCat = !estado.cat || p.cat === estado.cat;
      const okMod = !estado.modelo || p.modelos.includes(estado.modelo) || (familia(estado.modelo) && p.modelos.includes(familia(estado.modelo)));
      const mostra = okTexto && okCat && okMod;
      c.hidden = !mostra;
      if (mostra) n++;
    });
    chips.forEach((ch) => ch.setAttribute("aria-pressed", String(ch.dataset.cat === estado.cat)));
    contagem.textContent = n === 1 ? "1 peça" : `${n} peças`;
    vazio.hidden = n > 0;
    const u = new URLSearchParams();
    Object.entries(estado).forEach(([k, v]) => v && u.set(k, v));
    history.replaceState(null, "", u.toString() ? `?${u}` : location.pathname);
  }

  let espera;
  busca.addEventListener("input", () => { clearTimeout(espera); espera = setTimeout(() => { estado.q = busca.value.trim(); aplicar(); }, 120); });
  modelo.addEventListener("change", () => { estado.modelo = modelo.value; aplicar(); });
  chips.forEach((ch) => ch.addEventListener("click", () => { estado.cat = ch.dataset.cat; aplicar(); }));
  $("[data-limpar]").addEventListener("click", () => {
    Object.assign(estado, { q: "", cat: "", modelo: "" });
    busca.value = ""; modelo.value = "";
    aplicar();
  });
  aplicar();
  if (estado.cat) chips.find((c) => c.dataset.cat === estado.cat)?.scrollIntoView({ inline: "center", block: "nearest" });

  /* ---------- lista de cotação ---------- */
  const CHAVE = "wrm-cotacao";
  let lista = {};
  try { lista = JSON.parse(localStorage.getItem(CHAVE)) || {}; } catch { lista = {}; }
  Object.keys(lista).forEach((id) => { if (!pecas[id]) delete lista[id]; });
  const salvar = () => { try { localStorage.setItem(CHAVE, JSON.stringify(lista)); } catch {} };

  const caixa = $("[data-lista]");
  const barra = $("[data-lista-abre]");
  const painel = $("[data-lista-painel]");
  const qtd = $("[data-lista-qtd]");
  const txt = $("[data-lista-txt]");
  const itens = $("[data-lista-itens]");
  const form = $("[data-lista-form]");
  const aviso = $("[data-lista-aviso]");

  const total = () => Object.keys(lista).length;

  function desenhar(pulsar) {
    const n = total();
    caixa.hidden = n === 0;
    if (n === 0) fecharPainel();
    qtd.textContent = n;
    txt.textContent = n === 1 ? "peça na cotação" : "peças na cotação";
    if (pulsar) { qtd.classList.remove("pulsa"); void qtd.offsetWidth; qtd.classList.add("pulsa"); }
    $$("[data-add]").forEach((b) => {
      const tem = b.dataset.add in lista;
      b.setAttribute("aria-pressed", String(tem));
      $("[data-add-txt]", b).textContent = tem ? "Na cotação" : "Adicionar à cotação";
    });
    itens.innerHTML = Object.entries(lista).map(([id, q]) => `
      <li class="lista__item">
        <img src="assets/img/pecas/${id}-p.webp" alt="" width="56" height="42">
        <p>${pecas[id].nome}</p>
        <div class="qtd" role="group" aria-label="Quantidade de ${pecas[id].nome}">
          <button type="button" data-menos="${id}" aria-label="Diminuir">−</button>
          <output>${q}</output>
          <button type="button" data-mais="${id}" aria-label="Aumentar">+</button>
        </div>
      </li>`).join("");
  }

  function abrirPainel() { painel.hidden = false; barra.setAttribute("aria-expanded", "true"); }
  function fecharPainel() { painel.hidden = true; barra.setAttribute("aria-expanded", "false"); }

  document.addEventListener("click", (e) => {
    const add = e.target.closest("[data-add]");
    const mais = e.target.closest("[data-mais]");
    const menos = e.target.closest("[data-menos]");
    if (add) {
      const id = add.dataset.add;
      if (id in lista) delete lista[id]; else lista[id] = 1;
      salvar(); desenhar(true);
    } else if (mais) {
      lista[mais.dataset.mais]++; salvar(); desenhar();
    } else if (menos) {
      const id = menos.dataset.menos;
      if (--lista[id] <= 0) delete lista[id];
      salvar(); desenhar();
    }
  });
  barra.addEventListener("click", () => (painel.hidden ? abrirPainel() : fecharPainel()));
  $("[data-lista-fecha]").addEventListener("click", fecharPainel);
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && !painel.hidden) { fecharPainel(); barra.focus(); } });

  function mensagem() {
    const d = Object.fromEntries(new FormData(form));
    const linhas = ["Olá, WRM! Gostaria de cotar as peças abaixo:", ""];
    Object.entries(lista).forEach(([id, q]) => linhas.push(`• ${q}x ${pecas[id].nome}`));
    linhas.push("");
    if (d.modelo) linhas.push(`Britador: ${d.modelo}`);
    if (d.nome) linhas.push(`Nome: ${d.nome}`);
    if (d.empresa) linhas.push(`Empresa: ${d.empresa}`);
    if (d.obs) linhas.push(`Obs.: ${d.obs}`);
    return linhas.join("\n").trim();
  }
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    window.abrirWhats(mensagem());
    aviso.textContent = "Abrimos o WhatsApp de vendas com a lista pronta.";
  });
  $("[data-lista-copia]").addEventListener("click", async () => {
    try { await navigator.clipboard.writeText(mensagem()); aviso.textContent = "Lista copiada."; }
    catch { aviso.textContent = "Não deu para copiar neste navegador."; }
  });
  $("[data-lista-limpa]").addEventListener("click", () => { lista = {}; salvar(); desenhar(); });

  desenhar();
})();
