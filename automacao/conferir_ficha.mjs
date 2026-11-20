// Confere a ficha visual antes de gravar o post (grátis, sem API).
// Uso: node automacao/conferir_ficha.mjs caminho.json
// caminho.json = { "pecas": {capa, slides[], legenda}, "ficha": <plano_visual.post>, "tipo": "<id em tipos-dp.json>", "reprovados": ["capa_caderno", ...] }
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
  // lâmina que é desenhada com foto não pode ir "sem foto" (o robô repetiria a foto da capa)
  if (["f1_corrido", "fecho_foto", "esc_checklist", "esc_titulo_moldura", "antes_hoje"].includes(s.molde) && !["ia", "real"].includes(s.foto_fonte)) problemas.push(`lâmina ${i + 2} (${s.molde}) precisa de foto: foto_fonte "ia" ou "real"`);
  if (s.foto_fonte === "real" && !(s.busca_real || s.pessoa_real)) problemas.push(`lâmina ${i + 2} com foto real sem busca_real`);
  if (s.foto_fonte === "real" && !s.foto_prompt) problemas.push(`lâmina ${i + 2} com foto real precisa de foto_prompt de reserva (cena sem rosto, se não achar a foto)`);
});
if (proibidos.has(ficha?.capa?.molde)) problemas.push(`capa usa molde reprovado ${ficha.capa.molde}`);

// D-19/D-20: o post segue um tipo da DP (automacao/tipos-dp.json): mesma capa e mesma ordem de lâminas
if (d.tipo) {
  // a fonte é a tabela tipos_post (a rotina manda a linha em d.tipo_def); o arquivo é só a cópia inicial
  const T = JSON.parse(fs.readFileSync(new URL("./tipos-dp.json", import.meta.url), "utf8"));
  const t = d.tipo_def && d.tipo_def.id === d.tipo ? d.tipo_def : T.tipos.find((x) => x.id === d.tipo);
  if (!t) problemas.push(`tipo desconhecido: ${d.tipo}`);
  else {
    if (ficha?.capa?.molde !== t.capa.molde) problemas.push(`capa ${ficha?.capa?.molde} não é a do tipo ${t.id} (${t.capa.molde})`);
    if (ficha?.capa?.estilo !== t.capa.estilo) problemas.push(`estilo da capa ${ficha?.capa?.estilo} não é o do tipo (${t.capa.estilo})`);
    const seq = fs_.map((s) => s.molde).join(",");
    if (seq !== t.laminas.join(",")) problemas.push(`lâminas fora da ordem do tipo ${t.id}: veio [${seq}], o tipo é [${t.laminas.join(",")}]`);
    if (t.famoso) {
      if (!ficha?.capa?.famoso || !ficha?.capa?.fato) problemas.push("famoso sem nome ou sem fato na capa");
      if (!/fonte\s*:/i.test(String(pecas?.legenda ?? ""))) problemas.push("famoso sem \"Fonte:\" na legenda");
    }
  }
} else problemas.push("falta o tipo do post (tipos-dp.json)");
// pessoas das fotos (D-19): nada de jovem; personagem é mulher de 40 a 60, mãe ou avó
const prompts = [ficha?.capa?.foto_prompt, ficha?.capa?.foto_prompt2, ficha?.personagem, ...fs_.map((s) => s.foto_prompt)].filter(Boolean).join(" | ");
const jovem = prompts.match(/\b(young|teen\w*|adolescen\w*|student|college|20s|twenty|motoboy|delivery rider|groom|bride|boyfriend|girlfriend)\b/i);
const relig = prompts.match(/\b(church|bible|biblical|crucifix|rosary|praying|prayer|priest|pastor|saint|angel|jesus|god|religious|chapel|altar)\b/i);
const somb = prompts.match(/\b(skull|skeleton|demon\w*|devil|satan|grim reaper|reaper|zombie|vampire|ghost|monster|horror|creepy|haunted)\b/i);
if (somb) problemas.push(`foto sombria ("${somb[0]}"): o dono proibiu caveira, demônio e afins`);
if (relig) problemas.push(`foto com cena religiosa ("${relig[0]}"): D-21 proíbe religião`);
if (jovem) problemas.push(`foto com pessoa jovem ("${jovem[0]}"): use mulher de 40 a 60, mãe ou avó`);
if (fs_.some((s) => s.foto_fonte === "ia") || ficha?.capa?.foto_fonte === "ia") {
  if (!/\b(4\d|5\d|60|middle-aged|mother|grandmother|grandma|mãe|avó)\b/i.test(prompts) && !(ficha?.capa?.famoso)) problemas.push("as fotos não dizem a idade/papel da personagem (mulher de 40 a 60, mãe ou avó)");
}

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
