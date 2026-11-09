"""Moldes visuais da fábrica (F1, F2, F5, F6 do estudo dna_visual.md), em HTML/CSS para 1080x1350.

Cada slide é um dict: {"molde": "capa_f1" | "papel_f2" | "preto_f5" | "cta_f6", ...campos}
Marcação no texto: **palavra** = marca-texto amarelo; [[PALAVRA]] = carimbo da palavra do CTA.
"""
import html, re
from pathlib import Path

LOGO = (Path(__file__).resolve().parent / "assets" / "logo-horizontal.svg").as_uri()
HANDLE = "@ahistoriaquemuda"

FONTES = ("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900"
          "&family=Archivo+Black&family=Crimson+Pro:wght@400;600;700&family=Source+Sans+3:wght@400;600;700;800&display=block")

# trama de papel (feTurbulence) — 4% de contraste, como nos vencedores
PAPEL = ("data:image/svg+xml;utf8," +
         "<svg xmlns='http://www.w3.org/2000/svg' width='600' height='600'>"
         "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/>"
         "<feColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .55 0'/></filter>"
         "<rect width='100%' height='100%' filter='url(%23n)'/></svg>").replace("#", "%23").replace("%2523", "%23")

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1350px;background:#000}
.slide{width:1080px;height:1350px;position:relative;overflow:hidden;-webkit-font-smoothing:antialiased}
.handle{position:absolute;left:0;right:0;top:1268px;text-align:center;font:500 23px/1 'Inter',sans-serif;letter-spacing:.01em}
mark{background:#FFD21F;color:#111;padding:0 .12em;margin:0 -.04em;-webkit-box-decoration-break:clone;box-decoration-break:clone}
.fit{overflow:hidden}

/* F1 · foto em cima, manchete branca no bloco preto */
.f1{background:#0b0b0b}
.f1 .foto{position:absolute;left:0;top:0;width:1080px;height:920px;object-fit:cover;object-position:var(--foco,50% 60%);filter:contrast(1.04) saturate(.92);
  -webkit-mask-image:linear-gradient(to bottom,#000 0,#000 560px,rgba(0,0,0,.82) 680px,rgba(0,0,0,.35) 800px,transparent 900px);
          mask-image:linear-gradient(to bottom,#000 0,#000 560px,rgba(0,0,0,.82) 680px,rgba(0,0,0,.35) 800px,transparent 900px)}
.f1 .degrade{position:absolute;left:0;right:0;top:0;height:920px;background:linear-gradient(to bottom,rgba(11,11,11,.18) 0,rgba(11,11,11,0) 160px,rgba(11,11,11,0) 600px,rgba(11,11,11,.55) 800px,#0b0b0b 920px)}
.f1 .grao{position:absolute;inset:0;background-image:url("__PAPEL__");opacity:.10;mix-blend-mode:overlay}
.f1 .texto{position:absolute;left:66px;right:66px;top:870px;height:360px;display:flex;align-items:center;justify-content:center}
.f1 .texto p{font:700 66px/1.12 'Inter',sans-serif;letter-spacing:-.012em;color:#fff;text-align:center;text-wrap:balance}
.f1 .handle{color:#8C8C8C}

/* F2 · papel claro com texto corrido (o miolo que mais separa vencedor do resto) */
.f2{background:#F1F0EC}
.f2::before{content:"";position:absolute;inset:0;background-image:url("__PAPEL__");opacity:.07;mix-blend-mode:multiply}
.f2 .texto{position:absolute;left:84px;right:84px;top:150px;bottom:150px;display:flex;flex-direction:column;justify-content:center}
.f2 .texto p{font:700 50px/1.2 'Inter',sans-serif;letter-spacing:-.018em;color:#141414}
.f2 .texto p+p{margin-top:.95em}
.f2 .handle{color:#8E8E8E}

/* F5 · frase em fundo preto (slide da marca) */
.f5{background:#111}
.f5::before{content:"";position:absolute;inset:0;background-image:url("__PAPEL__");opacity:.06;mix-blend-mode:screen}
.f5 .rotulo{font:800 30px/1 'Inter',sans-serif;letter-spacing:.14em;text-transform:uppercase;color:#FFD21F;margin-bottom:44px}
.f5 .texto{position:absolute;left:96px;right:96px;top:150px;bottom:150px;display:flex;flex-direction:column;justify-content:center}
.f5 .texto p{font:700 54px/1.22 'Inter',sans-serif;letter-spacing:-.015em;color:#F5F5F0}
.f5 .texto p+p{margin-top:.8em}
.f5 .handle{color:#8A8F96}

/* F6 · CTA da palavra (oferta disfarçada) em papel preto, PALAVRA em amarelo com carimbo */
.f6{background:#111}
.f6::before{content:"";position:absolute;inset:0;background-image:url("__PAPEL__");opacity:.07;mix-blend-mode:screen}
.f6 .moldura{position:absolute;inset:34px;border:2px solid rgba(245,245,240,.16)}
.f6 .texto{position:absolute;left:110px;right:110px;top:170px;bottom:300px;display:flex;flex-direction:column;justify-content:center}
.f6 .texto p{font:400 60px/1.25 'Crimson Pro',serif;color:#F5F5F0}
.f6 .texto p.pergunta{font-weight:600;font-size:66px;margin-bottom:.7em}
.f6 .carimbo{display:inline-block;font:400 1.55em/1 'Archivo Black',sans-serif;color:#FFD21F;border:5px solid #FFD21F;padding:.12em .28em .08em;margin:.18em .1em .1em 0;transform:rotate(-2.2deg);letter-spacing:.02em;filter:url(#aspero)}
.f6 .siga{position:absolute;left:110px;bottom:150px;font:600 34px/1 'Source Sans 3',sans-serif;color:#8A8F96}
.f6 .logo{position:absolute;right:76px;bottom:118px;width:230px}
"""

FIT_JS = """
(() => {
  for (const box of document.querySelectorAll('.fit')) {
    const ps = box.querySelectorAll('p');
    // texto curto: cresce até o teto do molde (data-max), sem passar da caixa
    const max = parseFloat(box.dataset.max || 0);
    const altura = () => { const k = box.children; return k[k.length-1].getBoundingClientRect().bottom - k[0].getBoundingClientRect().top; };
    let g = 0;
    while (max && g++ < 40) {
      const fs = parseFloat(getComputedStyle(ps[0]).fontSize);
      if (fs >= max || altura() > box.clientHeight * 0.55) break;
      ps.forEach(p => { const f = parseFloat(getComputedStyle(p).fontSize); p.style.fontSize = Math.min(f * 1.04, max * f / fs) + 'px'; });
    }
    let guard = 0;
    while (box.scrollHeight > box.clientHeight + 1 && guard++ < 60) {
      ps.forEach(p => { const fs = parseFloat(getComputedStyle(p).fontSize); p.style.fontSize = (fs * 0.97) + 'px'; });
    }
    box.dataset.encolheu = guard;
  }
})();
"""

SVG_FILTROS = """<svg width="0" height="0" style="position:absolute"><filter id="aspero">
<feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" result="t"/>
<feDisplacementMap in="SourceGraphic" in2="t" scale="3"/></filter></svg>"""


def marcar(txt: str) -> str:
    t = html.escape(txt, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<mark>\1</mark>", t)
    t = re.sub(r"\[\[(.+?)\]\]", r'<span class="carimbo">\1</span>', t)
    return t


def paras(ps, cls=""):
    c = f' class="{cls}"' if cls else ""
    return "".join(f"<p{c}>{marcar(p)}</p>" for p in ps)


def _normalizar(s: dict) -> dict:
    s = dict(s)
    ps = [p for p in (s.get("paragrafos") or []) if p and p.strip()]
    if not ps and s.get("texto") and s["molde"] != "capa_f1":
        ps = [p.strip() for p in re.split(r"\n\s*\n|\n", s["texto"]) if p.strip()]
    s["paragrafos"] = ps
    if s["molde"] == "capa_f1" and not s.get("texto"):
        s["texto"] = " ".join(ps)
    return s


def slide_html(s: dict) -> str:
    s = _normalizar(s)
    m = s["molde"]
    if m == "capa_f1":
        foco = html.escape(s.get("foco") or "50% 60%")
        corpo = (f'<div class="slide f1"><img class="foto" src="{s["foto"]}" style="--foco:{foco}"><div class="degrade"></div><div class="grao"></div>'
                 f'<div class="texto fit"><p>{marcar(s["texto"])}</p></div><div class="handle">{HANDLE}</div></div>')
    elif m == "papel_f2":
        corpo = f'<div class="slide f2"><div class="texto fit" data-max="62">{paras(s["paragrafos"])}</div><div class="handle">{HANDLE}</div></div>'
    elif m == "preto_f5":
        rot = f'<div class="rotulo">{html.escape(s["rotulo"])}</div>' if s.get("rotulo") else ""
        corpo = f'<div class="slide f5"><div class="texto fit" data-max="64">{rot}{paras(s["paragrafos"])}</div><div class="handle">{HANDLE}</div></div>'
    elif m == "cta_f6":
        perg = f'<p class="pergunta">{marcar(s["pergunta"])}</p>' if s.get("pergunta") else ""
        corpo = (f'<div class="slide f6"><div class="moldura"></div><div class="texto fit">{perg}{paras(s["paragrafos"])}</div>'
                 f'<div class="siga">Siga {HANDLE}</div><img class="logo" src="{LOGO}"></div>')
    else:
        raise ValueError(m)
    css = CSS.replace("__PAPEL__", PAPEL)
    return (f'<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{FONTES}">'
            f"<style>{css}</style></head><body>{SVG_FILTROS}{corpo}</body></html>")
