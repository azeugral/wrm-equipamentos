/* WRM Equipamentos — menu, entradas, lupa e formulário de cotação */
const CONFIG = {
  whatsVendas: "5519998360495",
  email: "wrm.usinagem@gmail.com",
};
window.WRM = CONFIG;

const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];

window.abrirWhats = (texto) => {
  const url = `https://wa.me/${CONFIG.whatsVendas}?text=${encodeURIComponent(texto)}`;
  window.open(url, "_blank", "noopener");
};

/* ano no rodapé */
$$("[data-ano]").forEach((el) => (el.textContent = new Date().getFullYear()));

/* entrada da abertura */
requestAnimationFrame(() => requestAnimationFrame(() => document.documentElement.classList.add("pronto")));

/* menu no celular */
const botaoMenu = $("[data-menu]");
const nav = $("#nav");
if (botaoMenu && nav) {
  const fechar = () => { nav.classList.remove("aberto"); botaoMenu.setAttribute("aria-expanded", "false"); };
  botaoMenu.addEventListener("click", () => {
    const abrir = !nav.classList.contains("aberto");
    nav.classList.toggle("aberto", abrir);
    botaoMenu.setAttribute("aria-expanded", String(abrir));
  });
  $$("a", nav).forEach((a) => a.addEventListener("click", fechar));
  document.addEventListener("keydown", (e) => e.key === "Escape" && fechar());
  matchMedia("(min-width: 901px)").addEventListener("change", fechar);
}

/* revela ao rolar, com pequeno escalonamento entre irmãos */
const revelar = $$("[data-revela]");
if ("IntersectionObserver" in window && revelar.length) {
  const io = new IntersectionObserver((itens) => {
    itens.forEach((it) => {
      if (!it.isIntersecting) return;
      const el = it.target;
      const irmaos = [...el.parentElement.children].filter((c) => c.hasAttribute("data-revela"));
      el.style.transitionDelay = `${Math.min(irmaos.indexOf(el), 4) * 70}ms`;
      el.classList.add("visto");
      io.unobserve(el);
    });
  }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
  revelar.forEach((el) => io.observe(el));
} else {
  revelar.forEach((el) => el.classList.add("visto"));
}

/* lupa */
const lupa = $("[data-lupa]");
if (lupa) {
  const img = $("[data-lupa-img]", lupa);
  const leg = $("[data-lupa-leg]", lupa);
  const caixa = $(".lupa__caixa", lupa);
  let origem = null;
  const fechar = () => { lupa.hidden = true; document.body.style.overflow = ""; origem && origem.focus(); };
  document.addEventListener("click", (e) => {
    const alvo = e.target.closest("[data-amplia]");
    if (alvo) {
      origem = alvo;
      img.src = alvo.dataset.amplia;
      img.alt = alvo.dataset.leg || "";
      leg.textContent = alvo.dataset.leg || "";
      caixa.classList.toggle("escuro", alvo.hasAttribute("data-escuro"));
      lupa.hidden = false;
      document.body.style.overflow = "hidden";
      $(".lupa__fechar", lupa).focus();
    } else if (e.target.closest("[data-fechar]")) {
      fechar();
    }
  });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && !lupa.hidden) fechar(); });
}

/* setas da faixa de usinagem */
$$("[data-rola]").forEach((b) => b.addEventListener("click", () => {
  const faixa = $(".usinagem");
  faixa.scrollBy({ left: Number(b.dataset.rola) * faixa.clientWidth * 0.8, behavior: "smooth" });
}));

/* formulário de cotação da página inicial */
const form = $("[data-form-cotacao]");
if (form) {
  const aviso = $("[data-aviso]", form);
  const montar = () => {
    const d = Object.fromEntries(new FormData(form));
    const linhas = ["Olá, WRM! Gostaria de uma cotação.", ""];
    if (d.nome) linhas.push(`Nome: ${d.nome}`);
    if (d.empresa) linhas.push(`Empresa: ${d.empresa}`);
    if (d.cidade) linhas.push(`Cidade: ${d.cidade}`);
    if (d.modelo) linhas.push(`Equipamento: ${d.modelo}`);
    linhas.push("", d.msg);
    return linhas.join("\n");
  };
  const valido = () => {
    let ok = true;
    $$("[required]", form).forEach((c) => {
      const vazio = !c.value.trim();
      c.closest(".campo").classList.toggle("erro", vazio);
      if (vazio && ok) { c.focus(); ok = false; }
    });
    aviso.textContent = ok ? "" : "Preencha seu nome e o que você precisa.";
    return ok;
  };
  form.addEventListener("input", (e) => e.target.closest(".campo")?.classList.remove("erro"));
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    if (!valido()) return;
    window.abrirWhats(montar());
    aviso.textContent = "Abrimos o WhatsApp com a mensagem pronta.";
  });
  $("[data-email]", form).addEventListener("click", () => {
    if (!valido()) return;
    location.href = `mailto:${CONFIG.email}?subject=${encodeURIComponent("Pedido de cotação pelo site")}&body=${encodeURIComponent(montar())}`;
  });
}
