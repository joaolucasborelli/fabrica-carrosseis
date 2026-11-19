// Vigias grátis do caminho "Pelo Claude" (D-17). Não chama nenhuma API.
// Uso: node automacao/vigias.mjs caminho/do/teste.json
// teste.json = { "base": { "n_slides": 11, "capa_texto": "...", "slides": ["..."] },
//               "post": { "capa": "...", "slides": ["..."], "legenda": "...", "pessoa_real": false, "pedido_fila": false } }
// pedido_fila: true quando o post termina com "comente FILA" (D-18, até 2 por dia).
// pessoa_real: true só para história real de famoso com fonte (D-16); aí não leva "história ilustrativa".
// Sai com {"ok":true|false,"problemas":[...],"avisos":[...]} e código 0 (ok) ou 1 (reprovado).
import fs from "node:fs";

// mesma lista da fábrica (app/backend/fabrica-index.ts, PROIBIDAS)
const PROIBIDAS = ["finanças", "financas", "orçamento", "orcamento", "fluxo de caixa", "educação financeira", "investimento", "investimentos", "planejamento financeiro", "fique rica", "riqueza", "prosperidade", "abundância", "mentalidade milionária", "liberdade financeira", "destravar", "limpe seu nome", "nome limpo garantido", "durma em paz", "10 minutos", "15 minutos", "você gasta demais", "gastadeira", "garantido", "garantida", "100%", "vai mudar sua vida", "2027 vai ser o seu ano", "só hoje", "últimas vagas", "corre", "nossas alunas", "vovozinha", "guerreira", "empodere-se", "mano", "rolê", "liso", "lisa", "planner", "mande seus dados", "cpf", "trampo", "arrasta pro lado"];

const escRe = (t) => t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const limpa = (s) => String(s ?? "").replace(/\*\*/g, " ").replace(/\[\[|\]\]/g, " ");
const palavras = (s) => limpa(s).split(/\s+/).filter((w) => /[\p{L}\p{N}]/u.test(w));
const norm = (s) => limpa(s).toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9\s]/g, " ").split(/\s+/).filter(Boolean);
const semAspas = (s) => String(s).replace(/["“][^"”]*["”]/g, " ").replace(/(^|\n)\s*[—-][^\n]*/g, " ");

const d = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const { base, post } = d;
const problemas = [], avisos = [];
const slides = (post.slides ?? []).map(String);
const ultima = slides[slides.length - 1] ?? "";
// o pedido "comente FILA" (D-18) não conta como texto da história
const PEDIDO = /comente\s+\*{0,2}FILA\*{0,2}[^\n]*/i;
const slidesConta = slides.map((s, i) => (i === slides.length - 1 ? s.replace(PEDIDO, "") : s));

// 1. capa
const nCapa = palavras(post.capa).length;
if (nCapa < 6 || nCapa > 10) problemas.push(`capa com ${nCapa} palavras (o certo é de 6 a 10)`);
if (/(?<!\p{L})eu(?!\p{L})/iu.test(semAspas(post.capa))) problemas.push(`capa com "eu"`);

// 2. tamanho (D-17)
const total = slides.length + 1;
// com tipo da DP (D-19/D-20) quem manda no tamanho é o tipo (até 10); sem tipo, nunca maior que a base (D-17)
const tetoLaminas = post.tipo ? 10 : Math.min(10, Number(base?.n_slides) || 10);
if (total > tetoLaminas) problemas.push(`${total} lâminas (máximo ${tetoLaminas}: até 10 e nunca maior que a base)`);
if (total < 5) problemas.push(`só ${total} lâminas`);
slidesConta.forEach((s, i) => { const n = palavras(s).length; if (n > 35) problemas.push(`lâmina ${i + 2} com ${n} palavras (máximo 35)`); });
const nTotal = nCapa + slidesConta.reduce((a, s) => a + palavras(s).length, 0);
if (nTotal > 180) problemas.push(`${nTotal} palavras no post (máximo 180)`);

// 3. palavras proibidas e pedido de comentário
const tudo = [post.capa, ...slides, post.legenda ?? ""].map(String).join("\n");
const achadas = PROIBIDAS.filter((t) => new RegExp(`(?<![\\p{L}\\p{N}])${escRe(t)}(?![\\p{L}\\p{N}])`, "iu").test(t === "você gasta demais" ? semAspas(tudo) : tudo));
if (achadas.length) problemas.push(`palavra proibida: ${achadas.join(", ")}`);
// D-18: só vale "comente FILA", e só na última lâmina
const semPedido = [post.capa, ...slides.slice(0, -1), ultima.replace(PEDIDO, ""), post.legenda ?? ""].map(String).join("\n");
if (/(?<!\p{L})(coment|digite|escreva)\p{L}*/iu.test(semPedido)) problemas.push(`pedido de comentário fora do "comente FILA" da última lâmina`);
if (post.pedido_fila === true && !PEDIDO.test(ultima)) problemas.push(`falta "comente FILA" na última lâmina`);
if (post.famoso === true && PEDIDO.test(ultima)) problemas.push(`post de famoso não leva "Comente FILA" (D-16: o famoso nunca vende)`);
if (post.pedido_fila !== true && PEDIDO.test(ultima)) problemas.push(`"comente FILA" sem pedido_fila: true (limite de 2 por dia)`);

// 4. "eu" de personagem nas lâminas (fala entre aspas ou travessão pode)
slides.forEach((s, i) => { if (/(?<!\p{L})eu(?!\p{L})/iu.test(semAspas(s))) problemas.push(`lâmina ${i + 2} com "eu" fora de fala`); });

// 5. cópia de frase da base: 6 palavras seguidas iguais
if (base) {
  const b = norm([base.capa_texto ?? "", ...(base.slides ?? []).map((x) => (typeof x === "string" ? x : (x?.texto ?? "")))].join(" "));
  const grams = new Set();
  for (let i = 0; i + 6 <= b.length; i++) grams.add(b.slice(i, i + 6).join(" "));
  const p = norm([post.capa, ...slides].join(" "));
  const copiadas = [];
  for (let i = 0; i + 6 <= p.length; i++) { const g = p.slice(i, i + 6).join(" "); if (grams.has(g)) copiadas.push(g); }
  if (copiadas.length) problemas.push(`6 palavras seguidas iguais à base: "${copiadas[0]}"`);
} else avisos.push("sem base para comparar a cópia de frase");

// 6. marca e coisas que vão para a legenda (D-17)
const lam = [post.capa, ...slides].join("\n");
if (/@|ahistoriaquemuda|siga (a|nossa) p[áa]gina/iu.test(lam)) problemas.push("marca ou \"siga\" dentro das lâminas");
if (/fila das contas|defensoria/iu.test(lam)) avisos.push("Fila das Contas ou Defensoria dentro das lâminas: só se o tema pedir");
// história real de famoso (D-16): não leva "história ilustrativa", mas precisa de fonte na legenda
if (post.pessoa_real === true) {
  if (!/fonte/i.test(String(post.legenda ?? ""))) problemas.push("história real de famoso sem fonte na legenda");
  if (/hist[óo]ria ilustrativa/i.test(lam)) problemas.push("história real não leva \"história ilustrativa\"");
} else {
  // D-18: a página se chama Histórias Ilustrativas; o aviso fica só na legenda
  if (/hist[óo]ria ilustrativa/i.test(lam)) problemas.push("\"história ilustrativa\" não vai nas lâminas (só na legenda)");
  if (!/ilustrativ/i.test(String(post.legenda ?? ""))) problemas.push("falta o aviso de história ilustrativa na legenda");
}

// 7. número sem fonte
if (/\d+([.,]\d+)?\s*%/.test(lam) && !/fonte/i.test(String(post.legenda ?? ""))) problemas.push("número em % sem fonte na legenda");

const r = { ok: problemas.length === 0, palavras: nTotal, laminas: total, problemas, avisos };
console.log(JSON.stringify(r, null, 1));
process.exit(r.ok ? 0 : 1);
