/* Escritório da fábrica — pixel art animado que mostra os agentes trabalhando num post.
   Uso: const e = Escritorio.criar(elemento, {aoClicar}); e.carregar(eventos, historicoTexto); e.vivo(evento); e.destruir();
   Eventos: {agente, estado: trabalhando|pronto|erro, fala, criado_em}
*/
(function () {
  const W = 400, H = 250;
  const AG = {
    planejadora: { nome: "Planejadora", sala: "redacao", cab: "#5b3a29", cam: "#3b82f6", pele: "#e8b48c", papel: "Escolhe o ângulo da história e o post vencedor que serve de base." },
    escritora:   { nome: "Escritora",   sala: "redacao", cab: "#1f1b18", cam: "#eab308", pele: "#c98d63", papel: "Escreve a capa, os slides e a legenda copiando e remodelando o vencedor." },
    plateia:     { nome: "Plateia",     sala: "redacao", cab: "#6b4423", cam: "#ef4444", pele: "#f0c9a0", papel: "4 leitores (Diego, Marcos, Renata e o cético Paulo) dizem se parariam no post." },
    diagramador: { nome: "Diagramador", sala: "estudio", cab: "#2b2b2b", cam: "#22c55e", pele: "#d9a37a", papel: "Divide o texto aprovado em slides e escolhe o molde de cada um, sem mudar palavras." },
    diretor:     { nome: "Diretor de cena", sala: "estudio", cab: "#8a8a8a", cam: "#a855f7", pele: "#e3b089", papel: "Decide o instante exato da foto, os detalhes do texto e quanto da emoção aparece no rosto." },
    fotografo:   { nome: "Fotógrafo",   sala: "estudio", cab: "#3d2314", cam: "#f97316", pele: "#b97a52", papel: "Gera a foto realista (gpt-image) seguindo a ficha do Diretor." },
    conferente:  { nome: "Conferente",  sala: "estudio", cab: "#c9c9c9", cam: "#14b8a6", pele: "#f1c9a5", papel: "Olha a foto com visão de editor: dá nota, aponta o que falta e o que está exagerado." },
    retocador:   { nome: "Retocador",   sala: "estudio", cab: "#b5651d", cam: "#ec4899", pele: "#e0ac85", papel: "Corrige só o que o Conferente apontou, mantendo o resto da foto igual." },
    montador:    { nome: "Montador",    sala: "estudio", cab: "#222",    cam: "#64748b", pele: "#c68b62", papel: "Desenha os slides em 1080×1350 com os moldes copiados dos vencedores." },
    entregador:  { nome: "Entregador",  sala: "estudio", cab: "#4a2f1d", cam: "#0ea5e9", pele: "#dba57c", papel: "Guarda os slides no banco e entrega na sua tela." },
  };
  // posição da cadeira (onde o boneco senta) — coordenadas do mundo 400x250
  const POS = {
    planejadora: [36, 84], escritora: [98, 84], plateia: [64, 200],
    diagramador: [162, 84], diretor: [224, 84], fotografo: [286, 84], conferente: [352, 84],
    retocador: [180, 196], montador: [256, 196], entregador: [332, 196],
  };
  const ORDEM = ["planejadora", "escritora", "plateia", "diagramador", "diretor", "fotografo", "conferente", "retocador", "montador", "entregador"];
  const EST = { ocioso: "ocioso", trabalhando: "trabalhando", pronto: "pronto", erro: "erro" };

  function px(c, x, y, w, h, cor) { c.fillStyle = cor; c.fillRect(Math.round(x), Math.round(y), w, h); }
  function escurecer(hex, f) { const n = parseInt(hex.slice(1), 16); const r = (n >> 16) * f, g = ((n >> 8) & 255) * f, b = (n & 255) * f; return `rgb(${r | 0},${g | 0},${b | 0})`; }

  // ---------- cenário (desenhado uma vez num canvas de fundo) ----------
  function desenharCenario(c) {
    // parede de cima
    px(c, 0, 0, W, 40, "#3a4a63"); px(c, 0, 36, W, 4, "#2b384c");
    for (const x of [24, 150, 262]) { px(c, x, 8, 44, 20, "#1d2737"); px(c, x + 2, 10, 40, 16, "#8ec5ff"); px(c, x + 2, 18, 40, 1, "#b9dcff"); px(c, x + 21, 10, 2, 16, "#1d2737"); }
    // placa e relógio
    px(c, 330, 9, 52, 18, "#111"); px(c, 331, 10, 50, 16, "#FFD21F"); px(c, 336, 14, 8, 8, "#111"); px(c, 338, 15, 4, 6, "#FFD21F");
    px(c, 110, 12, 14, 14, "#f2f2f2"); px(c, 116, 13, 2, 6, "#222"); px(c, 117, 18, 5, 2, "#222");
    // piso: redação (madeira) e estúdio (carpete azul em placas)
    for (let y = 40; y < H; y += 6) for (let x = 0; x < 128; x += 24) {
      const o = ((y / 6) % 2) * 12; px(c, x - o, y, 24, 6, (x / 24 + y / 6) % 3 ? "#9c6b3e" : "#8f6136"); px(c, x - o, y + 5, 24, 1, "#7a5230");
    }
    for (let y = 40; y < H; y += 16) for (let x = 132; x < W; x += 16) { px(c, x, y, 16, 16, ((x + y) / 16) % 2 ? "#2f5d8a" : "#33669a"); px(c, x, y, 16, 1, "#2a537c"); }
    // parede divisória com porta
    px(c, 128, 40, 4, 92, "#2b384c"); px(c, 128, 168, 4, 82, "#2b384c"); px(c, 126, 130, 8, 2, "#1d2737"); px(c, 126, 166, 8, 2, "#1d2737");
    // tapetes
    px(c, 30, 150, 70, 4, "#7b2d36"); px(c, 30, 210, 70, 4, "#7b2d36");
    // estante e plantas
    estante(c, 2, 120); estante(c, 384, 110);
    planta(c, 112, 44); planta(c, 136, 44); planta(c, 384, 228); planta(c, 4, 228);
    // café
    px(c, 368, 206, 18, 22, "#1f2937"); px(c, 370, 208, 14, 8, "#4b5563"); px(c, 374, 220, 6, 5, "#f5f5f5"); px(c, 360, 228, 34, 4, "#5c4033");
    // sofá da plateia
    px(c, 30, 190, 66, 16, "#b91c1c"); px(c, 30, 186, 66, 6, "#991b1b"); px(c, 26, 188, 6, 18, "#991b1b"); px(c, 94, 188, 6, 18, "#991b1b");
    // quadros
    px(c, 196, 12, 30, 18, "#5c4033"); px(c, 198, 14, 26, 14, "#facc15"); px(c, 198, 22, 26, 6, "#16a34a");
  }
  function estante(c, x, y) { px(c, x, y, 14, 46, "#5c4033"); for (let i = 0; i < 4; i++) { px(c, x + 1, y + 2 + i * 11, 12, 8, "#3b2a1f"); for (let k = 0; k < 4; k++) px(c, x + 2 + k * 3, y + 3 + i * 11, 2, 7, ["#ef4444", "#3b82f6", "#eab308", "#22c55e"][(i + k) % 4]); } }
  function planta(c, x, y) { px(c, x + 3, y + 10, 8, 8, "#92400e"); px(c, x + 2, y + 4, 4, 7, "#15803d"); px(c, x + 8, y + 2, 4, 9, "#16a34a"); px(c, x + 5, y, 4, 10, "#22c55e"); }

  // mesa com monitor de lado (o rosto de quem está sentado fica visível)
  function mesa(c, a, t, ativo) {
    const [x, y] = POS[a]; const tipo = a;
    if (a === "plateia") return;
    // tampo e frente
    px(c, x - 24, y - 2, 48, 5, "#a06a35"); px(c, x - 24, y - 2, 48, 1, "#b97c40"); px(c, x - 24, y + 3, 48, 12, "#7a4a22");
    px(c, x - 22, y + 15, 4, 7, "#4a2f15"); px(c, x + 18, y + 15, 4, 7, "#4a2f15"); px(c, x - 24, y + 3, 48, 1, "#5e3818");
    // monitor à esquerda, virado para a pessoa (vemos a lateral/tela de leve)
    const big = tipo === "conferente";
    const mx = x - 23, mw = big ? 20 : 15, mh = big ? 15 : 12;
    px(c, mx, y - 3 - mh, mw, mh, "#0f172a"); px(c, mx + 1, y - 2 - mh, mw - 2, mh - 2, ativo ? "#0c3b28" : "#1e293b");
    if (ativo) for (let i = 0; i < 3; i++) px(c, mx + 2, y - 1 - mh + i * 3, ((t / 110 + i * 5) % (mw - 5)) + 2, 1, i === 1 ? "#FFD21F" : "#4ade80");
    px(c, mx + mw / 2 - 1, y - 3, 3, 2, "#0f172a");
    // teclado e caneca
    px(c, x - 4, y - 1, 12, 2, "#cbd5e1"); px(c, x + 14, y - 5, 4, 4, "#f8fafc"); px(c, x + 18, y - 4, 1, 2, "#f8fafc");
    if (tipo === "fotografo") { px(c, x + 26, y - 30, 2, 50, "#374151"); px(c, x + 22, y + 18, 10, 2, "#374151"); px(c, x + 20, y - 36, 12, 8, "#111"); px(c, x + 23, y - 34, 5, 4, ativo && (t / 300 | 0) % 6 === 0 ? "#fff" : "#60a5fa"); }
    if (tipo === "montador") { px(c, x + 8, y - 9, 14, 8, "#e5e7eb"); px(c, x + 10, y - 12, 10, 3, "#f9fafb"); if (ativo) px(c, x + 11, y - 1, 8, 3, "#f8fafc"); }
    if (tipo === "entregador") { px(c, x + 6, y - 11, 16, 10, "#a16207"); px(c, x + 7, y - 10, 14, 3, "#facc15"); }
    if (tipo === "diretor") { px(c, x + 6, y - 8, 9, 7, "#f5f5f5"); px(c, x + 7, y - 7, 6, 1, "#9ca3af"); px(c, x + 7, y - 5, 6, 1, "#9ca3af"); }
    if (tipo === "retocador") { px(c, x + 8, y - 6, 10, 5, "#1f2937"); px(c, x + 9, y - 5, 8, 3, "#93c5fd"); }
  }

  // ---------- boneco (cada "pixel" do desenho = 2 px do mundo) ----------
  function boneco(c, ag, x, y, f) {
    const a = AG[ag], U = 2; const X = Math.round(x) - 5 * U, Y = Math.round(y) - 16 * U;
    const p = (ux, uy, uw, uh, cor) => px(c, X + ux * U, Y + uy * U, uw * U, uh * U, cor);
    if (!f.sentado) px(c, X + 2, Y + 16 * U - 1, 7 * U, 3, "rgba(0,0,0,.28)");
    if (!f.sentado) {
      const q = f.quadro % 4, pa = q === 1 ? -1 : q === 3 ? 1 : 0;
      p(2, 11, 2, 4 + (pa < 0 ? -1 : 0), "#1f2937"); p(6, 11, 2, 4 + (pa > 0 ? -1 : 0), "#1f2937");
      p(1.5, 15 + (pa < 0 ? -1 : 0), 3, 1, "#0b0f14"); p(5.5, 15 + (pa > 0 ? -1 : 0), 3, 1, "#0b0f14");
    }
    // tronco com sombra lateral
    p(1, 6, 8, 6, a.cam); p(1, 6, 1, 6, escurecer(a.cam, .8)); p(1, 11, 8, 1, escurecer(a.cam, .65)); p(4, 6, 2, 1, escurecer(a.cam, .7));
    // braços (digitando: alternam)
    const dg = f.digitando ? f.quadro % 2 : 0;
    if (f.sentado && f.digitando) { p(0, 8 + dg, 2, 2, a.pele); p(8, 9 - dg, 2, 2, a.pele); }
    else { p(0, 7, 1, 4, escurecer(a.cam, .85)); p(9, 7, 1, 4, escurecer(a.cam, .85)); p(0, 11, 1, 1, a.pele); p(9, 11, 1, 1, a.pele); }
    if (f.papel) { p(8, 7, 4, 5, "#f8fafc"); p(8.5, 8, 3, 0.5, "#94a3b8"); p(8.5, 9.5, 3, 0.5, "#94a3b8"); }
    // cabeça
    p(2, 0, 6, 6, a.pele); p(2, 5, 6, 1, escurecer(a.pele, .88));
    p(1, -1, 8, 2, a.cab); p(1, 1, 1, 3, a.cab); p(8, 1, 1, 3, a.cab); p(2, 1, 6, 1, a.cab);
    if (f.costas) { p(2, 1, 6, 5, a.cab); }
    else {
      const ox = f.dir === -1 ? -0.5 : f.dir === 1 ? 0.5 : 0;
      const pisca = (f.quadro + ag.length * 3) % 37 === 0;
      if (!pisca) { p(3 + ox, 3, 1, 1, "#111"); p(6 + ox, 3, 1, 1, "#111"); }
      p(3 + ox, 2.5, 1, 0.5, escurecer(a.cab, 1)); p(6 + ox, 2.5, 1, 0.5, escurecer(a.cab, 1));
      p(4 + ox, 4.5, 2, 0.5, f.feliz ? "#9f1239" : escurecer(a.pele, .7));
      p(2, 3.5, 1, 1, "rgba(255,120,120,.18)"); p(7, 3.5, 1, 1, "rgba(255,120,120,.18)");
    }
  }
  function plateiaGrupo(c, t, ativo) {
    const P = [["#3b82f6", "#5b3a29", "#e8b48c"], ["#22c55e", "#111", "#c98d63"], ["#ec4899", "#7c2d12", "#f0c9a0"], ["#6b7280", "#d1d5db", "#e3b089"]];
    P.forEach(([cam, cab, pele], i) => {
      AG.__tmp = { cam, cab, pele };
      const x = 37 + i * 18, y = 202 + (ativo && ((t / 260 + i) | 0) % 2 ? -1 : 0);
      boneco(c, "__tmp", x, y, { sentado: true, quadro: (t / 160) | 0, digitando: false });
    });
  }

  // ---------- motor ----------
  const CSS = `
.escr{display:flex;flex-direction:column;height:100%;min-height:0;background:#0f1115;border:1px solid #23262d;border-radius:14px;overflow:hidden;font-family:Inter,system-ui,sans-serif;color:#e7e7e3}
.escr-topo{display:flex;align-items:center;gap:10px;padding:9px 12px;border-bottom:1px solid #23262d;font-size:13px}
.escr-topo b{font-size:14px}.escr-topo .sp{flex:1}
.escr-st{color:#9aa0a8}.escr-st.on{color:#4ade80}
.escr-bt{background:#1b1e24;border:1px solid #2c3038;color:#e7e7e3;border-radius:8px;padding:5px 9px;font:600 12px Inter,sans-serif;cursor:pointer}
.escr-bt:hover{border-color:#FFD21F;color:#FFD21F}
.escr-palco{position:relative;width:100%;aspect-ratio:400/250;flex:none;background:#0b0d10}
.escr-palco canvas{position:absolute;inset:0;width:100%;height:100%;image-rendering:pixelated;image-rendering:crisp-edges}
.escr-hud{position:absolute;inset:0;pointer-events:none}
.escr-ag{position:absolute;left:0;top:0;width:0;height:0;pointer-events:auto;cursor:pointer;will-change:transform}
.escr-tag{position:absolute;left:0;top:0;transform:translate(-50%,-100%);display:flex;align-items:center;gap:4px;white-space:nowrap;background:rgba(10,12,16,.82);border:1px solid #2c3038;border-radius:999px;padding:2px 7px 2px 5px;font:600 10px/1.2 Inter,sans-serif;color:#e7e7e3}
.escr-tag i{width:6px;height:6px;border-radius:50%;background:#6b7280}
.escr-tag em{font-style:normal;color:#9aa0a8;font-weight:500}
.escr-ag[data-st=trabalhando] .escr-tag{border-color:#4ade80}.escr-ag[data-st=trabalhando] .escr-tag i{background:#4ade80;box-shadow:0 0 0 0 rgba(74,222,128,.7);animation:escrPulso 1.2s infinite}
.escr-ag[data-st=pronto] .escr-tag i{background:#60a5fa}.escr-ag[data-st=erro] .escr-tag{border-color:#f87171}.escr-ag[data-st=erro] .escr-tag i{background:#f87171}
.escr-ag:hover .escr-tag{border-color:#FFD21F}
@keyframes escrPulso{70%{box-shadow:0 0 0 6px rgba(74,222,128,0)}100%{box-shadow:0 0 0 0 rgba(74,222,128,0)}}
.escr-bolha{position:absolute;left:0;bottom:22px;transform:translateX(-50%);width:max-content;max-width:210px;background:#fff;color:#111;border-radius:10px;padding:6px 9px;font:500 11px/1.35 Inter,sans-serif;box-shadow:0 6px 18px rgba(0,0,0,.45);animation:escrEntra .25s ease-out}
.escr-bolha::after{content:"";position:absolute;left:50%;bottom:-5px;transform:translateX(-50%) rotate(45deg);width:10px;height:10px;background:#fff}
.escr-bolha.pronto{background:#ecfdf5}.escr-bolha.pronto::after{background:#ecfdf5}.escr-bolha.erro{background:#fef2f2}.escr-bolha.erro::after{background:#fef2f2}
@keyframes escrEntra{from{opacity:0;transform:translate(-50%,6px) scale(.96)}to{opacity:1;transform:translate(-50%,0)}}
.escr-ficha{position:absolute;right:10px;top:10px;width:250px;background:rgba(15,17,21,.97);border:1px solid #2c3038;border-radius:12px;padding:12px 14px;font-size:12.5px;line-height:1.45;box-shadow:0 10px 30px rgba(0,0,0,.5);z-index:3}
.escr-ficha h4{margin:0 0 4px;font-size:15px}.escr-ficha h5{margin:10px 0 4px;font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:#9aa0a8}
.escr-ficha p{margin:0;color:#cfd2d6}.escr-ficha ul{margin:0;padding-left:16px}.escr-ficha li{margin:3px 0}.escr-ficha li.erro{color:#fca5a5}.escr-ficha li.pronto{color:#a7f3d0}
.escr-ficha .x{position:absolute;right:8px;top:6px;background:none;border:0;color:#9aa0a8;font-size:18px;cursor:pointer}
.escr-feed{flex:1;min-height:60px;overflow:auto;padding:8px 12px;border-top:1px solid #23262d;font-size:12px;line-height:1.45}
.escr-linha{padding:3px 0;color:#cfd2d6}.escr-linha .h{color:#6b7280;margin-right:6px;font-variant-numeric:tabular-nums}.escr-linha.erro{color:#fca5a5}
`;
  function estilo() { if (document.getElementById("escr-css")) return; const s = document.createElement("style"); s.id = "escr-css"; s.textContent = CSS; document.head.appendChild(s); }

  function criar(container, op = {}) {
    estilo();
    const raiz = document.createElement("div"); container.appendChild(raiz);
    raiz.classList.add("escr");
    raiz.innerHTML = `<div class="escr-topo"><b>Escritório</b><span class="escr-st">—</span><span class="sp"></span>
      <button class="escr-bt" data-escr="rever">▶ Rever como foi feito</button><button class="escr-bt" data-escr="vel" title="Velocidade">1×</button></div>
      <div class="escr-palco"><canvas class="escr-fundo" width="${W}" height="${H}"></canvas><canvas class="escr-cena" width="${W}" height="${H}"></canvas><div class="escr-hud"></div>
      <div class="escr-ficha" hidden></div></div>
      <div class="escr-feed"></div>`;
    const fundo = raiz.querySelector(".escr-fundo"), cena = raiz.querySelector(".escr-cena"), hud = raiz.querySelector(".escr-hud");
    const ficha = raiz.querySelector(".escr-ficha"), feed = raiz.querySelector(".escr-feed"), st = raiz.querySelector(".escr-st");
    desenharCenario(fundo.getContext("2d"));
    const c = cena.getContext("2d");
    const S = {}; // estado dos agentes
    ORDEM.forEach((k) => { const [x, y] = POS[k]; S[k] = { x, y, casa: [x, y], estado: "ocioso", fala: "", falaVis: "", falaAte: 0, rota: [], papel: false, log: [], feliz: 0 }; });
    let entregaTxt = "", fila = [], ultimoPronto = null, vel = 1, rodando = true, t0 = performance.now(), aoVivo = false, todos = [];
    // HUD: balão + etiqueta por agente
    const tags = {};
    ORDEM.forEach((k) => {
      const d = document.createElement("div"); d.className = "escr-ag"; d.dataset.ag = k;
      d.innerHTML = `<div class="escr-bolha" hidden></div><div class="escr-tag"><i></i><span>${AG[k].nome}</span><em>${EST.ocioso}</em></div>`;
      hud.appendChild(d); tags[k] = d;
    });
    function escala() { return cena.clientWidth / W; }

    function andar(k, destino, depois) {
      const a = S[k], [dx, dy] = destino, corredor = 132;
      a.rota = [[a.x, corredor], [dx, corredor], [dx, dy]].filter((p, i, arr) => i === 0 || p[0] !== arr[i - 1][0] || p[1] !== arr[i - 1][1]);
      a.depois = depois;
    }
    function entregar(de, para, depois) {
      const a = S[de]; if (!a || de === para) { depois && depois(); return; }
      a.papel = true; entregaTxt = `${AG[de].nome} levando a folha para ${AG[para].nome}`;
      const [px2, py2] = S[para].casa;
      andar(de, [px2 + (px2 > a.casa[0] ? -14 : 14), py2 + 2], () => {
        a.papel = false; S[para].papelNaMesa = performance.now(); entregaTxt = "";
        depois && depois();
        setTimeout(() => andar(de, a.casa, null), 450 / vel);
      });
    }
    function falar(k, txt, estado) {
      const a = S[k]; a.estado = estado || "trabalhando"; a.fala = txt; a.falaVis = ""; a.falaAte = performance.now() + ((estado === "pronto" ? 4500 : 9000) + txt.length * 30) / vel;
      if (estado === "pronto") a.feliz = performance.now() + 1500;
      const b = tags[k].querySelector(".escr-bolha"); b.hidden = false; b.className = "escr-bolha " + (estado || "trabalhando");
      tags[k].querySelector("em").textContent = EST[a.estado] || a.estado; tags[k].dataset.st = a.estado;
    }
    function processar(ev) {
      const k = ev.agente; if (!S[k]) return;
      S[k].log.push(ev);
      const linha = document.createElement("div"); linha.className = "escr-linha " + ev.estado;
      const hora = ev.criado_em ? new Date(ev.criado_em).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : "";
      linha.innerHTML = `<span class="h">${hora}</span><b style="color:${AG[k].cam}">${AG[k].nome}</b> ${esc(ev.fala)}`;
      feed.prepend(linha); while (feed.children.length > 40) feed.lastChild.remove();
      const comecar = () => falar(k, ev.fala, ev.estado);
      if (ev.estado === "trabalhando" && ultimoPronto && ultimoPronto !== k && S[ultimoPronto].rota.length === 0) {
        const de = ultimoPronto; ultimoPronto = null; entregar(de, k, comecar);
      } else comecar();
      if (ev.estado === "pronto") ultimoPronto = k;
      ORDEM.forEach((o) => { if (o !== k && S[o].estado === "trabalhando" && ev.estado === "trabalhando") { S[o].estado = "pronto"; tags[o].dataset.st = "pronto"; tags[o].querySelector("em").textContent = "pronto"; } });
    }
    function tocarFila() {
      if (!fila.length) return;
      const ev = fila.shift(); processar(ev);
      const espera = ev.estado === "pronto" ? 2600 : 3400;
      setTimeout(tocarFila, espera / vel);
    }
    function esc(s) { return String(s ?? "").replace(/[&<>"]/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch])); }

    // ocioso: de vez em quando alguém vai tomar café ou olhar a planta
    let proxPasseio = performance.now() + 4000;
    function passeios(agora) {
      if (agora < proxPasseio) return; proxPasseio = agora + 5000 + Math.random() * 6000;
      if (ORDEM.some((k) => S[k].estado === "trabalhando" || S[k].rota.length)) return;
      const livres = ORDEM.filter((k) => k !== "plateia" && S[k].estado !== "trabalhando"); const k = livres[(Math.random() * livres.length) | 0];
      const destinos = [[364, 230], [120, 62], [140, 62], [20, 236]];
      const d = destinos[(Math.random() * destinos.length) | 0];
      andar(k, d, () => setTimeout(() => andar(k, S[k].casa, null), 1800 / vel));
    }

    function quadro(agora) {
      if (!rodando) return;
      const t = (agora - t0) * vel, q = (t / 160) | 0;
      c.clearRect(0, 0, W, H);
      passeios(agora);
      // movimento
      ORDEM.forEach((k) => {
        const a = S[k]; if (!a.rota.length) return;
        const [tx, ty] = a.rota[0], v = 0.9 * vel, dx = tx - a.x, dy = ty - a.y, dist = Math.hypot(dx, dy);
        if (dist <= v) { a.x = tx; a.y = ty; a.rota.shift(); if (!a.rota.length && a.depois) { const f = a.depois; a.depois = null; f(); } }
        else { a.x += (dx / dist) * v; a.y += (dy / dist) * v; a.dir = Math.abs(dx) > Math.abs(dy) ? Math.sign(dx) : 0; a.costas = dy < -0.2 && Math.abs(dy) > Math.abs(dx); }
      });
      // desenha por profundidade (y)
      const ordem = [...ORDEM].sort((p, q2) => S[p].y - S[q2].y);
      const mesas = new Set();
      for (const k of ordem) {
        const a = S[k], sentado = !a.rota.length && Math.abs(a.x - a.casa[0]) < 1 && Math.abs(a.y - a.casa[1]) < 1;
        if (k === "plateia") { if (sentado) { plateiaGrupo(c, t, a.estado === "trabalhando"); continue; } }
        if (sentado) {
          boneco(c, k, a.x, a.y + 4, { sentado: true, quadro: q, digitando: a.estado === "trabalhando", dir: 0, feliz: agora < a.feliz });
          mesa(c, k, t, a.estado === "trabalhando"); mesas.add(k);
          if (a.papelNaMesa && agora - a.papelNaMesa < 6000) { px(c, a.x + 6, a.y + 2, 6, 4, "#f8fafc"); }
        } else {
          if (!mesas.has(k)) { mesa(c, k, t, false); mesas.add(k); }
          boneco(c, k, a.x, a.y, { quadro: q, dir: a.dir, costas: a.costas, papel: a.papel });
        }
      }
      ORDEM.forEach((k) => { if (!mesas.has(k)) mesa(c, k, t, false); });
      // vapor do café
      if (((t / 400) | 0) % 2) { px(c, 376, 200 - ((t / 90) % 6), 1, 2, "rgba(255,255,255,.5)"); }
      // HUD posicionado
      const e = escala();
      ORDEM.forEach((k) => {
        const a = S[k], el = tags[k], b = el.querySelector(".escr-bolha");
        el.style.transform = `translate(${a.x * e}px, ${(a.y - (k === "plateia" ? 34 : 32)) * e}px)`;
        if (a.fala) {
          if (a.falaVis.length < a.fala.length) { a.falaVis = a.fala.slice(0, a.falaVis.length + Math.max(1, Math.round(1.6 * vel))); b.textContent = a.falaVis; }
          if (agora > a.falaAte) { a.fala = ""; b.hidden = true; if (a.estado === "pronto") { a.estado = "ocioso"; el.dataset.st = "ocioso"; el.querySelector("em").textContent = "ocioso"; } }
        }
      });
      const trab = ORDEM.filter((k) => S[k].estado === "trabalhando").map((k) => AG[k].nome);
      st.textContent = entregaTxt ? (aoVivo ? "● ao vivo · " : "") + entregaTxt : trab.length ? `${aoVivo ? "● ao vivo · " : ""}${trab.join(", ")} trabalhando` : (aoVivo ? "● ao vivo · esperando o próximo passo" : "ninguém trabalhando agora");
      st.className = "escr-st" + (trab.length || entregaTxt ? " on" : "");
      requestAnimationFrame(quadro);
    }
    requestAnimationFrame(quadro);

    // clique: ficha do agente
    hud.addEventListener("click", (ev) => {
      const el = ev.target.closest(".escr-ag"); if (!el) return; const k = el.dataset.ag, a = AG[k];
      const log = S[k].log.slice(-6).reverse().map((e) => `<li class="${e.estado}">${esc(e.fala)}</li>`).join("") || "<li>Ainda não fez nada neste post.</li>";
      ficha.innerHTML = `<button class="x" aria-label="Fechar">×</button><h4 style="color:${a.cam}">${a.nome}</h4><p>${a.papel}</p><h5>O que fez neste post</h5><ul>${log}</ul>`;
      ficha.hidden = false; op.aoClicar && op.aoClicar(k);
    });
    ficha.addEventListener("click", (ev) => { if (ev.target.closest(".x")) ficha.hidden = true; });
    raiz.querySelector('[data-escr="vel"]').onclick = (ev) => { vel = vel === 1 ? 2 : vel === 2 ? 4 : 1; ev.target.textContent = vel + "×"; };
    raiz.querySelector('[data-escr="rever"]').onclick = () => {
      ORDEM.forEach((k) => { S[k].log = []; S[k].estado = "ocioso"; S[k].fala = ""; tags[k].querySelector(".escr-bolha").hidden = true; tags[k].dataset.st = "ocioso"; tags[k].querySelector("em").textContent = "ocioso"; });
      feed.innerHTML = ""; ultimoPronto = null; fila = todos.slice(); tocarFila();
    };

    return {
      carregar(eventos, ehAoVivo) {
        todos = eventos.slice(); aoVivo = !!ehAoVivo; feed.innerHTML = "";
        if (!eventos.length) { feed.innerHTML = '<div class="escr-linha">Ainda não há trabalho registrado neste post. Quando você clicar em "Gerar post e thumbnails", a equipe aparece trabalhando aqui.</div>'; return; }
        // mostra o histórico na lista e deixa o último estado de cada agente
        eventos.slice(-40).forEach((e) => { S[e.agente] && S[e.agente].log.push(e); const l = document.createElement("div"); l.className = "escr-linha " + e.estado; l.innerHTML = `<span class="h">${e.criado_em ? new Date(e.criado_em).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }) : ""}</span><b style="color:${(AG[e.agente] || {}).cam}">${(AG[e.agente] || {}).nome || e.agente}</b> ${esc(e.fala)}`; feed.prepend(l); });
        const ult = eventos[eventos.length - 1];
        if (aoVivo && ult) falar(ult.agente, ult.fala, ult.estado);
      },
      vivo(ev) { aoVivo = true; todos.push(ev); fila.push(ev); if (fila.length === 1) tocarFila(); },
      reanexar(novo) { if (novo && raiz.parentNode !== novo) novo.appendChild(raiz); },
      destruir() { rodando = false; raiz.remove(); },
      el: raiz,
    };
  }
  window.Escritorio = { criar, AGENTES: AG };
})();
