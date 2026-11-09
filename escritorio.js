/* Escritório da fábrica v2 — um prédio em pixel art com 6 salas, corredor e placas.
   Os agentes trabalham, falam em balões e levam a folha de uma sala para outra.
   Uso: const e = Escritorio.criar(container); e.carregar(eventos, aoVivo); e.vivo(evento); e.reanexar(el); e.destruir();
*/
(function () {
  const W = 640, H = 400;
  const AG = {
    planejadora: { nome: "Planejadora", sala: "redacao", cab: "#6b3f22", cam: "#3b82f6", pele: "#e9b48a", cabelo: "coque", papel: "Escolhe o ângulo da história e o post vencedor que serve de base." },
    escritora:   { nome: "Escritora",   sala: "redacao", cab: "#1f1b18", cam: "#eab308", pele: "#c98d63", cabelo: "longo", papel: "Escreve a capa, os slides e a legenda copiando e remodelando o vencedor." },
    plateia:     { nome: "Plateia",     sala: "plateia", cab: "#6b4423", cam: "#ef4444", pele: "#f0c9a0", papel: "4 leitores (Diego, Marcos, Renata e o cético Paulo) dizem se parariam no post." },
    diagramador: { nome: "Diagramador", sala: "diagramacao", cab: "#2b2b2b", cam: "#22c55e", pele: "#d9a37a", cabelo: "curto", papel: "Escolhe a receita e o molde de cada slide, sem mudar as frases aprovadas." },
    montador:    { nome: "Montador",    sala: "diagramacao", cab: "#111", cam: "#64748b", pele: "#a86f48", cabelo: "careca", papel: "Desenha os slides em 1080×1350 com os moldes do kit." },
    diretor:     { nome: "Diretor de cena", sala: "estudio", cab: "#9a9a9a", cam: "#a855f7", pele: "#e3b089", cabelo: "curto", papel: "Decide o instante exato da foto, os detalhes do texto e quanto da emoção aparece no rosto." },
    fotografo:   { nome: "Fotógrafo",   sala: "estudio", cab: "#3d2314", cam: "#f97316", pele: "#b97a52", cabelo: "bone", papel: "Gera as fotos realistas seguindo a ficha do Diretor, com a mesma pessoa em toda a história." },
    conferente:  { nome: "Conferente",  sala: "conferencia", cab: "#d1d5db", cam: "#14b8a6", pele: "#f1c9a5", cabelo: "curto", papel: "Olha a foto com olho de editor: dá nota, aponta o que falta e o que está exagerado." },
    retocador:   { nome: "Retocador",   sala: "conferencia", cab: "#b5651d", cam: "#ec4899", pele: "#e0ac85", cabelo: "longo", papel: "Corrige só o que o Conferente apontou, mantendo o resto da foto igual." },
    entregador:  { nome: "Entregador",  sala: "expedicao", cab: "#4a2f1d", cam: "#0ea5e9", pele: "#dba57c", cabelo: "curto", papel: "Guarda os slides no banco e entrega na sua tela." },
  };
  const ORDEM = ["planejadora", "escritora", "plateia", "diagramador", "montador", "diretor", "fotografo", "conferente", "retocador", "entregador"];
  // salas: [x, y, w, h], porta (x no corredor), placa
  const SALAS = {
    redacao:     { r: [8, 34, 206, 142],  porta: 182, nome: "Redação" },
    plateia:     { r: [218, 34, 170, 142], porta: 300, nome: "Plateia" },
    estudio:     { r: [392, 34, 240, 142], porta: 418, nome: "Estúdio de foto" },
    diagramacao: { r: [8, 220, 206, 172], porta: 182, nome: "Diagramação e montagem" },
    conferencia: { r: [218, 220, 204, 172], porta: 320, nome: "Conferência" },
    expedicao:   { r: [426, 220, 206, 172], porta: 452, nome: "Expedição" },
  };
  const CORR_Y = 198; // linha do corredor
  const POS = {
    planejadora: [62, 116], escritora: [148, 116], plateia: [303, 124],
    diretor: [482, 112], fotografo: [588, 134],
    diagramador: [62, 300], montador: [148, 300],
    conferente: [276, 300], retocador: [366, 300], entregador: [540, 300],
  };
  const EST = { ocioso: "ocioso", trabalhando: "trabalhando", pronto: "pronto", erro: "erro" };

  const px = (c, x, y, w, h, cor) => { c.fillStyle = cor; c.fillRect(Math.round(x), Math.round(y), w, h); };
  function tom(hex, f) { const n = parseInt(hex.slice(1), 16); const r = Math.min(255, (n >> 16) * f), g = Math.min(255, ((n >> 8) & 255) * f), b = Math.min(255, (n & 255) * f); return `rgb(${r | 0},${g | 0},${b | 0})`; }

  // ---------- cenário ----------
  function piso(c, [x, y, w, h], tipo) {
    if (tipo === "madeira") { for (let j = y; j < y + h; j += 6) for (let i = x - ((j / 6) % 2) * 12; i < x + w; i += 24) { px(c, Math.max(i, x), j, Math.min(24, x + w - Math.max(i, x)), 6, ((i + j) / 6) % 3 ? "#a87445" : "#9a693d"); px(c, Math.max(i, x), j + 5, Math.min(24, x + w - Math.max(i, x)), 1, "#80552f"); } }
    else if (tipo === "carpete") { px(c, x, y, w, h, "#7f1d2d"); for (let j = y; j < y + h; j += 4) for (let i = x + (j % 8); i < x + w; i += 8) px(c, i, j, 1, 1, "#8f2536"); }
    else if (tipo === "concreto") { px(c, x, y, w, h, "#8b8f97"); for (let j = y; j < y + h; j += 32) px(c, x, j, w, 1, "#7b7f87"); for (let i = x; i < x + w; i += 48) px(c, i, y, 1, h, "#7b7f87"); }
    else if (tipo === "xadrez") { for (let j = y; j < y + h; j += 12) for (let i = x; i < x + w; i += 12) px(c, i, j, 12, 12, ((i + j) / 12) % 2 ? "#e9e4d8" : "#d6cfbf"); }
    else if (tipo === "azul") { for (let j = y; j < y + h; j += 16) for (let i = x; i < x + w; i += 16) { px(c, i, j, 16, 16, ((i + j) / 16) % 2 ? "#2f5d8a" : "#33669a"); } }
    else if (tipo === "corredor") { for (let j = y; j < y + h; j += 11) for (let i = x; i < x + w; i += 22) px(c, i, j, 22, 11, ((i / 22 + j / 11) % 2) ? "#cfc8b8" : "#c4bcaa"); }
  }
  function planta(c, x, y, g = 1) { px(c, x, y + 10 * g, 10 * g, 8 * g, "#92400e"); px(c, x + 1, y + 10 * g, 8 * g, 2, "#b45309"); px(c, x + 1, y + 3 * g, 3 * g, 8 * g, "#15803d"); px(c, x + 6 * g, y + 1, 3 * g, 10 * g, "#16a34a"); px(c, x + 3 * g, y - 2, 4 * g, 12 * g, "#22c55e"); }
  function estante(c, x, y) { px(c, x, y, 26, 40, "#5c4033"); for (let i = 0; i < 3; i++) { px(c, x + 2, y + 3 + i * 12, 22, 9, "#3b2a1f"); for (let k = 0; k < 6; k++) px(c, x + 3 + k * 3.6, y + 4 + i * 12, 3, 8 - (k % 3), ["#ef4444", "#3b82f6", "#eab308", "#22c55e", "#a855f7", "#f97316"][(i + k) % 6]); } }
  function quadro(c, x, y, w, h, cores) { px(c, x - 2, y - 2, w + 4, h + 4, "#4a3423"); px(c, x, y, w, h, cores[0]); px(c, x, y + h * .6, w, h * .4, cores[1]); if (cores[2]) px(c, x + w * .65, y + 3, w * .2, w * .2, cores[2]); }
  function tapete(c, x, y, w, h, cor, borda) { px(c, x, y, w, h, borda); px(c, x + 3, y + 3, w - 6, h - 6, cor); }
  function janela(c, x, y) { px(c, x, y, 40, 18, "#1d2737"); px(c, x + 2, y + 2, 17, 14, "#8ec5ff"); px(c, x + 21, y + 2, 17, 14, "#8ec5ff"); px(c, x + 2, y + 8, 36, 1, "#b9dcff"); }

  function desenharCenario(c) {
    px(c, 0, 0, W, H, "#1a1f29");
    // fachada de cima com janelas
    px(c, 0, 0, W, 34, "#3a4a63"); px(c, 0, 30, W, 4, "#2b384c");
    for (let x = 18; x < W - 40; x += 74) janela(c, x, 7);
    px(c, 268, 6, 104, 22, "#111"); px(c, 270, 8, 100, 18, "#FFD21F"); // placa da fábrica (texto no HUD)
    // pisos
    piso(c, SALAS.redacao.r, "madeira"); piso(c, SALAS.plateia.r, "carpete"); piso(c, SALAS.estudio.r, "concreto");
    piso(c, SALAS.diagramacao.r, "xadrez"); piso(c, SALAS.conferencia.r, "azul"); piso(c, SALAS.expedicao.r, "concreto");
    piso(c, [0, 176, W, 44], "corredor");
    // paredes (com vãos de porta)
    const parede = "#2b2f3a", topo = "#454b5a";
    for (const s of Object.values(SALAS)) {
      const [x, y, w, h] = s.r; const emCima = y < 176;
      px(c, x - 4, y - 4, w + 8, 4, parede); px(c, x - 4, y + h, w + 8, 4, parede); px(c, x - 4, y - 4, 4, h + 8, parede); px(c, x + w, y - 4, 4, h + 8, parede);
      // vão da porta no lado do corredor
      const py = emCima ? y + h : y - 4;
      px(c, s.porta - 11, py, 22, 4, "#cfc8b8"); px(c, s.porta - 13, py, 2, 4, topo); px(c, s.porta + 11, py, 2, 4, topo);
      // placa ao lado da porta (o texto vem no HUD)
      px(c, s.porta + 15, emCima ? y + h + 6 : y - 16, 46, 10, "#111"); px(c, s.porta + 16, emCima ? y + h + 7 : y - 15, 44, 8, "#FFD21F");
    }
    // ---- Redação: quadro branco, estante, tapete, planta, luminárias
    px(c, 30, 40, 70, 30, "#e5e7eb"); px(c, 31, 41, 68, 28, "#f8fafc"); for (let i = 0; i < 4; i++) px(c, 36, 46 + i * 6, 30 + (i * 13) % 25, 1, ["#ef4444", "#2563eb", "#16a34a", "#111"][i]); px(c, 78, 48, 12, 12, "#FFD21F");
    estante(c, 172, 44); planta(c, 14, 150); tapete(c, 30, 136, 150, 30, "#1e3a8a", "#172554");
    // ---- Plateia: sofá, TV na parede, mesinha, planta
    px(c, 262, 40, 82, 44, "#111"); px(c, 265, 43, 76, 38, "#0b1220"); px(c, 270, 50, 30, 20, "#FFD21F"); px(c, 304, 50, 32, 4, "#e5e7eb"); px(c, 304, 58, 26, 3, "#9ca3af"); px(c, 304, 64, 22, 3, "#9ca3af");
    px(c, 258, 112, 92, 20, "#b91c1c"); px(c, 258, 106, 92, 8, "#991b1b"); px(c, 252, 108, 8, 24, "#991b1b"); px(c, 348, 108, 8, 24, "#991b1b");
    px(c, 284, 146, 40, 14, "#5c4033"); px(c, 290, 142, 8, 6, "#f8fafc"); px(c, 306, 141, 10, 7, "#f59e0b"); planta(c, 364, 148); planta(c, 224, 148);
    // ---- Estúdio: fundo infinito, 2 softboxes, cabos
    px(c, 520, 38, 100, 86, "#e7e5e4"); px(c, 520, 110, 100, 14, "#d6d3d1");
    for (const sx of [506, 618]) { px(c, sx, 60, 2, 70, "#374151"); px(c, sx - 10, 52, 22, 14, "#f8fafc"); px(c, sx - 10, 52, 22, 2, "#e5e7eb"); px(c, sx - 6, 128, 14, 2, "#374151"); }
    px(c, 410, 150, 60, 2, "#111"); px(c, 470, 150, 2, 18, "#111"); quadro(c, 404, 44, 34, 24, ["#60a5fa", "#16a34a", "#fde047"]);
    // ---- Corredor: café, bebedouro, banco, quadros, plantas, relógio
    px(c, 236, 180, 18, 14, "#1f2937"); px(c, 238, 182, 14, 6, "#4b5563"); px(c, 242, 189, 6, 4, "#f5f5f5");
    px(c, 262, 178, 10, 16, "#93c5fd"); px(c, 263, 180, 8, 6, "#dbeafe"); px(c, 262, 194, 10, 2, "#64748b");
    px(c, 540, 202, 50, 8, "#78350f"); px(c, 542, 210, 4, 6, "#451a03"); px(c, 584, 210, 4, 6, "#451a03");
    planta(c, 4, 180); planta(c, 624, 180); planta(c, 400, 182, 1);
    // ---- Diagramação: mural com slides, impressora, pilhas de papel
    px(c, 26, 226, 90, 34, "#a16207"); for (let i = 0; i < 8; i++) px(c, 30 + (i % 4) * 21, 230 + Math.floor(i / 4) * 15, 17, 12, ["#111", "#f8fafc", "#FFD21F", "#111", "#f8fafc", "#111", "#FFD21F", "#f8fafc"][i]);
    estante(c, 180, 230); planta(c, 14, 366); px(c, 120, 370, 30, 12, "#f8fafc"); px(c, 122, 366, 26, 4, "#e5e7eb");
    // ---- Conferência: telão com nota, planta, tapete
    px(c, 252, 226, 120, 40, "#111"); px(c, 255, 229, 114, 34, "#0f172a"); px(c, 262, 236, 40, 20, "#334155"); px(c, 308, 238, 54, 4, "#4ade80"); px(c, 308, 246, 40, 4, "#facc15"); px(c, 308, 254, 26, 4, "#f87171");
    tapete(c, 238, 340, 170, 36, "#0f766e", "#115e59"); planta(c, 400, 366);
    // ---- Expedição: prateleiras com caixas, carrinho, porta de saída
    for (let i = 0; i < 3; i++) { px(c, 590, 232 + i * 40, 36, 3, "#78350f"); for (let k = 0; k < 3; k++) px(c, 592 + k * 11, 220 + i * 40, 10, 12, ["#b45309", "#a16207", "#92400e"][(i + k) % 3]); }
    px(c, 470, 360, 40, 20, "#64748b"); px(c, 472, 352, 16, 10, "#b45309"); px(c, 490, 354, 14, 8, "#a16207"); px(c, 474, 380, 6, 6, "#111"); px(c, 500, 380, 6, 6, "#111");
    px(c, 600, 380, 26, 12, "#166534"); px(c, 602, 382, 22, 3, "#4ade80");
  }

  // ---------- mobília por agente (desenhada por cima de quem está sentado) ----------
  function mesa(c, a, t, ativo) {
    const [x, y] = POS[a];
    if (a === "plateia") return;
    px(c, x - 18, y + 2, 36, 4, "#a06a35"); px(c, x - 18, y + 2, 36, 1, "#bd8148"); px(c, x - 18, y + 6, 36, 9, "#7a4a22"); px(c, x - 16, y + 15, 3, 5, "#4a2f15"); px(c, x + 13, y + 15, 3, 5, "#4a2f15");
    const big = a === "conferente";
    const mw = big ? 16 : 12, mx = x - 17;
    px(c, mx, y - 9, mw, 11, "#0f172a"); px(c, mx + 1, y - 8, mw - 2, 8, ativo ? "#0c3b28" : "#1e293b");
    if (ativo) for (let i = 0; i < 3; i++) px(c, mx + 2, y - 7 + i * 3, ((t / 110 + i * 5) % (mw - 5)) + 2, 1, i === 1 ? "#FFD21F" : "#4ade80");
    px(c, mx + mw / 2 - 1, y + 1, 2, 2, "#0f172a");
    px(c, x - 2, y + 3, 9, 1, "#e2e8f0"); px(c, x + 11, y - 1, 3, 3, "#f8fafc");
    if (a === "fotografo") { px(c, x + 20, y - 26, 2, 40, "#374151"); px(c, x + 16, y + 14, 10, 2, "#374151"); px(c, x + 15, y - 31, 12, 7, "#111"); px(c, x + 18, y - 30, 4, 4, ativo && (t / 300 | 0) % 6 === 0 ? "#fff" : "#60a5fa"); }
    if (a === "montador") { px(c, x + 6, y - 7, 11, 7, "#e5e7eb"); px(c, x + 8, y - 9, 7, 2, "#f9fafb"); if (ativo) px(c, x + 8, y, 7, 3, "#f8fafc"); }
    if (a === "entregador") { px(c, x + 4, y - 9, 13, 9, "#b45309"); px(c, x + 5, y - 8, 11, 2, "#facc15"); }
    if (a === "diretor") { px(c, x + 4, y - 6, 8, 6, "#f5f5f5"); px(c, x + 5, y - 5, 6, 1, "#9ca3af"); px(c, x + 5, y - 3, 5, 1, "#9ca3af"); }
    if (a === "retocador") { px(c, x + 5, y - 5, 9, 5, "#1f2937"); px(c, x + 6, y - 4, 7, 3, "#93c5fd"); }
    if (a === "escritora" || a === "planejadora") { px(c, x + 6, y - 4, 7, 4, "#f8fafc"); px(c, x + 7, y - 3, 5, 1, "#94a3b8"); }
  }

  // ---------- boneco: 12×18, com contorno e sombreado ----------
  function boneco(c, ag, x, y, f) {
    const a = AG[ag] || ag; const X = Math.round(x) - 6, Y = Math.round(y) - 18;
    const p = (ux, uy, uw, uh, cor) => px(c, X + ux, Y + uy, uw, uh, cor);
    const linha = "#14161c";
    if (!f.sentado) p(2, 18, 8, 2, "rgba(0,0,0,.28)");
    // contorno
    p(1, -1, 10, 9, linha); p(0, 7, 12, 8, linha); if (!f.sentado) p(2, 14, 8, 4, linha);
    // pernas
    if (!f.sentado) {
      const q = f.quadro % 4, pa = q === 1 ? -1 : q === 3 ? 1 : 0;
      p(3, 14, 3, 3 + (pa < 0 ? -1 : 0), "#1f2937"); p(6, 14, 3, 3 + (pa > 0 ? -1 : 0), "#1f2937");
      p(3, 17 + (pa < 0 ? -1 : 0), 3, 1, "#0b0f14"); p(6, 17 + (pa > 0 ? -1 : 0), 3, 1, "#0b0f14");
    }
    // tronco
    p(1, 8, 10, 6, a.cam); p(9, 8, 2, 6, tom(a.cam, .78)); p(1, 13, 10, 1, tom(a.cam, .65)); p(5, 8, 2, 1, tom(a.cam, 1.25));
    const dg = f.digitando ? f.quadro % 2 : 0;
    if (f.sentado && f.digitando) { p(1, 11 + dg, 2, 2, a.pele); p(9, 12 - dg, 2, 2, a.pele); }
    else { p(0, 9, 1, 4, tom(a.cam, .85)); p(11, 9, 1, 4, tom(a.cam, .85)); p(0, 13, 1, 1, a.pele); p(11, 13, 1, 1, a.pele); }
    if (f.papel) { p(9, 9, 5, 6, "#f8fafc"); p(10, 10, 3, 1, "#94a3b8"); p(10, 12, 3, 1, "#94a3b8"); }
    // cabeça
    p(2, 1, 8, 7, a.pele); p(2, 7, 8, 1, tom(a.pele, .86));
    const cab = a.cab;
    if (a.cabelo !== "careca") { p(2, 0, 8, 2, cab); p(2, 2, 1, 2, cab); p(9, 2, 1, 2, cab); }
    if (a.cabelo === "longo") { p(1, 2, 1, 6, cab); p(10, 2, 1, 6, cab); }
    if (a.cabelo === "coque") { p(4, -2, 4, 2, cab); }
    if (a.cabelo === "bone") { p(2, 0, 8, 2, tom(a.cam, .9)); p(8, 2, 4, 1, tom(a.cam, .7)); }
    if (f.costas) { p(2, 1, 8, 6, cab); }
    else {
      const ox = f.dir === -1 ? -1 : f.dir === 1 ? 1 : 0;
      if ((f.quadro + ag.length * 3) % 37) { p(4 + ox, 4, 1, 1, "#111"); p(7 + ox, 4, 1, 1, "#111"); }
      p(5 + ox, 6, 2, 1, f.feliz ? "#9f1239" : tom(a.pele, .7));
      p(3, 5, 1, 1, "rgba(255,110,110,.25)"); p(8, 5, 1, 1, "rgba(255,110,110,.25)");
    }
  }
  function plateiaGrupo(c, t, ativo) {
    const P = [["#3b82f6", "#5b3a29", "#e8b48c", "curto"], ["#22c55e", "#111", "#c98d63", "curto"], ["#ec4899", "#7c2d12", "#f0c9a0", "longo"], ["#6b7280", "#d1d5db", "#e3b089", "careca"]];
    P.forEach(([cam, cab, pele, cabelo], i) => {
      const x = 271 + i * 21, y = 124 + (ativo && ((t / 260 + i) | 0) % 2 ? -1 : 0);
      boneco(c, { cam, cab, pele, cabelo }, x, y, { sentado: true, quadro: (t / 160) | 0, digitando: false, dir: 0 });
    });
  }

  // ---------- estilo ----------
  const CSS = `
.escr{display:flex;flex-direction:column;height:100%;min-height:0;background:#0f1115;border:1px solid #23262d;border-radius:14px;overflow:hidden;font-family:Inter,system-ui,sans-serif;color:#e7e7e3}
.escr-topo{display:flex;align-items:center;gap:10px;padding:9px 12px;border-bottom:1px solid #23262d;font-size:13px;flex:none}
.escr-topo b{font-size:14px}.escr-topo .sp{flex:1}
.escr-st{color:#9aa0a8}.escr-st.on{color:#4ade80}
.escr-bt{background:#1b1e24;border:1px solid #2c3038;color:#e7e7e3;border-radius:8px;padding:5px 9px;font:600 12px Inter,sans-serif;cursor:pointer}
.escr-bt:hover{border-color:#FFD21F;color:#FFD21F}
.escr-palco{position:relative;flex:1;min-height:220px;background:#0b0d10;overflow:hidden}
.escr-tela{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%)}
.escr-tela canvas{position:absolute;inset:0;width:100%;height:100%;image-rendering:pixelated;image-rendering:crisp-edges}
.escr-hud{position:absolute;inset:0;pointer-events:none}
.escr-ag{position:absolute;left:0;top:0;width:0;height:0;pointer-events:auto;cursor:pointer}
.escr-bolha{position:absolute;left:0;bottom:6px;transform:translateX(-50%);width:max-content;max-width:200px;background:#fff;color:#111;border-radius:9px;padding:5px 8px;font:500 11px/1.35 Inter,sans-serif;box-shadow:0 6px 18px rgba(0,0,0,.45);animation:escrEntra .25s ease-out;z-index:2}
.escr-bolha::after{content:"";position:absolute;left:50%;bottom:-4px;transform:translateX(-50%) rotate(45deg);width:8px;height:8px;background:#fff}
.escr-bolha.pronto,.escr-bolha.pronto::after{background:#ecfdf5}.escr-bolha.erro,.escr-bolha.erro::after{background:#fef2f2}
.escr-ponto{position:absolute;left:0;top:0;width:7px;height:7px;border-radius:50%;transform:translate(-50%,-50%);background:#6b7280;border:1.5px solid #0b0d10}
.escr-ag[data-st=trabalhando] .escr-ponto{background:#4ade80;animation:escrPulso 1.2s infinite}
.escr-ag[data-st=pronto] .escr-ponto{background:#60a5fa}.escr-ag[data-st=erro] .escr-ponto{background:#f87171}
@keyframes escrPulso{0%{box-shadow:0 0 0 0 rgba(74,222,128,.7)}70%{box-shadow:0 0 0 6px rgba(74,222,128,0)}100%{box-shadow:0 0 0 0 rgba(74,222,128,0)}}
@keyframes escrEntra{from{opacity:0;transform:translate(-50%,5px) scale(.96)}to{opacity:1;transform:translate(-50%,0)}}
.escr-plaq{position:absolute;transform:translate(-50%,-50%);white-space:nowrap;font:700 9px/1 Inter,sans-serif;color:#111;letter-spacing:.02em;text-transform:uppercase;pointer-events:none}
.escr-nome{position:absolute;transform:translate(-50%,0);white-space:nowrap;background:rgba(10,12,16,.78);border:1px solid #2c3038;color:#e7e7e3;border-radius:5px;padding:1px 5px;font:600 9.5px/1.3 Inter,sans-serif;pointer-events:auto;cursor:pointer}
.escr-nome:hover{border-color:#FFD21F;color:#FFD21F}
.escr-ag[data-st=trabalhando]+.escr-nome,.escr-nome.on{border-color:#4ade80}
.escr-marca{position:absolute;transform:translate(-50%,-50%);font:800 11px/1 'Archivo Black',Inter,sans-serif;color:#111;white-space:nowrap;pointer-events:none}
.escr-ficha{position:absolute;right:10px;top:10px;width:250px;background:rgba(15,17,21,.97);border:1px solid #2c3038;border-radius:12px;padding:12px 14px;font-size:12.5px;line-height:1.45;box-shadow:0 10px 30px rgba(0,0,0,.5);z-index:5}
.escr-ficha h4{margin:0 0 4px;font-size:15px}.escr-ficha h5{margin:10px 0 4px;font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:#9aa0a8}
.escr-ficha p{margin:0;color:#cfd2d6}.escr-ficha ul{margin:0;padding-left:16px}.escr-ficha li{margin:3px 0}.escr-ficha li.erro{color:#fca5a5}.escr-ficha li.pronto{color:#a7f3d0}
.escr-ficha .x{position:absolute;right:8px;top:6px;background:none;border:0;color:#9aa0a8;font-size:18px;cursor:pointer}
.escr-feed{flex:none;height:118px;overflow:auto;padding:8px 12px;border-top:1px solid #23262d;font-size:12px;line-height:1.45}
.escr-linha{padding:3px 0;color:#cfd2d6}.escr-linha .h{color:#6b7280;margin-right:6px;font-variant-numeric:tabular-nums}.escr-linha.erro{color:#fca5a5}
`;
  function estilo() { if (document.getElementById("escr-css2")) return; const s = document.createElement("style"); s.id = "escr-css2"; s.textContent = CSS; document.head.appendChild(s); }
  const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch]));

  // ---------- motor ----------
  function criar(container, op = {}) {
    estilo();
    const raiz = document.createElement("div"); raiz.className = "escr"; container.appendChild(raiz);
    raiz.innerHTML = `<div class="escr-topo"><b>Escritório</b><span class="escr-st">—</span><span class="sp"></span>
      <button class="escr-bt" data-escr="rever">▶ Rever como foi feito</button><button class="escr-bt" data-escr="vel" title="Velocidade">1×</button></div>
      <div class="escr-palco"><div class="escr-tela"><canvas class="escr-fundo" width="${W}" height="${H}"></canvas><canvas class="escr-cena" width="${W}" height="${H}"></canvas><div class="escr-hud"></div></div>
      <div class="escr-ficha" hidden></div></div><div class="escr-feed"></div>`;
    const palco = raiz.querySelector(".escr-palco"), tela = raiz.querySelector(".escr-tela");
    const fundo = raiz.querySelector(".escr-fundo"), cena = raiz.querySelector(".escr-cena"), hud = raiz.querySelector(".escr-hud");
    const ficha = raiz.querySelector(".escr-ficha"), feed = raiz.querySelector(".escr-feed"), st = raiz.querySelector(".escr-st");
    desenharCenario(fundo.getContext("2d"));
    const c = cena.getContext("2d");
    let s = 1;
    function encaixar() { const cw = palco.clientWidth, ch = palco.clientHeight; if (!cw || !ch) return; s = Math.min(cw / W, ch / H); tela.style.width = W * s + "px"; tela.style.height = H * s + "px"; }
    // placas (salas e marca) — posições em coordenadas do mundo
    const fixos = [];
    const marca = document.createElement("div"); marca.className = "escr-marca"; marca.textContent = "A HISTÓRIA QUE MUDA"; hud.appendChild(marca); fixos.push([marca, 320, 17]);
    for (const sa of Object.values(SALAS)) {
      const el = document.createElement("div"); el.className = "escr-plaq"; el.textContent = sa.nome.length > 14 ? sa.nome.split(" ")[0] : sa.nome; hud.appendChild(el);
      const emCima = sa.r[1] < 176; fixos.push([el, sa.porta + 38, emCima ? sa.r[1] + sa.r[3] + 11 : sa.r[1] - 11]);
    }
    const S = {}, tags = {}, nomes = {};
    ORDEM.forEach((k) => {
      const [x, y] = POS[k]; S[k] = { x, y, casa: [x, y], estado: "ocioso", fala: "", falaVis: "", falaAte: 0, rota: [], papel: false, log: [], feliz: 0 };
      const d = document.createElement("div"); d.className = "escr-ag"; d.dataset.ag = k; d.innerHTML = `<div class="escr-bolha" hidden></div><div class="escr-ponto"></div>`; hud.appendChild(d); tags[k] = d;
      const n = document.createElement("div"); n.className = "escr-nome"; n.dataset.ag = k; n.textContent = AG[k].nome; hud.appendChild(n); nomes[k] = n;
    });
    let entregaTxt = "", fila = [], ultimoPronto = null, vel = 1, rodando = true, t0 = performance.now(), aoVivo = false, todos = [];

    function portaDe(k) { const sa = SALAS[AG[k].sala]; const emCima = sa.r[1] < 176; return [sa.porta, emCima ? sa.r[1] + sa.r[3] - 8 : sa.r[1] + 8]; }
    function rotaEntre(k, de, para, destino) {
      const [pa, pya] = portaDe(de), [pb, pyb] = portaDe(para);
      const r = [];
      if (AG[de].sala === AG[para].sala) { r.push(destino); return r; }
      r.push([pa, pya], [pa, CORR_Y], [pb, CORR_Y], [pb, pyb], destino);
      return r;
    }
    function andarAte(k, salaDe, salaPara, destino, depois) { S[k].rota = rotaEntre(k, salaDe, salaPara, destino); S[k].depois = depois; }
    function entregar(de, para, depois) {
      const a = S[de]; if (!a || de === para) { depois && depois(); return; }
      a.papel = true; entregaTxt = `${AG[de].nome} levando a folha para ${AG[para].nome}`;
      const [bx, by] = S[para].casa;
      andarAte(de, de, para, [bx + (bx > a.casa[0] ? -16 : 16), by + 8], () => {
        a.papel = false; S[para].papelNaMesa = performance.now(); entregaTxt = "";
        depois && depois();
        setTimeout(() => andarAte(de, para, de, a.casa, null), 450 / vel);
      });
    }
    function falar(k, txt, estado) {
      const a = S[k]; a.estado = estado || "trabalhando"; a.fala = txt; a.falaVis = ""; a.falaAte = performance.now() + ((estado === "pronto" ? 4500 : 9000) + txt.length * 30) / vel;
      if (estado === "pronto") a.feliz = performance.now() + 1500;
      const b = tags[k].querySelector(".escr-bolha"); b.hidden = false; b.className = "escr-bolha " + (estado || "trabalhando");
      tags[k].dataset.st = a.estado; nomes[k].classList.toggle("on", a.estado === "trabalhando");
    }
    function linhaFeed(ev) {
      const k = ev.agente; const l = document.createElement("div"); l.className = "escr-linha " + (ev.estado || "");
      const hora = ev.criado_em ? new Date(ev.criado_em).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : "";
      l.innerHTML = `<span class="h">${hora}</span><b style="color:${(AG[k] || {}).cam}">${(AG[k] || {}).nome || k}</b> ${esc(ev.fala)}`;
      feed.prepend(l); while (feed.children.length > 40) feed.lastChild.remove();
    }
    function processar(ev) {
      const k = ev.agente; if (!S[k]) return;
      S[k].log.push(ev); linhaFeed(ev);
      const comecar = () => falar(k, ev.fala, ev.estado);
      if (ev.estado === "trabalhando" && ultimoPronto && ultimoPronto !== k && S[ultimoPronto].rota.length === 0 && ultimoPronto !== "plateia" && k !== "plateia") {
        const de = ultimoPronto; ultimoPronto = null; entregar(de, k, comecar);
      } else comecar();
      if (ev.estado === "pronto") ultimoPronto = k;
      ORDEM.forEach((o) => { if (o !== k && S[o].estado === "trabalhando" && ev.estado === "trabalhando") { S[o].estado = "pronto"; tags[o].dataset.st = "pronto"; nomes[o].classList.remove("on"); } });
    }
    function tocarFila() { if (!fila.length) return; const ev = fila.shift(); processar(ev); setTimeout(tocarFila, (ev.estado === "pronto" ? 2800 : 3600) / vel); }

    let proxPasseio = performance.now() + 5000;
    function passeios(agora) {
      if (agora < proxPasseio) return; proxPasseio = agora + 6000 + Math.random() * 7000;
      if (ORDEM.some((k) => S[k].estado === "trabalhando" || S[k].rota.length)) return;
      const livres = ORDEM.filter((k) => k !== "plateia"); const k = livres[(Math.random() * livres.length) | 0];
      const destinos = [[246, 204], [266, 204], [565, 214], [130, 204]];
      const d = destinos[(Math.random() * destinos.length) | 0];
      const [pa, pya] = portaDe(k);
      S[k].rota = [[pa, pya], [pa, CORR_Y], d];
      S[k].depois = () => setTimeout(() => { S[k].rota = [[pa, CORR_Y], [pa, pya], S[k].casa]; S[k].depois = null; }, 2200 / vel);
    }

    function quadroAnim(agora) {
      if (!rodando) return;
      encaixar();
      const t = (agora - t0) * vel, q = (t / 160) | 0;
      c.clearRect(0, 0, W, H);
      passeios(agora);
      ORDEM.forEach((k) => {
        const a = S[k]; if (!a.rota.length) return;
        const [tx, ty] = a.rota[0], v = 0.75 * vel, dx = tx - a.x, dy = ty - a.y, dist = Math.hypot(dx, dy);
        if (dist <= v) { a.x = tx; a.y = ty; a.rota.shift(); if (!a.rota.length && a.depois) { const f = a.depois; a.depois = null; f(); } }
        else { a.x += (dx / dist) * v; a.y += (dy / dist) * v; a.dir = Math.abs(dx) > Math.abs(dy) ? Math.sign(dx) : 0; a.costas = dy < -0.2 && Math.abs(dy) > Math.abs(dx); }
      });
      const ordem = [...ORDEM].sort((p1, p2) => S[p1].y - S[p2].y);
      const mesas = new Set();
      for (const k of ordem) {
        const a = S[k], sentado = !a.rota.length && Math.abs(a.x - a.casa[0]) < 1 && Math.abs(a.y - a.casa[1]) < 1;
        if (k === "plateia") { plateiaGrupo(c, t, a.estado === "trabalhando"); continue; }
        if (sentado) {
          boneco(c, k, a.x, a.y + 6, { sentado: true, quadro: q, digitando: a.estado === "trabalhando", dir: 0, feliz: agora < a.feliz });
          mesa(c, k, t, a.estado === "trabalhando"); mesas.add(k);
          if (a.papelNaMesa && agora - a.papelNaMesa < 6000) px(c, a.x + 3, a.y + 3, 6, 4, "#f8fafc");
        } else {
          if (!mesas.has(k)) { mesa(c, k, t, false); mesas.add(k); }
          boneco(c, k, a.x, a.y, { quadro: q, dir: a.dir, costas: a.costas, papel: a.papel });
        }
      }
      if (((t / 400) | 0) % 2) px(c, 245, 176 - ((t / 90) % 5), 1, 2, "rgba(255,255,255,.6)");
      // HUD
      for (const [el, wx, wy] of fixos) { el.style.left = wx * s + "px"; el.style.top = wy * s + "px"; el.style.fontSize = Math.max(7, 4.6 * s) + "px"; }
      ORDEM.forEach((k) => {
        const a = S[k], el = tags[k], b = el.querySelector(".escr-bolha"), [cx, cy] = a.casa;
        const topo = k === "plateia" ? a.y - 22 : (a.rota.length ? a.y - 22 : a.y - 14);
        el.style.transform = `translate(${a.x * s}px, ${topo * s}px)`;
        nomes[k].style.left = cx * s + "px"; nomes[k].style.top = (cy + (k === "plateia" ? 16 : 22)) * s + "px";
        if (a.fala) {
          if (a.falaVis.length < a.fala.length) { a.falaVis = a.fala.slice(0, a.falaVis.length + Math.max(1, Math.round(1.6 * vel))); b.textContent = a.falaVis; }
          if (agora > a.falaAte) { a.fala = ""; b.hidden = true; if (a.estado === "pronto") { a.estado = "ocioso"; el.dataset.st = "ocioso"; } }
        }
      });
      const trab = ORDEM.filter((k) => S[k].estado === "trabalhando").map((k) => AG[k].nome);
      st.textContent = entregaTxt ? (aoVivo ? "● ao vivo · " : "") + entregaTxt : trab.length ? `${aoVivo ? "● ao vivo · " : ""}${trab.join(", ")} trabalhando` : (aoVivo ? "● ao vivo · esperando o próximo passo" : "ninguém trabalhando agora");
      st.className = "escr-st" + (trab.length || entregaTxt ? " on" : "");
      requestAnimationFrame(quadroAnim);
    }
    requestAnimationFrame(quadroAnim);

    function abrirFicha(k) {
      const a = AG[k];
      const log = S[k].log.slice(-6).reverse().map((e) => `<li class="${e.estado}">${esc(e.fala)}</li>`).join("") || "<li>Ainda não fez nada neste post.</li>";
      ficha.innerHTML = `<button class="x" aria-label="Fechar">×</button><h4 style="color:${a.cam}">${a.nome}</h4><p><b>Sala:</b> ${SALAS[a.sala].nome}</p><p>${a.papel}</p><h5>O que fez neste post</h5><ul>${log}</ul>`;
      ficha.hidden = false; op.aoClicar && op.aoClicar(k);
    }
    hud.addEventListener("click", (ev) => { const el = ev.target.closest("[data-ag]"); if (el) abrirFicha(el.dataset.ag); });
    ficha.addEventListener("click", (ev) => { if (ev.target.closest(".x")) ficha.hidden = true; });
    raiz.querySelector('[data-escr="vel"]').onclick = (ev) => { vel = vel === 1 ? 2 : vel === 2 ? 4 : 1; ev.target.textContent = vel + "×"; };
    raiz.querySelector('[data-escr="rever"]').onclick = () => {
      ORDEM.forEach((k) => { S[k].log = []; S[k].estado = "ocioso"; S[k].fala = ""; tags[k].querySelector(".escr-bolha").hidden = true; tags[k].dataset.st = "ocioso"; nomes[k].classList.remove("on"); });
      feed.innerHTML = ""; ultimoPronto = null; fila = todos.slice(); tocarFila();
    };

    return {
      carregar(eventos, ehAoVivo) {
        todos = eventos.slice(); aoVivo = !!ehAoVivo; feed.innerHTML = "";
        if (!eventos.length) { feed.innerHTML = '<div class="escr-linha">Ainda não há trabalho registrado neste post. Quando você clicar em "Gerar post e thumbnails", a equipe aparece trabalhando aqui.</div>'; return; }
        eventos.slice(-40).forEach((e) => { S[e.agente] && S[e.agente].log.push(e); linhaFeed(e); });
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
