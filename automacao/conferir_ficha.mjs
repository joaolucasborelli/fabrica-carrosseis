// Confere a ficha visual antes de gravar o post (grátis, sem API).
// Uso: node automacao/conferir_ficha.mjs caminho.json
// caminho.json = { "pecas": {capa, slides[]}, "ficha": <plano_visual.post>, "reprovados": ["capa_caderno", ...] }
// Se falhar, o robô chamaria a OpenAI para diagramar de novo (gasto). Por isso: só grava o post com ok=true.
import fs from "node:fs";

const SEMPRE_PROIBIDOS = ["capa_caderno", "capa_marcatexto", "conta_visual", "esc_cards", "faixa_amarela", "foto_sticker"];
const CAPA = ["molde", "estilo", "texto", "sub", "titulo", "paragrafos", "rotulos", "numero", "faixa", "cor", "foto_prompt", "foto_prompt2", "famoso", "fato", "marca", "por_que", "foto_fonte", "busca_real", "pessoa_real"];
const NAO_TEXTO = new Set(["molde", "estilo", "cor", "foto_prompt", "foto_prompt2", "por_que", "foto_fonte", "busca_real", "pessoa_real", "mesma_pessoa", "lado", "famoso", "fato", "marca"]);
const norm = (s) => String(s ?? "").replace(/\*\*|\[\[|\]\]/g, " ").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9\s]/g, " ").split(/\s+/).filter(Boolean);

const d = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const { pecas, ficha } = d;
const proibidos = new Set([...SEMPRE_PROIBIDOS, ...(d.reprovados ?? []).map((x) => String(x).replace(/^tipo:/, ""))]);
const problemas = [];

if (!ficha?.receita) problemas.push("falta receita");
for (const k of CAPA) if (!(k in (ficha?.capa ?? {}))) problemas.push(`capa sem o campo ${k}`);
if (!ficha?.capa?.molde) problemas.push("capa sem molde");
if (!ficha?.capa?.estilo) problemas.push("capa sem estilo");
if (ficha?.capa?.foto_fonte !== "nenhuma" && !ficha?.capa?.foto_prompt) problemas.push("capa sem foto_prompt");
const fs_ = ficha?.slides ?? [];
if (fs_.length !== (pecas.slides ?? []).length) problemas.push(`ficha com ${fs_.length} lâminas, texto com ${(pecas.slides ?? []).length}`);
fs_.forEach((s, i) => {
  if (!s.molde) problemas.push(`lâmina ${i + 2} sem molde`);
  if (proibidos.has(s.molde)) problemas.push(`lâmina ${i + 2} usa molde reprovado ${s.molde}`);
  if (s.foto_fonte === "ia" && !s.foto_prompt) problemas.push(`lâmina ${i + 2} sem foto_prompt`);
});
if (proibidos.has(ficha?.capa?.molde)) problemas.push(`capa usa molde reprovado ${ficha.capa.molde}`);

// cobertura: as palavras do texto aprovado precisam estar na ficha (o robô exige 93%)
const textos = [];
const junta = (o) => { for (const [k, v] of Object.entries(o ?? {})) { if (NAO_TEXTO.has(k)) continue; if (typeof v === "string") textos.push(v); else if (Array.isArray(v)) v.forEach((x) => (typeof x === "object" ? junta(x) : textos.push(String(x)))); else if (v && typeof v === "object") junta(v); } };
junta(ficha?.capa); fs_.forEach(junta);
const saco = new Map(); for (const w of norm(textos.join(" "))) saco.set(w, (saco.get(w) ?? 0) + 1);
const alvo = norm([pecas.capa, ...(pecas.slides ?? [])].join(" "));
let achou = 0; for (const w of alvo) { const n = saco.get(w) ?? 0; if (n > 0) { achou++; saco.set(w, n - 1); } }
const cobertura = alvo.length ? Math.round((achou / alvo.length) * 1000) / 10 : 0;
if (cobertura < 98) problemas.push(`cobertura do texto ${cobertura}% (mínimo 98% aqui, o robô exige 93%)`);

const r = { ok: problemas.length === 0, cobertura, problemas };
console.log(JSON.stringify(r, null, 1));
process.exit(r.ok ? 0 : 1);
