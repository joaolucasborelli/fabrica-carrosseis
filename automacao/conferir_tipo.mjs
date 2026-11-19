// Confere uma mudança de TIPO de post pedida pelo dono (botão "Tipos de post"). Grátis, sem API.
// Uso: node automacao/conferir_tipo.mjs caminho.json
// caminho.json = { "novo": {id, capa:{molde, estilo}, laminas:[...], famoso}, "presets": <config_fabrica.presets>, "reprovados": ["capa_caderno", ...] }
import fs from "node:fs";
const SEMPRE_PROIBIDOS = ["capa_caderno", "capa_marcatexto", "conta_visual", "esc_cards", "faixa_amarela", "foto_sticker"];
const ESTILOS = ["foto_real", "famoso", "famoso_composicao"];
const d = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const n = d.novo ?? {}, P = d.presets ?? {};
const proib = new Set([...SEMPRE_PROIBIDOS, ...(d.reprovados ?? []).map((x) => String(x).replace(/^tipo:/, ""))]);
const capas = new Set([...(P.capas?.usar ?? []), ...(P.capas?.talvez ?? [])].filter((m) => !proib.has(m)));
const lams = new Set([...(P.slides?.usar ?? []), ...(P.slides?.talvez ?? [])].filter((m) => !proib.has(m)));
const problemas = [];
if (!n.id) problemas.push("tipo sem id");
if (!capas.has(n.capa?.molde)) problemas.push(`capa ${n.capa?.molde} fora da lista aprovada`);
if (!ESTILOS.includes(n.capa?.estilo)) problemas.push(`estilo ${n.capa?.estilo} desconhecido`);
if (n.famoso && !String(n.capa?.estilo).startsWith("famoso")) problemas.push("tipo de famoso precisa de estilo famoso");
const L = n.laminas ?? [];
if (L.length < 4 || L.length > 9) problemas.push(`${L.length} lâminas (de 4 a 9, para dar no máximo 10 com a capa)`);
L.forEach((m, i) => { if (!lams.has(m)) problemas.push(`lâmina ${i + 2}: ${m} fora da lista aprovada`); });
if (L.length && !["cta_f6", "fecho_foto"].includes(L[L.length - 1])) problemas.push("a última lâmina precisa ser cta_f6 ou fecho_foto");
const r = { ok: problemas.length === 0, problemas, capas_aprovadas: [...capas], laminas_aprovadas: [...lams] };
console.log(JSON.stringify(r, null, 1));
process.exit(r.ok ? 0 : 1);
