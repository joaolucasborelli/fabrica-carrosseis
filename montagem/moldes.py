"""Moldes visuais da fábrica (F1, F2, F5, F6 do estudo dna_visual.md), em HTML/CSS para 1080x1350.

Cada slide é um dict: {"molde": "capa_f1" | "papel_f2" | "preto_f5" | "cta_f6", ...campos}
Marcação no texto: **palavra** = marca-texto amarelo; [[PALAVRA]] = carimbo da palavra do CTA.
"""
import html, re
from pathlib import Path

# D-22 (19/11/2026): identidade "Café com as Contas" da DP (nome: Contas da casa)
LOGO = (Path(__file__).resolve().parent / "assets" / "cafe-horizontal.svg").as_uri()
AVATAR = (Path(__file__).resolve().parent / "assets" / "cafe-perfil.png").as_uri()
HANDLE = "@contasdacasaaa1"  # 24/11: conta nova criada pelo dono (antes @ahistoriaquemuda)
NOME = "Contas da casa"  # 20/11: o dono tirou "Histórias Ilustrativas" do nome
_PADRAO = (LOGO, AVATAR, HANDLE, NOME)
DP_TEMA_BASE = {"fundo": "#2A211C", "destaque": "#E3A845", "claro": "#F7F1E6", "fonte_titulo": "Lexend", "fonte_texto": "Lexend",
                "sem_caixa_alta": True, "aviso": "nunca pedimos senha nem Pix"}


TEMA = None  # cores e fontes do ambiente; a DP usa DP_TEMA (definido logo abaixo de tema_seguro)


def _rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _hex(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(v))) for v in rgb)


def _mistura(a, b, t):
    ra, rb = _rgb(a), _rgb(b)
    return _hex(tuple(ra[i] + (rb[i] - ra[i]) * t for i in range(3)))


def _lum(h):
    def c(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = _rgb(h)
    return 0.2126 * c(r) + 0.7152 * c(g) + 0.0722 * c(b)


def contraste(a, b):
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def tema_seguro(t):
    """Garante leitura: fundo escuro, destaque que aparece no fundo, papel claro. Ajusta as cores da marca só o necessário."""
    if not t:
        return None
    try:
        f = t.get("fundo") or "#111111"
        d = t.get("destaque") or "#FFD21F"
        c = t.get("claro") or "#F5F5F0"
        k = 0
        while _lum(f) > 0.03 and k < 20:  # fundo precisa ser bem escuro (o texto branco vai em cima)
            f = _mistura(f, "#000000", 0.15); k += 1
        k = 0
        while contraste(d, f) < 4.5 and k < 20:  # destaque tem que aparecer no fundo
            d = _mistura(d, "#ffffff", 0.12); k += 1
        k = 0
        while _lum(c) < 0.75 and k < 20:  # papel claro (texto escuro em cima)
            c = _mistura(c, "#ffffff", 0.15); k += 1
        tx = f if contraste(f, d) >= 4.5 else "#111111"  # texto em cima do destaque
        return {**t, "fundo": f, "destaque": d, "claro": c, "texto_destaque": tx}
    except Exception:
        return None


DP_TEMA = None  # preenchido logo abaixo


DP_AVISO = "nunca pedimos senha nem Pix"
DP_ATIVA = True  # 23/11: o dono quer os posts da DP no preto e amarelo de antes (sem o tema café); fica só o aviso


def _tematizar(doc):
    """Troca as cores e fontes da Do outro lado da Porta pelas do ambiente, por papel."""
    t = TEMA
    if not t:
        if DP_ATIVA and DP_AVISO:  # rodapé contra golpe, no visual preto e amarelo
            css = (f'.handle::after,.assin::after,.rod::after{{content:" · {DP_AVISO}";font-weight:500;opacity:.85;white-space:nowrap}}'
                   '.assin::after{font-size:.78em;margin-left:-8px}')
            doc = doc.replace("</head>", f"<style>{css}</style></head>", 1)
        return doc
    import re as _re
    d, f, c, tx = t["destaque"], t["fundo"], t["claro"], t["texto_destaque"]
    rd = ",".join(str(v) for v in _rgb(d)); rf = ",".join(str(v) for v in _rgb(f))
    for a, b in (("#FFD21F", d), ("#ffd21f", d), ("255,210,31", rd), ("11,11,11", rf),
                 ("#F5F5F0", c), ("#F3EEDC", c), ("#f7f4ec", c), ("#f2f2ef", c),
                 ("#0b0b0b", f), ("#0c0c0d", f), ("#0b0b0c", f), ("#141416", _mistura(f, "#ffffff", 0.05)),
                 ("#1b1b1b", _mistura(f, "#ffffff", 0.08))):
        doc = doc.replace(a, b)
    doc = _re.sub(r"#111(?![0-9A-Fa-f])", tx, doc)
    doc = _re.sub(r"#000(?![0-9A-Fa-f])", f, doc)
    ft, fx = t.get("fonte_titulo"), t.get("fonte_texto")
    extra = ""
    if ft:
        for a in ("'Archivo Black'", "'Bebas Neue'", "'Barlow Condensed'", "'Archivo'"):
            doc = doc.replace(a, f"'{ft}'")
        extra += "&family=" + ft.replace(" ", "+") + ":wght@400;600;700;800;900"
    if fx:
        doc = doc.replace("'Inter'", f"'{fx}'")
        extra += "&family=" + fx.replace(" ", "+") + ":wght@400;500;600;700;800"
    if extra:
        doc = doc.replace("&display=block", extra + "&display=block", 1)
    css = ""
    if t.get("sem_caixa_alta"):  # D-22: título grande sem tudo em maiúscula
        css += "*{text-transform:none!important}"
    if t.get("aviso"):  # rodapé: aviso contra golpe
        av = t["aviso"].replace('"', "")
        css += f'.handle::after,.assin::after,.rod::after{{content:" · {av}";font-weight:500;opacity:.85;white-space:nowrap}}.assin::after{{font-size:.78em;margin-left:-8px}}'
    if t.get("sem_caixa_alta") and fx:  # D-22: uma família de letra só (Lexend) em todas as peças
        for a in ("'Crimson Pro'", "'Bitter'", "'Source Sans 3'", "'Space Mono'"):
            doc = doc.replace(a, f"'{fx}'")
    if css:
        doc = doc.replace("</head>", f"<style>{css}</style></head>", 1)
    return doc


DP_TEMA = None  # 23/11: volta o preto e amarelo (o tema café de D-22 fica guardado em DP_TEMA_BASE, sem uso)
TEMA = DP_TEMA  # padrão = DP


def usar_marca(marca=None):
    """Cada ambiente desenha com a própria marca. Sem marca (ou o ambiente 1) volta para a Do outro lado da Porta."""
    global LOGO, AVATAR, HANDLE, NOME, TEMA, PERFIL, DP_ATIVA
    import base64 as _b64, html as _h
    if not marca or not marca.get("nome") or marca.get("ambiente_id") in (None, 1):
        LOGO, AVATAR, HANDLE, NOME = _PADRAO
        TEMA = DP_TEMA; PERFIL = None; DP_ATIVA = True  # 23/11: preto e amarelo de antes
        return
    DP_ATIVA = False
    PERFIL = marca.get("perfil") or None
    TEMA = tema_seguro(marca.get("tema"))
    NOME = marca["nome"]
    HANDLE = marca.get("handle") or ""
    sigla = (marca.get("sigla") or "".join(w[0] for w in NOME.split()[:2])).upper()[:3]
    cor = (TEMA or {}).get("destaque") or marca.get("cor") or "#FFD21F"
    av = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="50" fill="{cor}"/>'
          f'<text x="50" y="62" font-family="Inter,Arial" font-weight="800" font-size="36" text-anchor="middle" fill="#111">{_h.escape(sigla)}</text></svg>')
    lg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 80"><text x="0" y="58" font-family="Inter,Arial" font-weight="800" font-size="52" fill="#fff">'
          f'{_h.escape(NOME)}</text></svg>')
    AVATAR = "data:image/svg+xml;base64," + _b64.b64encode(av.encode()).decode()
    LOGO = "data:image/svg+xml;base64," + _b64.b64encode(lg.encode()).decode()
    # logo de verdade da marca (baixado do site pelo coletor): vira o avatar redondo
    if marca.get("logo_arquivo"):
        try:
            from pathlib import Path as _P
            from PIL import Image as _I
            import io as _io
            im = _I.open(marca["logo_arquivo"]).convert("RGBA"); im.thumbnail((180, 180))
            fundo = _I.new("RGBA", (220, 220), (255, 255, 255, 255)); fundo.paste(im, ((220 - im.width) // 2, (220 - im.height) // 2), im)
            buf = _io.BytesIO(); fundo.save(buf, "PNG")
            AVATAR = "data:image/png;base64," + _b64.b64encode(buf.getvalue()).decode()
        except Exception:
            pass

# D-22 (20/11): o emblema é o logo 6 (óculos mostarda sobre a conta, ao lado do café)
PORTA = ('<svg class="emblema" viewBox="0 0 200 200" aria-hidden="true">'
         '<image x="0" y="0" width="200" height="200" href="data:image/png;base64,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"/></svg>')

FONTES = ("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Bebas+Neue&family=Barlow+Condensed:wght@500;600;700"
          "&family=Archivo:wdth,wght@62..125,500..900&family=Bitter:wght@400;600"
          "&family=Archivo+Black&family=Space+Mono:wght@400;700&family=Crimson+Pro:wght@400;600;700&family=Source+Sans+3:wght@400;600;700;800&display=block")

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

/* F1b · portal: foto em cima, divisor com emblema, manchete em caixa alta condensada com palavras amarelas */
.f1b{background:#0b0b0b}
.f1b .foto{position:absolute;left:0;top:0;width:1080px;height:1000px;object-fit:cover;object-position:var(--foco,50% 50%);filter:contrast(1.04) saturate(.95);
  -webkit-mask-image:linear-gradient(to bottom,#000 0,#000 640px,rgba(0,0,0,.6) 820px,transparent 990px);mask-image:linear-gradient(to bottom,#000 0,#000 640px,rgba(0,0,0,.6) 820px,transparent 990px)}
.f1b .grao{position:absolute;inset:0;background-image:url("__PAPEL__");opacity:.10;mix-blend-mode:overlay}
.f1b .divisor{position:absolute;left:150px;right:150px;top:968px;height:64px;display:flex;align-items:center;gap:26px}
.f1b .divisor i{flex:1;height:2px;background:rgba(255,255,255,.7)}
.f1b .emblema{width:34px;height:64px}
.f1b .texto{position:absolute;left:70px;right:70px;top:1050px;height:236px;display:flex;align-items:center;justify-content:center}
.f1b .texto p{font:400 104px/.98 'Bebas Neue',sans-serif;letter-spacing:.005em;color:#fff;text-align:center;text-transform:uppercase;text-wrap:balance}
.f1b .texto p .am{color:#FFD21F}
.f1b .seta{position:absolute;right:46px;top:46px;width:54px;height:54px;border-radius:50%;background:rgba(255,255,255,.92);display:flex;align-items:center;justify-content:center}
.f1b .seta svg{width:26px;height:26px}

/* Perfil · portal com o nosso perfil no divisor (estilo das páginas de IA que o dono mandou) */
.perfil{background:#0b0b0b}
.perfil .foto{position:absolute;left:0;top:0;width:1080px;height:960px;object-fit:cover;object-position:var(--foco,50% 40%);filter:contrast(1.04) saturate(.96);
  -webkit-mask-image:linear-gradient(to bottom,#000 0,#000 640px,rgba(0,0,0,.55) 820px,transparent 950px);mask-image:linear-gradient(to bottom,#000 0,#000 640px,rgba(0,0,0,.55) 820px,transparent 950px)}
.perfil .grao{position:absolute;inset:0;background-image:url("__PAPEL__");opacity:.08;mix-blend-mode:overlay}
.perfil .divisor{position:absolute;left:60px;right:60px;top:880px;height:76px;display:flex;align-items:center;gap:22px}
.perfil .divisor i{flex:1;height:2px;background:rgba(255,255,255,.55)}
.perfil .chip{display:flex;align-items:center;gap:14px}
.perfil .chip img{width:66px;height:66px;border-radius:50%;border:2px solid rgba(255,255,255,.85)}
.perfil .chip b{display:block;font:700 27px/1.1 'Inter',sans-serif;color:#fff}
.perfil .chip span{display:block;font:400 21px/1.2 'Inter',sans-serif;color:#a6a9ae}
.perfil .texto{position:absolute;left:56px;right:56px;top:976px;height:310px;display:flex;align-items:center;justify-content:center}
.perfil .texto p{font:400 92px/.98 'Bebas Neue',sans-serif;color:#fff;text-align:center;text-transform:uppercase;text-wrap:balance}
.perfil .texto p .am{color:#FFD21F}

/* Comparação · foto cortada ao meio (antes x depois), rótulos e manchete no preto */
.comp{background:#0b0b0b}
.comp .foto{position:absolute;left:0;top:0;width:1080px;height:880px;object-fit:cover;object-position:var(--foco,50% 45%);filter:contrast(1.04) saturate(.95);
  -webkit-mask-image:linear-gradient(to bottom,#000 0,#000 700px,transparent 875px);mask-image:linear-gradient(to bottom,#000 0,#000 700px,transparent 875px)}
.comp .corte{position:absolute;left:537px;top:0;width:6px;height:800px;background:#0b0b0b}
.comp .rot{position:absolute;top:48px;font:700 34px/1 'Barlow Condensed',sans-serif;letter-spacing:.06em;text-transform:uppercase;padding:12px 20px 10px;border-radius:8px}
.comp .rot.e{left:44px;background:rgba(17,17,17,.88);color:#F5F5F0}
.comp .rot.d{right:44px;background:#FFD21F;color:#111}
.comp .texto{position:absolute;left:66px;right:66px;top:850px;height:390px;display:flex;align-items:center;justify-content:center}
.comp .texto p{font:700 66px/1.12 'Inter',sans-serif;letter-spacing:-.012em;color:#fff;text-align:center;text-wrap:balance}
.comp .handle{color:#8C8C8C}

/* Tweet · print de post da NOSSA conta (sem selo de verificado) com foto embaixo */
.tw{background:#fff}
.tw .topo{position:absolute;left:84px;top:96px;display:flex;align-items:center;gap:26px}
.tw .topo img{width:128px;height:128px;border-radius:50%}
.tw .topo b{display:block;font:800 46px/1.1 'Inter',sans-serif;color:#0f1419}
.tw .topo span{display:block;font:400 34px/1.3 'Inter',sans-serif;color:#536471}
.tw .texto{position:absolute;left:84px;right:84px;top:280px;height:430px;display:flex;flex-direction:column;justify-content:center}
.tw .texto p{font:400 58px/1.24 'Inter',sans-serif;color:#0f1419;letter-spacing:-.01em}
.tw .texto p+p{margin-top:.6em}
.tw .texto mark{background:none;color:#0f1419;font-weight:800;padding:0;margin:0}
.tw .img{position:absolute;left:84px;right:84px;top:740px;height:520px;border-radius:30px;overflow:hidden;border:1px solid #e6e9ec}
.tw .img img{width:100%;height:100%;object-fit:cover;object-position:var(--foco,50% 45%)}

/* ESCURO · miolos estilo páginas grandes de IA/negócio: fundo preto com grade de pontos, título condensado com palavra em destaque,
   moldura com brilho, cards numerados, checklist, rede de rostos, rodapé ——— @handle ——— */
.esc{background:#0c0c0d}
.esc::before{content:"";position:absolute;inset:0;background-image:radial-gradient(rgba(255,255,255,.075) 1.6px,transparent 1.7px);background-size:22px 22px}
.esc::after{content:"";position:absolute;inset:0;background:radial-gradient(ellipse at 50% 40%,rgba(255,210,31,.05),transparent 60%)}
.esc>*{position:relative;z-index:1}
.esc .rod{position:absolute;left:56px;right:56px;bottom:62px;display:flex;align-items:center;gap:22px;font:500 30px/1 'Inter',sans-serif;color:#e9e9e6}
.esc .rod i{flex:1;height:2px;background:rgba(255,255,255,.75)}
.esc .tit{position:absolute;left:60px;right:60px;text-align:center;font:400 112px/.95 'Bebas Neue',sans-serif;color:#fff;text-transform:uppercase}
.esc .tit .am,.esc .am{color:#FFD21F}
.esc .sub{position:absolute;left:60px;right:60px;text-align:center;font:400 40px/1.3 'Inter',sans-serif;color:#e6e6e3}
.esc .moldura{position:absolute;border:4px solid #FFD21F;border-radius:30px;overflow:hidden;box-shadow:0 0 34px rgba(255,210,31,.45),0 0 4px rgba(255,210,31,.9)}
.esc .moldura img{width:100%;height:100%;object-fit:cover;object-position:var(--foco,50% 40%);display:block}
/* título + moldura + legenda */
.esc.tm .tit{top:250px}
.esc.tm .moldura{left:72px;right:72px;top:420px;height:440px}
.esc.tm .sub{top:900px;height:280px}
/* cards numerados */
.esc.cd .tit{top:120px;font-size:96px}
.esc.cd .sub{top:232px;font-size:34px;color:#cfcfcb}
.esc.cd .cards{position:absolute;left:52px;right:52px;top:350px;bottom:150px;display:flex;flex-direction:column;justify-content:center;gap:20px}
.esc.cd .card{position:relative;flex:1 1 0;max-height:205px;min-height:118px;display:flex;align-items:center;gap:28px;padding:20px 36px 20px 30px;overflow:hidden;
  background:linear-gradient(180deg,#1b1c21,#121215);border:1.5px solid #2e2f36;border-radius:28px;box-shadow:0 16px 36px rgba(0,0,0,.45),inset 0 1px 0 rgba(255,255,255,.06)}
.esc.cd .card::before{content:"";position:absolute;left:0;top:22px;bottom:22px;width:6px;border-radius:0 6px 6px 0;background:#FFD21F;box-shadow:0 0 18px rgba(255,210,31,.7)}
.esc.cd .card .n{flex:none;width:90px;height:90px;border-radius:24px;background:rgba(255,210,31,.1);border:2px solid rgba(255,210,31,.55);display:flex;align-items:center;justify-content:center;padding-top:6px;font:400 60px/1 'Bebas Neue',sans-serif;color:#FFD21F}
.esc.cd .card .ic{width:90px;height:90px;border-radius:22px;object-fit:cover;flex:none}
.esc.cd .card b{font:800 40px/1.12 'Inter',sans-serif;color:#fff;flex:0 0 270px}
.esc.cd .card span{flex:1;border-left:2px solid #35363d;padding-left:28px;font:400 32px/1.3 'Inter',sans-serif;color:#d9d9d5}
.esc.cd .card span mark,.esc.cd .card b mark{background:#FFD21F;color:#111;padding:0 .1em}
/* checklist + foto */
.esc.ck .tit{top:110px;font-size:112px}
.esc.ck .sub{top:232px;font-weight:700;color:#fff}
.esc.ck .sub u{text-decoration:none;border-bottom:3px solid #FFD21F;padding-bottom:6px}
.esc.ck .corpo{position:absolute;left:60px;right:60px;top:320px;bottom:150px;display:flex;flex-direction:column;gap:44px}
.esc.ck .itens{display:flex;flex-direction:column;gap:16px}
.esc.ck .corpo .moldura{position:relative;left:auto;right:auto;top:auto;height:auto;flex:1;min-height:380px}
.esc.ck .it{display:flex;align-items:center;gap:22px;padding:16px 26px 16px 18px;background:linear-gradient(180deg,#1a1b20,#131316);border:1.5px solid #2c2d34;border-radius:20px;font:500 37px/1.25 'Inter',sans-serif;color:#f2f2ef;box-shadow:0 10px 24px rgba(0,0,0,.35)}
.esc.ck .it::before{content:"✓";flex:none;width:50px;height:50px;border-radius:50%;background:#FFD21F;color:#111;font:900 30px/50px 'Inter',sans-serif;text-align:center;box-shadow:0 0 18px rgba(255,210,31,.5)}
.esc.ck .moldura{left:60px;right:60px;top:640px;height:510px}
/* rede de rostos */
.esc.rd .tit{top:70px;font-size:104px}
.esc.rd .lista{position:absolute;left:56px;right:56px;top:190px;display:flex;flex-direction:column;gap:14px}
.esc.rd .lista div{background:#141416;border:2px solid #2a2a2e;border-radius:18px;padding:14px 24px;font:400 30px/1.3 'Inter',sans-serif;color:#eee}
.esc.rd .lista b{color:#FFD21F;font:400 44px/1 'Bebas Neue',sans-serif;margin-right:14px}
.esc.rd .rede{position:absolute;left:0;right:0;top:500px;height:560px}
.esc.rd .rede svg{position:absolute;inset:0}
.esc.rd .no{position:absolute;width:150px;text-align:center;transform:translate(-50%,-50%)}
.esc.rd .no img{width:118px;height:118px;border-radius:50%;object-fit:cover;border:4px solid #FFD21F;box-shadow:0 0 22px rgba(255,210,31,.5);background:#222}
.esc.rd .no b{display:block;font:700 25px/1.15 'Inter',sans-serif;color:#fff;margin-top:6px;text-shadow:0 2px 6px #000}
.esc.rd .no span{display:block;font:400 21px/1.2 'Inter',sans-serif;color:#c9c9c4;text-shadow:0 2px 6px #000}
.esc.rd .centro{position:absolute;left:540px;top:280px;width:120px;height:120px;transform:translate(-50%,-50%);border-radius:50%;background:#141416;border:4px solid #FFD21F;display:flex;align-items:center;justify-content:center;font:400 48px/1 'Bebas Neue',sans-serif;color:#FFD21F;text-align:center;box-shadow:0 0 30px rgba(255,210,31,.45)}
.esc.rd .caixa{position:absolute;left:56px;right:56px;bottom:140px;border:3px solid #FFD21F;border-radius:20px;padding:18px;text-align:center;font:700 40px/1.2 'Inter',sans-serif;color:#fff;background:rgba(20,20,22,.9)}

/* Tweet com 2 fotos lado a lado (capa ou miolo) */
.tw2 .img{display:none}
.tw2 .duas{position:absolute;left:58px;right:58px;top:690px;height:560px;display:flex;gap:22px}
.tw2 .duas img{flex:1;min-width:0;height:100%;object-fit:cover;border-radius:26px;border:1px solid #e6e9ec}

/* ===== KIT 2 (catálogo de 60 formatos, 09/11) ===== */
.cond{font-family:'Archivo',sans-serif;font-weight:900;font-stretch:62%;text-transform:uppercase;line-height:.92}
.assin{position:absolute;left:62px;right:62px;bottom:52px;display:flex;align-items:center;gap:18px;font:600 24px/1 'Inter',sans-serif;color:#F5F5F0}
.assin::before,.assin::after{content:"";flex:1;height:2px;background:currentColor;opacity:.8}
.assin img{width:46px;height:46px;border-radius:50%}
/* capa · rostos em círculo */
.circ{background:#0b0b0b}
.circ .foto{position:absolute;inset:0 0 auto 0;width:1080px;height:980px;object-fit:cover;object-position:var(--foco,50% 35%);
  -webkit-mask-image:linear-gradient(#000 0,#000 640px,transparent 960px);mask-image:linear-gradient(#000 0,#000 640px,transparent 960px)}
.circ .bolas{position:absolute;right:56px;top:60px;display:flex;flex-direction:column;gap:22px}
.circ .bolas img{width:300px;height:300px;border-radius:50%;object-fit:cover;border:7px solid #fff;box-shadow:0 10px 34px rgba(0,0,0,.55)}
.circ .texto{position:absolute;left:62px;right:62px;top:900px;height:330px;display:flex;align-items:center;justify-content:center}
.circ .texto p{font:400 104px/.96 'Bebas Neue',sans-serif;color:#fff;text-align:center;text-transform:uppercase;text-wrap:balance}
.circ .texto .am{color:#FFD21F}
/* capa · marca-texto amarelo sobre foto */
.mt{background:#0a0a0a}
.mt .foto{position:absolute;inset:0;width:1080px;height:1350px;object-fit:cover;object-position:var(--foco,50% 40%)}
.mt .sombra{position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,10,10,.15) 0,transparent 30%,transparent 42%,#0A0A0A 80%)}
.mt .logo{position:absolute;left:70px;top:64px;width:210px}
.mt .texto{position:absolute;left:84px;right:84px;top:700px;height:420px;display:flex;flex-direction:column;justify-content:flex-end}
.mt .texto p{font:600 70px/1.2 'Inter',sans-serif;color:#111;letter-spacing:-.01em}
.mt .texto p span.l{background:#FFD21F;padding:2px 12px;-webkit-box-decoration-break:clone;box-decoration-break:clone}
.mt .sub{position:absolute;left:84px;right:84px;top:1150px;font:700 38px/1.25 'Inter',sans-serif;color:#F5F5F0}
/* capa · revista cor chapada + objeto */
.rv{background:var(--bg,#F3EEDC);color:var(--tx,#111)}
.rv .tit{position:absolute;left:52px;right:52px;top:70px;font-size:150px;color:var(--tx,#111)}
.rv .tit u{text-decoration:none;border-bottom:8px solid #FFD21F}
.rv .corpo{position:absolute;left:56px;width:560px;top:var(--ty,640px);bottom:150px;display:flex;flex-direction:column;justify-content:center}
.rv .corpo p{font:500 46px/1.18 'Inter',sans-serif;color:var(--tx,#111)}
.rv .corpo p+p{margin-top:.6em}
.rv .corpo mark{background:#111;color:#F3EEDC;padding:0 .14em}
.rv .obj{position:absolute;right:20px;bottom:120px;width:470px;height:720px;object-fit:contain;mix-blend-mode:multiply}
.rv.escuro .obj{mix-blend-mode:normal;border-radius:24px}
.rv .rodape{position:absolute;left:56px;bottom:56px;font:700 24px/1 'Inter',sans-serif;letter-spacing:.06em;text-transform:uppercase;color:var(--tx,#111)}
/* capa · número gigante */
.ng{background:#0b0b0b}
.ng .foto{position:absolute;inset:0;width:1080px;height:1350px;object-fit:cover;object-position:var(--foco,50% 45%);filter:brightness(.45) saturate(.9)}
.ng .num{position:absolute;left:30px;right:30px;top:300px;text-align:center;color:#FFD21F;font-size:270px;text-shadow:0 8px 40px rgba(0,0,0,.6)}
.ng .num small{display:block;font-size:110px;color:#F5F5F0;margin-top:10px}
.ng .faixa{position:absolute;left:0;right:0;top:860px;display:flex;justify-content:center}
.ng .faixa span{background:#FFD21F;color:#111;font:800 34px/1.25 'Inter',sans-serif;text-transform:uppercase;letter-spacing:.02em;padding:12px 22px;max-width:900px;text-align:center}
.ng .texto{position:absolute;left:84px;right:84px;top:990px;font:600 44px/1.25 'Inter',sans-serif;color:#F5F5F0;text-align:center}
/* capa · caderno com faixa */
.cad{background:#2a2621}
.cad .foto{position:absolute;inset:-12px;width:1104px;height:1374px;object-fit:cover;filter:blur(1.6px) brightness(.92)}
.cad .faixa{position:absolute;left:0;right:0;top:var(--fy,430px);min-height:430px;background:rgba(17,17,17,.93);display:flex;align-items:center;padding:50px 74px}
.cad .faixa p{font:400 58px/1.45 'Bitter',serif;color:#F5F5F0}
.cad .faixa p .am{color:#FFD21F;font-weight:600}
.cad .handle{color:#F5F5F0;opacity:.85}
/* miolo · F1 corrido */
.fc{background:#000}
.fc .foto{position:absolute;inset:0 0 auto 0;width:1080px;height:780px;object-fit:cover;object-position:var(--foco,50% 40%);
  -webkit-mask-image:linear-gradient(#000 0,#000 600px,transparent 770px);mask-image:linear-gradient(#000 0,#000 600px,transparent 770px)}
.fc .texto{position:absolute;left:40px;right:40px;top:735px;height:470px;display:flex;flex-direction:column;align-items:center;justify-content:center}
.fc .texto p{font:700 60px/1.12 'Inter',sans-serif;color:#fff;text-align:center;text-wrap:balance}
.fc .texto p+p{margin-top:.5em}
.fc .assin{bottom:40px;color:#BDBDBD}
/* miolo · meia tela */
.mtela{background:#111}
.mtela .col{position:absolute;top:0;bottom:0;width:540px;padding:0 44px;display:flex;flex-direction:column;justify-content:center}
.mtela .col p{font:400 37px/1.38 'Inter',sans-serif;color:#F5F5F0}
.mtela .col p+p{margin-top:26px}
.mtela .col b,.mtela .col .am{color:#FFD21F;font-weight:700}
.mtela .foto{position:absolute;top:0;bottom:0;width:540px;height:1350px;object-fit:cover;object-position:var(--foco,50% 40%)}
.mtela.esq .col{left:0}.mtela.esq .foto{right:0}.mtela.dir .col{right:0}.mtela.dir .foto{left:0}
.mtela .handle{width:540px;text-align:left;padding-left:44px;font-size:20px;color:#777}.mtela.dir .handle{left:540px}
/* miolo · faixa amarela */
.fx{background:#F5F5F0}
.fx .texto{position:absolute;left:0;right:0;top:150px;bottom:180px;display:flex;flex-direction:column;justify-content:center;gap:42px}
.fx .texto p{font:400 52px/1.12 'Inter',sans-serif;color:#13161b;letter-spacing:-.02em;padding:0 100px}
.fx .texto p.faixa{background:#FFD21F;margin-left:84px;padding:40px 60px 40px 40px;font-weight:800;font-size:50px;line-height:1.12}
.fx .seta{position:absolute;left:115px;right:110px;bottom:120px;height:2px;background:#8A99AA}
.fx .seta::after{content:"";position:absolute;right:-2px;top:-7px;border:8px solid transparent;border-left:14px solid #8A99AA}
.fx .handle{color:#8E8E8E}
/* miolo · foto + legenda-adesivo */
.stk{background:#111}
.stk .foto{position:absolute;inset:0;width:1080px;height:1350px;object-fit:cover;object-position:var(--foco,50% 45%)}
.stk .texto{position:absolute;left:90px;right:90px;top:var(--sy,860px);display:flex;flex-direction:column;align-items:center;gap:0}
.stk .texto p{text-align:center}
.stk .texto p span{background:#fff;color:#111;font:600 42px/1.5 'Inter',sans-serif;padding:6px 16px;border-radius:12px;-webkit-box-decoration-break:clone;box-decoration-break:clone}
.stk .handle{color:rgba(255,255,255,.8);text-shadow:0 1px 6px #000}
/* miolo · antes e hoje empilhados */
.ah{background:#0b0b0b}
.ah .meia{position:absolute;left:0;right:0;height:530px;overflow:hidden}
.ah .meia img{width:100%;height:100%;object-fit:cover;object-position:var(--foco,50% 40%)}
.ah .m1{top:0}.ah .m2{top:540px}
.ah .m1 img{filter:grayscale(.8) brightness(.78) contrast(1.06)}
.ah .m1::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.25),transparent 30%,transparent 75%,rgba(0,0,0,.35))}
.ah .m2::after{content:"";position:absolute;left:0;right:0;bottom:0;height:190px;background:linear-gradient(transparent,#0b0b0b)}
.ah .costura{position:absolute;left:0;right:0;top:530px;height:10px;background:#FFD21F;box-shadow:0 0 34px rgba(255,210,31,.65);z-index:2}
.ah .seta{position:absolute;left:50%;top:535px;width:96px;height:96px;transform:translate(-50%,-50%);border-radius:50%;background:#FFD21F;border:7px solid #0b0b0b;z-index:3;display:flex;align-items:center;justify-content:center;box-shadow:0 0 30px rgba(255,210,31,.5)}
.ah .seta svg{width:44px;height:44px}
.ah .rot{position:absolute;left:40px;top:36px;z-index:2;display:flex;align-items:center;gap:12px;font:400 62px/1 'Bebas Neue',sans-serif;padding:12px 26px 8px 18px;border-radius:16px;box-shadow:0 10px 26px rgba(0,0,0,.45)}
.ah .rot i{width:38px;height:38px;border-radius:50%;font:900 24px/38px 'Inter',sans-serif;text-align:center;font-style:normal;margin-top:-4px}
.ah .m1 .rot{background:rgba(14,14,15,.9);color:#F5F5F0;border:2px solid rgba(255,255,255,.22)}.ah .m1 .rot i{background:#3a3a3e;color:#cfcfcb}
.ah .m2 .rot{top:66px;background:#FFD21F;color:#111}.ah .m2 .rot i{background:#111;color:#FFD21F}
.ah .texto{position:absolute;left:70px;right:70px;top:1080px;height:205px;display:flex;align-items:center;justify-content:center}
.ah .texto p{font:700 46px/1.22 'Inter',sans-serif;color:#F5F5F0;text-align:center;text-wrap:balance}
.ah .texto mark{background:#FFD21F;color:#111;padding:0 .12em}
/* miolo · lista com linhas sobre foto escura */
.ll{background:#0b0b0b}
.ll .foto{position:absolute;inset:0;width:1080px;height:1350px;object-fit:cover;filter:brightness(.6)}
.ll .veu{position:absolute;inset:0;background:rgba(10,10,10,.82)}
.ll .corpo{position:absolute;left:84px;right:84px;top:140px;bottom:150px;display:flex;flex-direction:column;gap:20px}
.ll .chapeu{display:flex;align-items:center;gap:16px;font:800 28px/1.2 'Archivo',sans-serif;letter-spacing:.22em;color:#FFD21F;text-transform:uppercase}
.ll .chapeu::before{content:"";flex:none;width:40px;height:4px;background:#FFD21F}
.ll .tit{font:400 116px/1.02 'Bebas Neue',sans-serif;color:#fff;text-transform:uppercase}
.ll .tit .am{color:#FFD21F}
.ll .sub{font:500 36px/1.3 'Inter',sans-serif;color:#e8e8e4}
.ll .sub mark{background:#FFD21F;color:#111;padding:0 .12em}
.ll .linhas{flex:1;min-height:0;margin:8px -14px 0;display:flex;flex-direction:column;justify-content:center;gap:22px}
.ll .lin{position:relative;flex:0 1 168px;min-height:112px;display:flex;align-items:center;gap:30px;padding:20px 36px 20px 26px;
  background:linear-gradient(180deg,rgba(28,29,34,.86),rgba(16,16,19,.86));border:1.5px solid rgba(255,255,255,.13);border-radius:26px;box-shadow:0 16px 34px rgba(0,0,0,.45),inset 0 1px 0 rgba(255,255,255,.06)}
.ll .lin+.lin::before{content:"";position:absolute;left:62px;top:-24px;width:4px;height:24px;background:linear-gradient(#FFD21F,rgba(255,210,31,.35))}
.ll .lin b{flex:none;width:78px;height:78px;border-radius:50%;background:#FFD21F;color:#111;font:400 52px/84px 'Bebas Neue',sans-serif;text-align:center;box-shadow:0 0 0 6px rgba(255,210,31,.14),0 0 24px rgba(255,210,31,.45)}
.ll .lin span{font:600 38px/1.25 'Inter',sans-serif;color:#fff}
.ll .lin span mark{background:#FFD21F;color:#111;padding:0 .12em}
.ll .barra{position:absolute;left:0;bottom:0;height:10px;background:#FFD21F}
.ll .handle{color:#cfcfcb;top:1290px}
/* miolo · conta visual (v2: caixas com número, operadores em círculo, resultado com brilho) */
.cv{background:#0c0c0d}
.cv::before{content:"";position:absolute;inset:0;background-image:radial-gradient(rgba(255,255,255,.07) 1.6px,transparent 1.7px);background-size:22px 22px}
.cv .brilho{position:absolute;left:50%;bottom:120px;width:1000px;height:640px;transform:translateX(-50%);background:radial-gradient(ellipse at 50% 70%,rgba(255,210,31,.16),transparent 62%);z-index:0}
.cv .chapeu{position:absolute;left:0;right:0;top:74px;text-align:center}
.cv .chapeu span{display:inline-block;background:#FFD21F;color:#111;font:800 24px/1 'Inter',sans-serif;letter-spacing:.18em;text-transform:uppercase;padding:11px 20px 10px;border-radius:999px}
.cv .tit{position:absolute;left:70px;right:70px;top:124px;text-align:center;font:400 124px/.95 'Bebas Neue',sans-serif;color:#F5F5F0;text-transform:uppercase}
.cv .tit .am{color:#FFD21F}
.cv .tit::after{content:"";display:block;width:120px;height:6px;margin:26px auto 0;border-radius:6px;background:#FFD21F;box-shadow:0 0 18px rgba(255,210,31,.6)}
.cv .conta{position:absolute;left:84px;right:84px;top:330px;bottom:150px;display:flex;flex-direction:column;justify-content:center;gap:26px}
.cv .cx{position:relative;flex:1 1 0;max-height:205px;min-height:112px;display:flex;align-items:center;gap:30px;padding:0 44px 0 34px;
  background:linear-gradient(180deg,#1e2026,#15161a);border:2px solid #2f323a;border-radius:30px;box-shadow:0 18px 40px rgba(0,0,0,.5),inset 0 1px 0 rgba(255,255,255,.07)}
.cv .cx em{flex:none;width:66px;height:66px;border-radius:50%;border:2.5px solid rgba(255,210,31,.6);color:#FFD21F;font:400 36px/62px 'Bebas Neue',sans-serif;text-align:center;font-style:normal;background:rgba(255,210,31,.06)}
.cv .cx .vt{flex:1;min-width:0}
.cv .cx b{display:block;white-space:nowrap;font:900 94px/1 'Archivo',sans-serif;font-stretch:76%;color:#F5F5F0;letter-spacing:-.005em}
.cv .cx span{display:block;margin-top:12px;font:700 26px/1.15 'Inter',sans-serif;letter-spacing:.15em;text-transform:uppercase;color:#9da2ac}
.cv .cx:not(.fim) .vt{display:flex;align-items:center;justify-content:space-between;gap:26px}
.cv .cx:not(.fim) b{flex:0 1 auto;min-width:0;overflow:hidden}
.cv .cx:not(.fim) span{flex:none;max-width:46%;margin:0;padding:13px 22px 12px;border-radius:999px;background:rgba(255,255,255,.05);border:1.5px solid #3a3d46;color:#c4c8d0;text-align:center;font-size:24px;line-height:1.2;letter-spacing:.1em}
.cv .op{position:relative;height:0;z-index:3;display:flex;justify-content:center}
.cv .op i{position:absolute;top:-39px;width:78px;height:78px;border-radius:50%;background:#FFD21F;color:#111;font:900 52px/76px 'Archivo',sans-serif;text-align:center;font-style:normal;
  box-shadow:0 0 0 9px #0c0c0d,0 0 30px rgba(255,210,31,.55)}
.cv .op.ig i{background:#F5F5F0;box-shadow:0 0 0 9px #0c0c0d,0 0 30px rgba(255,255,255,.25)}
.cv .cx.fim{flex-grow:1.4;max-height:285px;min-height:170px;border:0;background:linear-gradient(135deg,#FFE45C 0%,#FFD21F 50%,#F2B705 100%);
  box-shadow:0 0 0 7px rgba(255,210,31,.16),0 0 80px rgba(255,210,31,.38),0 22px 50px rgba(0,0,0,.55)}
.cv .cx.fim b{color:#111;font-size:118px}
.cv .cx.fim span{color:rgba(17,17,17,.72)}
.cv .cx.fim em{background:#111;border-color:#111;color:#FFD21F;font:900 34px/66px 'Inter',sans-serif;width:70px;height:70px}
.cv .selo{position:absolute;right:30px;top:-22px;background:#111;color:#FFD21F;border:2.5px solid #FFD21F;font:800 21px/1 'Inter',sans-serif;letter-spacing:.18em;padding:10px 16px 9px;border-radius:999px;transform:rotate(2.5deg);box-shadow:0 8px 20px rgba(0,0,0,.45)}
/* miolo · citação com assinatura */
.ct{background:#000}
.ct .aspas{position:absolute;left:84px;top:170px;font:900 260px/1 'Archivo',sans-serif;color:#FFD21F}
.ct .texto{position:absolute;left:96px;right:96px;top:330px;bottom:330px;display:flex;align-items:center}
.ct .texto p{font:700 58px/1.22 'Inter',sans-serif;color:#fff;letter-spacing:-.01em}
.ct .ass{position:absolute;left:96px;bottom:170px;display:flex;align-items:center;gap:20px}
.ct .ass i{width:76px;height:76px;border-radius:50%;background:#FFD21F;color:#111;font:900 34px/76px 'Archivo',sans-serif;text-align:center;font-style:normal}
.ct .ass b{display:block;font:700 30px/1.2 'Inter',sans-serif;color:#fff}.ct .ass span{display:block;font:400 26px/1.3 'Inter',sans-serif;color:#c9c9c4}
/* fechamento · foto + caixa branca */
.fcb{background:#111}
.fcb .foto{position:absolute;inset:0;width:1080px;height:1350px;object-fit:cover;object-position:var(--foco,50% 40%);filter:brightness(.8)}
.fcb .caixa{position:absolute;left:80px;right:80px;bottom:150px;background:#fff;border-radius:26px;padding:44px 48px;box-shadow:0 20px 60px rgba(0,0,0,.45)}
.fcb .caixa p{font:500 40px/1.3 'Inter',sans-serif;color:#111}
.fcb .caixa p+p{margin-top:.5em}
.fcb .caixa .carimbo2{display:inline-block;background:#FFD21F;color:#111;font:900 54px/1 'Archivo',sans-serif;padding:10px 18px 8px;border-radius:10px;margin:0 6px}
.fcb .caixa .siga{font:700 30px/1 'Inter',sans-serif;color:#555;margin-top:24px}

/* F3a · foto cheia escurecida, frase pequena no centro (legenda de story) */
.f3a,.f3b{background:#111}
.f3a .foto,.f3b .foto{position:absolute;inset:0;width:1080px;height:1350px;object-fit:cover;object-position:var(--foco,50% 50%)}
.f3a .foto{filter:brightness(.9) contrast(1.02) saturate(.9)}
.f3a .vinheta{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 42%,rgba(0,0,0,.28) 0,rgba(0,0,0,.08) 45%,rgba(0,0,0,.4) 100%)}
.f3a .grao,.f3b .grao{position:absolute;inset:0;background-image:url("__PAPEL__");opacity:.16;mix-blend-mode:overlay}
.f3a .texto{position:absolute;left:130px;right:130px;top:300px;height:480px;display:flex;align-items:center;justify-content:center}
.f3a .texto p{font:600 60px/1.22 'Inter',sans-serif;color:#fff;text-align:center;text-shadow:0 2px 14px rgba(0,0,0,.55);text-wrap:balance}
.f3a .handle,.f3b .handle{color:rgba(255,255,255,.72);text-shadow:0 1px 6px rgba(0,0,0,.5)}

/* F3b · foto cheia, legenda grande no terço de baixo */
.f3b .foto{filter:contrast(1.03) saturate(.92)}
.f3b .sombra{position:absolute;left:0;right:0;bottom:0;height:720px;background:linear-gradient(to bottom,rgba(8,8,8,0) 0,rgba(8,8,8,.55) 38%,rgba(8,8,8,.88) 78%,rgba(8,8,8,.95) 100%)}
.f3b .texto{position:absolute;left:74px;right:74px;top:840px;height:380px;display:flex;align-items:flex-end;justify-content:center}
.f3b .texto p{font:700 62px/1.13 'Inter',sans-serif;letter-spacing:-.012em;color:#fff;text-align:center;text-wrap:balance}

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
  // títulos condensados: cabem numa linha (encolhe até 62px; se ainda não couber, quebra em 2 linhas)
  for (const t of document.querySelectorAll('.esc .tit, .cv .tit, .ll .tit, .rv .tit')) {
    t.style.whiteSpace = 'nowrap'; let fs = parseFloat(getComputedStyle(t).fontSize), g = 0;
    while (t.scrollWidth > t.clientWidth + 1 && fs > 62 && g++ < 60) { fs *= 0.96; t.style.fontSize = fs + 'px'; }
    if (t.scrollWidth > t.clientWidth + 1) { t.style.whiteSpace = 'normal'; t.dataset.duas = '1'; }
  }
  // se o título quebrou em 2 linhas, empurra o resto do slide para baixo
  for (const s of document.querySelectorAll('.esc, .cv, .ll, .rv')) {
    const t = s.querySelector('.tit'); if (!t || !t.dataset.duas) continue;
    const extra = t.getBoundingClientRect().height - parseFloat(getComputedStyle(t).fontSize) * 1.0;
    for (const el of s.querySelectorAll('.sub, .cards, .corpo, .itens, .lista, .rede, .moldura, .conta, .linhas')) {
      if (el.closest('.corpo') && el !== s.querySelector('.corpo')) continue;
      el.style.top = (parseFloat(getComputedStyle(el).top) + extra) + 'px';
    }
  }
  // subtítulo curto (não o parágrafo .fit): no máximo 2 linhas (encolhe) e o bloco de baixo nunca encosta nele
  for (const s of document.querySelectorAll('.esc, .cv, .ll, .rv')) {
    const sub = s.querySelector(':scope > .sub:not(.fit)'); if (!sub) continue;
    const alt = () => { const lh = parseFloat(getComputedStyle(sub).lineHeight) || parseFloat(getComputedStyle(sub).fontSize) * 1.3; return sub.getBoundingClientRect().height / lh; };
    let fs = parseFloat(getComputedStyle(sub).fontSize), g = 0;
    while (alt() > 2.2 && fs > 26 && g++ < 30) { fs *= 0.95; sub.style.fontSize = fs + 'px'; }
    const fim = sub.getBoundingClientRect().bottom - s.getBoundingClientRect().top + 30;
    for (const el of s.querySelectorAll(':scope > .cards, :scope > .corpo, :scope > .itens, :scope > .lista, :scope > .conta, :scope > .linhas, :scope > .moldura')) {
      const t = parseFloat(getComputedStyle(el).top); if (!isNaN(t) && t < fim) el.style.top = fim + 'px';
    }
  }
  // REGRA ÚNICA DA FOTO (D-07): a foto emoldurada nunca é empurrada para fora nem fica sob o @; quem se ajusta é o texto
  for (const s of document.querySelectorAll('.esc')) {
    const mol = s.querySelector('.moldura'), rod = s.querySelector('.rod'); if (!mol) continue;
    const sTop = s.getBoundingClientRect().top;
    const limite = (rod ? rod.getBoundingClientRect().top : s.getBoundingClientRect().bottom) - sTop - 24;  // tudo acima do @
    const corpo = mol.closest('.corpo');
    if (corpo) {  // checklist: itens em cima, foto embaixo dentro do mesmo bloco → encolhe os itens até a foto caber inteira
      corpo.style.bottom = 'auto'; corpo.style.height = Math.max(200, limite - (corpo.getBoundingClientRect().top - sTop)) + 'px';
      const minFoto = () => parseFloat(getComputedStyle(mol).minHeight) || 0;
      const estoura = () => mol.getBoundingClientRect().bottom > corpo.getBoundingClientRect().bottom + 1;
      let g = 0;
      while (estoura() && g++ < 60) {
        const its = [...corpo.querySelectorAll('.it')]; const fs = its.length ? parseFloat(getComputedStyle(its[0]).fontSize) : 0;
        if (fs > 24) { its.forEach(el => { el.style.fontSize = fs * 0.95 + 'px'; el.style.paddingTop = el.style.paddingBottom = '10px'; }); corpo.style.gap = '28px'; }
        else if (minFoto() > 200) mol.style.minHeight = (minFoto() - 20) + 'px';
        else break;
      }
    } else {  // título + moldura + parágrafo: a moldura fica onde está; o parágrafo usa o espaço entre a foto e o @
      let mb = mol.getBoundingClientRect().bottom - sTop;
      const sub = s.querySelector(':scope > .sub.fit');
      if (sub) {
        const minTxt = 150;  // se faltar espaço para o texto, a moldura fica mais baixa (nunca sai do slide)
        if (limite - (mb + 30) < minTxt) { mol.style.height = Math.max(200, mol.clientHeight - (minTxt - (limite - (mb + 30)))) + 'px'; mb = mol.getBoundingClientRect().bottom - sTop; }
        sub.style.top = (mb + 30) + 'px'; sub.style.height = Math.max(minTxt, limite - (mb + 30)) + 'px';
      } else if (mb > limite) mol.style.height = Math.max(200, limite - (mol.getBoundingClientRect().top - sTop)) + 'px';
    }
  }
  // notícia sem foto: o nome grande (rótulo) cabe em no máximo 2 linhas e nunca entra embaixo do cartão
  for (const d of document.querySelectorAll('.nt .data')) {
    const dt = d.querySelector('.dt'), card = d.parentElement.querySelector('.card'); if (!dt || !card) continue;
    const linhas = () => { const r = [...dt.getClientRects()]; return new Set(r.map(q => Math.round(q.top))).size; };
    const fundo = () => d.getBoundingClientRect().bottom > card.getBoundingClientRect().top - 20;
    let fs = parseFloat(getComputedStyle(d).fontSize), g = 0;
    while ((linhas() > 2 || fundo() || d.scrollWidth > d.clientWidth + 1) && fs > 48 && g++ < 80) { fs *= 0.96; d.style.fontSize = fs + 'px'; }
  }
  // valores grandes das caixas: numa linha só, encolhendo; se ainda não couber, quebram em 2 linhas
  // valor nunca encosta no círculo do operador: o tamanho acompanha a altura da caixa
  for (const b of document.querySelectorAll('.cv .cx b')) {
    const cx = b.closest('.cx'), fim = cx.classList.contains('fim');
    const lim = Math.max(46, cx.clientHeight - (fim ? 104 : 62));
    if (parseFloat(getComputedStyle(b).fontSize) > lim) b.style.fontSize = lim + 'px';
  }
  for (const b of document.querySelectorAll('.cv .cx b')) {
    let fs = parseFloat(getComputedStyle(b).fontSize), g = 0;
    while (b.scrollWidth > b.clientWidth + 1 && fs > 46 && g++ < 60) { fs *= 0.95; b.style.fontSize = fs + 'px'; }
    if (b.scrollWidth > b.clientWidth + 1) b.style.whiteSpace = 'normal';
  }
  // caixas que mesmo assim estouram a altura: encolhe tudo dentro delas
  for (const cx of document.querySelectorAll('.cv .cx, .esc.cd .card, .ll .lin')) {
    let g = 0;
    while (cx.scrollHeight > cx.clientHeight + 1 && g++ < 40) {
      for (const el of cx.querySelectorAll('b, span')) { el.style.fontSize = parseFloat(getComputedStyle(el).fontSize) * 0.96 + 'px'; }
    }
  }
  // caixa centralizada que cresce para os DOIS lados esconde o estouro de cima (o robô não via): centraliza só se couber
  for (const box of document.querySelectorAll('.fit, .cp .zona')) {
    const st = getComputedStyle(box);
    if (st.justifyContent === 'center') box.style.justifyContent = 'safe center';
    if (st.alignItems === 'center' && st.flexDirection === 'row') box.style.alignItems = 'safe center';
  }
  // cupom: o papel nunca passa da área dele (encolhe inteiro, mantendo o desenho)
  for (const z of document.querySelectorAll('.cp .zona')) {
    const pp = z.querySelector('.papel'); if (!pp) continue;
    const k = Math.min(1, (z.clientHeight - 10) / pp.offsetHeight);
    if (k < 1) { pp.style.transform = `rotate(-1.6deg) scale(${k.toFixed(3)})`; pp.style.transformOrigin = 'center center'; pp.style.margin = `${-(pp.offsetHeight*(1-k))/2}px 0`; }
  }
  // lista: se o bloco empilhado não couber, encolhe título, frase e itens até caber (nada fica por cima de nada)
  for (const c of document.querySelectorAll('.ll .corpo')) {
    const fim = () => { const k = c.lastElementChild; const ls = k.querySelectorAll('.lin'); const u = ls.length ? ls[ls.length-1] : k; return u.getBoundingClientRect().bottom; };
    let g = 0;
    while (fim() > c.getBoundingClientRect().bottom + 1 && g++ < 40) {
      for (const el of c.querySelectorAll('.tit, .sub, .chapeu, .lin span, .lin b')) el.style.fontSize = parseFloat(getComputedStyle(el).fontSize) * 0.95 + 'px';
      for (const el of c.querySelectorAll('.lin')) { el.style.minHeight = Math.max(70, parseFloat(getComputedStyle(el).minHeight) * 0.93) + 'px'; el.style.paddingTop = el.style.paddingBottom = '12px'; }
    }
  }
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
  // trava geral (19/11): nenhum texto encosta em outro texto nem numa foto que não é o fundo; se encostar, encolhe a letra
  for (const S of document.querySelectorAll('.slide')) {
    let ts = [...S.querySelectorAll('.fit, .tit, .sub, .texto, .caixa, .siga, .assin, .handle, .rod, .rodape, .pergunta')].filter(e => e.textContent.trim());
    ts = ts.filter(e => !ts.some(o => o !== e && o.contains(e)));
    // só fotos emolduradas (as de fundo e as que esmaecem sob o texto fazem parte do visual aprovado)
    const fotos = [...S.querySelectorAll('.moldura img, .meia img, .img img, .duas img')].filter(i => i.getBoundingClientRect().width > 200);
    const caixa = e => { const g = document.createRange(); g.selectNodeContents(e); return g.getBoundingClientRect(); };
    const bate = (a, b) => a.width && b.width && a.left < b.right - 4 && b.left < a.right - 4 && a.top < b.bottom - 4 && b.top < a.bottom - 4;
    const encolhe = e => { const ps = e.querySelectorAll('p'); (ps.length ? [...ps] : [e]).forEach(x => { x.style.fontSize = parseFloat(getComputedStyle(x).fontSize) * 0.95 + 'px'; }); };
    let g = 0, resto = 0;
    while (g++ < 10) {  // no máximo ~40% menor: se ainda bater, o robô avisa (dataset.sobreposto)
      resto = 0;
      for (let i = 0; i < ts.length; i++) {
        const a = caixa(ts[i]);
        for (const f of fotos) if (!f.closest('.fit') && bate(a, f.getBoundingClientRect())) { resto++; encolhe(ts[i]); }
        for (let j = i + 1; j < ts.length; j++) if (bate(a, caixa(ts[j]))) { resto++; encolhe(ts[ts[i].classList.contains('fit') ? i : j]); }
      }
      if (!resto) break;
    }
    S.dataset.sobreposto = resto;
  }
})();
"""

SVG_FILTROS = """<svg width="0" height="0" style="position:absolute"><filter id="aspero">
<feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" result="t"/>
<feDisplacementMap in="SourceGraphic" in2="t" scale="3"/></filter></svg>"""


def marcar(txt: str, cor: bool = False) -> str:
    t = html.escape(txt, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r'<span class="am">\1</span>' if cor else r"<mark>\1</mark>", t)
    t = re.sub(r"\[\[(.+?)\]\]", r'<span class="carimbo">\1</span>', t)
    # quebras de linha do texto aprovado ficam (D-07 item 5): linha em branco = respiro, quebra simples = nova linha
    t = re.sub(r"[ \t]*\n[ \t]*\n\s*", "<br><br>", t.strip())
    return re.sub(r"[ \t]*\n[ \t]*", "<br>", t)


def paras(ps, cls=""):
    c = f' class="{cls}"' if cls else ""
    return "".join(f"<p{c}>{marcar(p)}</p>" for p in ps)


# ---------- KIT 2: moldes do catálogo de 60 formatos ----------
def _foco(s, padrao="50% 40%"):
    return html.escape(s.get("foco") or padrao)


def _assin():
    return f'<div class="assin"><img src="{AVATAR}">{HANDLE}</div>'


def _k_circulos(s):
    bolas = "".join(f'<img src="{u}">' for u in (s.get("fotos_circulo") or [])[:2])
    return (f'<div class="slide circ"><img class="foto" src="{s["foto"]}" style="--foco:{_foco(s,"50% 30%")}"><div class="bolas">{bolas}</div>'
            f'<div class="texto fit"><p>{marcar(s["texto"], cor=True)}</p></div><div class="handle" style="color:#8C8C8C">{HANDLE}</div></div>')


def _k_marcatexto(s):
    linhas = "".join(f'<span class="l">{marcar(l)}</span><br>' for l in re.split(r"\n+", s["texto"]) if l.strip())
    sub = f'<div class="sub">{marcar(s["sub"])}</div>' if s.get("sub") else ""
    return (f'<div class="slide mt"><img class="foto" src="{s["foto"]}" style="--foco:{_foco(s)}"><div class="sombra"></div>'
            f'<img class="logo" src="{LOGO}"><div class="texto fit"><p>{linhas}</p></div>{sub}</div>')


def _k_revista(s):
    cores = {"creme": ("#F3EEDC", "#111"), "preto": ("#111", "#F3EEDC"), "amarelo": ("#FFD21F", "#111"), "lilas": ("#B49CFF", "#111")}
    bg, tx = cores.get(s.get("cor") or "creme", cores["creme"])
    t0 = re.sub(r"_(.+?)_", lambda m: "**" + m.group(1) + "**", s.get("titulo", ""))  # o modelo às vezes sublinha com _palavra_
    tit = marcar(t0, cor=False).replace("<mark>", "<u>").replace("</mark>", "</u>")
    obj = f'<img class="obj" src="{s["foto"]}">' if s.get("foto") else ""
    esc_cls = " escuro" if (s.get("cor") == "preto") else ""
    return (f'<div class="slide rv{esc_cls}" style="--bg:{bg};--tx:{tx}"><div class="tit cond">{tit}</div>{obj}'
            f'<div class="corpo fit" data-max="52">{paras(s.get("paragrafos") or [])}</div><div class="rodape">{HANDLE}</div></div>')


def _k_numero(s):
    linhas = (s.get("numero") or "").split("\n")
    num = html.escape(linhas[0]) + (f"<small>{html.escape(linhas[1])}</small>" if len(linhas) > 1 else "")
    faixa = f'<div class="faixa"><span>{html.escape(s.get("faixa",""))}</span></div>' if s.get("faixa") else ""
    txt = f'<div class="texto">{marcar(s.get("texto",""))}</div>' if s.get("texto") else ""
    return (f'<div class="slide ng"><img class="foto" src="{s["foto"]}" style="--foco:{_foco(s)}"><div class="num cond">{num}</div>{faixa}{txt}'
            f'<div class="handle" style="color:#bdbdbd">{HANDLE}</div></div>')


def _k_caderno(s):
    return (f'<div class="slide cad"><img class="foto" src="{s["foto"]}"><div class="faixa"><p>{marcar(s["texto"], cor=True)}</p></div>'
            f'<div class="handle">{HANDLE}</div></div>')


def _k_corrido(s):
    ps = s.get("paragrafos") or [s.get("texto", "")]
    return (f'<div class="slide fc"><img class="foto" src="{s["foto"]}" style="--foco:{_foco(s)}">'
            f'<div class="texto fit" data-max="66">{"".join(f"<p>{marcar(p, cor=True)}</p>" for p in ps)}</div>{_assin()}</div>')


def _k_meiatela(s):
    lado = "dir" if s.get("lado") == "dir" else "esq"
    ps = s.get("paragrafos") or [s.get("texto", "")]
    return (f'<div class="slide mtela {lado}"><div class="col fit" data-max="42">{"".join(f"<p>{marcar(p, cor=True)}</p>" for p in ps)}</div>'
            f'<img class="foto" src="{s["foto"]}" style="--foco:{_foco(s)}"><div class="handle">{HANDLE}</div></div>')


def _k_faixa(s):
    antes = "".join(f"<p>{marcar(p)}</p>" for p in (s.get("antes") or []))
    depois = "".join(f"<p>{marcar(p)}</p>" for p in (s.get("depois") or []))
    return (f'<div class="slide fx"><div class="texto fit">{antes}<p class="faixa">{marcar(s.get("faixa",""))}</p>{depois}</div>'
            f'<div class="seta"></div><div class="handle">{HANDLE}</div></div>')


def _k_sticker(s):
    ps = s.get("paragrafos") or [s.get("texto", "")]
    return (f'<div class="slide stk"><img class="foto" src="{s["foto"]}" style="--foco:{_foco(s)}">'
            f'<div class="texto">{"".join(f"<p><span>{marcar(p)}</span></p>" for p in ps)}</div><div class="handle">{HANDLE}</div></div>')


def _k_antes_hoje(s):
    f1, f2 = (s.get("fotos") or [s.get("foto"), s.get("foto")])[:2]
    r1, r2 = (s.get("rotulos") or ["Antes", "Hoje"])[:2]
    seta = '<svg viewBox="0 0 24 24"><path d="M12 4v15M6 13l6 6 6-6" fill="none" stroke="#111" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    return (f'<div class="slide ah"><div class="meia m1"><img src="{f1}"><div class="rot"><i>✕</i>{html.escape(r1)}</div></div>'
            f'<div class="meia m2"><img src="{f2}"><div class="rot"><i>✓</i>{html.escape(r2)}</div></div>'
            f'<div class="costura"></div><div class="seta">{seta}</div>'
            f'<div class="texto fit"><p>{marcar(s.get("texto",""))}</p></div></div>')


def _k_lista(s):
    _semnum = lambda t: re.sub(r"^\s*\d+\s*[.)\-:]\s*", "", t)
    lins = "".join(f'<div class="lin"><b>{i}</b><span>{marcar(_semnum(t))}</span></div>' for i, t in enumerate(s.get("itens") or [], 1))
    fundo = f'<img class="foto" src="{s["foto"]}">' if s.get("foto") else ""
    prog = s.get("progresso") or 0
    # tudo empilhado num bloco só: chapéu, título, frase e lista nunca ficam um em cima do outro
    chapeu = f'<div class="chapeu">{html.escape(s["chapeu"])}</div>' if s.get("chapeu") else ""
    sub = f'<div class="sub">{marcar(s["sub"])}</div>' if s.get("sub") else ""
    return (f'<div class="slide ll">{fundo}<div class="veu"></div><div class="corpo">{chapeu}'
            f'<div class="tit">{marcar(s.get("titulo",""), cor=True)}</div>{sub}<div class="linhas">{lins}</div></div>'
            f'<div class="barra" style="width:{max(0,min(1,prog))*100:.0f}%"></div><div class="handle">{HANDLE}</div></div>')


def _k_conta(s):
    partes, n = [], 0
    caixas = s.get("caixas") or []
    for i, c in enumerate(caixas):
        fim = bool(c.get("fim")) or (i == len(caixas) - 1 and (c.get("op") or "").strip() == "=")
        if i and c.get("op"):
            op = c["op"].strip().replace("x", "×").replace("*", "×")
            partes.append(f'<div class="op{" ig" if op == "=" else ""}"><i>{html.escape(op)}</i></div>')
        n += 1
        marca = "✓" if fim else f"{n:02d}"
        rot = f'<span>{html.escape(c.get("rotulo",""))}</span>' if c.get("rotulo") else ""
        selo = '<div class="selo">RESULTADO</div>' if fim else ""
        partes.append(f'<div class="cx{" fim" if fim else ""}"><em>{marca}</em><div class="vt"><b>{html.escape(c["valor"])}</b>{rot}</div>{selo}</div>')
    chapeu = f'<div class="chapeu"><span>{html.escape(s["chapeu"])}</span></div>' if s.get("chapeu") else ""
    return (f'<div class="slide cv"><div class="brilho"></div>{chapeu}<div class="tit">{marcar(s.get("titulo",""), cor=True)}</div>'
            f'<div class="conta">{"".join(partes)}</div>{_assin()}</div>')


def _k_citacao(s):
    nome = s.get("nome", ""); ini = (nome[:1] or "•").upper()
    return (f'<div class="slide ct"><div class="aspas">“</div><div class="texto fit" data-max="64"><p>{marcar(s.get("texto",""), cor=True)}</p></div>'
            f'<div class="ass"><i>{html.escape(ini)}</i><div><b>{html.escape(nome)}</b><span>{html.escape(s.get("papel",""))}</span></div></div>{_assin()}</div>')


def _k_fecho(s):
    ps = s.get("paragrafos") or [s.get("texto", "")]
    corpo = "".join(f"<p>{marcar(p)}</p>" for p in ps).replace('class="carimbo"', 'class="carimbo2"')
    return (f'<div class="slide fcb"><img class="foto" src="{s["foto"]}" style="--foco:{_foco(s)}"><div class="caixa">{corpo}'
            f'<div class="siga">Siga {HANDLE}</div></div></div>')


KIT2 = {
    "capa_circulos": _k_circulos, "capa_marcatexto": _k_marcatexto, "capa_revista": _k_revista, "capa_numero": _k_numero,
    "capa_caderno": _k_caderno, "f1_corrido": _k_corrido, "meia_tela": _k_meiatela, "faixa_amarela": _k_faixa,
    "foto_sticker": _k_sticker, "antes_hoje": _k_antes_hoje, "lista_linhas": _k_lista, "conta_visual": _k_conta,
    "citacao": _k_citacao, "fecho_foto": _k_fecho, "miolo_revista": _k_revista,
}


# ---------- moldes do Diretor de Arte: cartão de notícia e cupom que cresce ----------
CSS_DA = """
.nt{background:#0b0b0c}
.nt .foto{position:absolute;left:0;top:0;width:1080px;height:660px;object-fit:cover;object-position:var(--foco,50% 30%)}
.nt .sombra{position:absolute;left:0;top:0;width:1080px;height:660px;background:linear-gradient(180deg,rgba(0,0,0,.25) 0,transparent 30%,transparent 60%,#0b0b0c 100%)}
.nt .cred{position:absolute;right:28px;top:578px;background:rgba(0,0,0,.55);padding:6px 10px;border-radius:6px;font:500 17px/1.2 'Inter',sans-serif;color:rgba(255,255,255,.78);text-shadow:0 1px 3px #000;max-width:620px;text-align:right}
.nt .topo{position:absolute;left:64px;top:56px;display:flex;gap:12px;align-items:center}
.nt .pil{background:#FFD21F;color:#111;font:800 24px/1 'Inter',sans-serif;letter-spacing:.08em;padding:12px 18px;border-radius:999px}
.nt .pil.esc{background:rgba(10,10,10,.75);color:#F5F5F0;border:1.5px solid rgba(255,255,255,.25)}
.nt .data{position:absolute;left:64px;right:64px;top:150px;font:400 210px/.9 'Bebas Neue',sans-serif;color:#F5F5F0;letter-spacing:.01em}
.nt .data small{display:block;font:700 30px/1.3 'Inter',sans-serif;color:#9a9a9a;letter-spacing:.12em;margin-top:14px}
.nt .card{position:absolute;left:56px;right:56px;top:630px;bottom:150px;background:linear-gradient(180deg,#171719,#121213);border:1px solid #2a2a2e;border-radius:28px;box-shadow:0 30px 60px rgba(0,0,0,.55);padding:44px 52px 44px 64px;overflow:hidden}
.nt.semfoto .card{top:470px;bottom:170px}
.nt.semfoto .card .texto p{font-size:54px}
.nt .card::before{content:"";position:absolute;left:0;top:34px;bottom:34px;width:8px;border-radius:0 8px 8px 0;background:#FFD21F;box-shadow:0 0 22px rgba(255,210,31,.55)}
.nt .fonte{display:flex;align-items:center;gap:14px;font:800 24px/1 'Inter',sans-serif;letter-spacing:.1em;color:#FFD21F;text-transform:uppercase;margin-bottom:26px}
.nt .fonte span{color:#8d8d92;font-weight:600;letter-spacing:.06em}
.nt .card .texto{position:absolute;left:64px;right:52px;top:104px;bottom:40px}
.nt .card .texto p{font:600 46px/1.28 'Inter',sans-serif;color:#F5F5F0;letter-spacing:-.01em;margin-bottom:22px}
.nt .card .texto p .am{color:#FFD21F}
.credito{position:absolute;right:22px;top:22px;z-index:20;max-width:640px;text-align:right;font:500 16px/1.25 Inter,sans-serif;color:rgba(255,255,255,.85);background:rgba(0,0,0,.55);padding:6px 10px;border-radius:6px}
.cp{background:#0c0c0d;background-image:radial-gradient(rgba(255,255,255,.05) 1.5px,transparent 1.5px);background-size:34px 34px}
.cp .texto{position:absolute;left:72px;right:72px;top:80px;height:330px;display:flex;flex-direction:column;justify-content:center}
.cp .texto p{font:700 52px/1.22 'Inter',sans-serif;color:#F5F5F0;letter-spacing:-.015em;margin-bottom:16px}
.cp .texto p .am{color:#FFD21F}
.cp .zona{position:absolute;left:0;right:0;top:420px;bottom:130px;display:flex;align-items:center;justify-content:center}
.cp .papel{position:relative;width:820px;transform:rotate(-1.6deg);background:#f7f4ec;color:#1b1b1b;padding:46px 54px 40px;font-family:'Space Mono',monospace;
  box-shadow:0 40px 80px rgba(0,0,0,.6),0 0 0 1px rgba(0,0,0,.05);
  -webkit-mask:conic-gradient(from -45deg at bottom,#0000,#000 1deg 89deg,#0000 90deg) 50%/28px 100%,conic-gradient(from 135deg at top,#0000,#000 1deg 89deg,#0000 90deg) 50%/28px 100%;
  -webkit-mask-composite:source-in;mask-composite:intersect}
.cp .cab{text-align:center;font:700 42px/1.2 'Space Mono',monospace;letter-spacing:.06em;text-transform:uppercase}
.cp .cab small{display:block;font:400 24px/1.4 'Space Mono',monospace;color:#777;letter-spacing:.04em;margin-top:6px}
.cp .tr{border-top:3px dashed #bdb8aa;margin:22px 0}
.cp .lin{display:flex;align-items:baseline;gap:12px;font:400 38px/1.55 'Space Mono',monospace;color:#8a867c;padding:4px 10px;margin:0 -10px;border-radius:6px}
.cp .lin b{font-weight:700}
.cp .lin i{flex:1;border-bottom:3px dotted #cfc9b9;transform:translateY(-8px)}
.cp .lin.novo{color:#111;background:#FFD21F;font-weight:700}
.cp .lin.novo i{border-color:rgba(0,0,0,.35)}
.cp .lin.novo::after{content:"NOVO";font:700 16px/1 'Inter',sans-serif;letter-spacing:.1em;background:#111;color:#FFD21F;padding:6px 8px;border-radius:5px;align-self:center}
.cp .tot{display:flex;justify-content:space-between;align-items:baseline;font:700 46px/1 'Space Mono',monospace;color:#111}
.cp .tot b{font:400 120px/1 'Bebas Neue',sans-serif;letter-spacing:.02em}
.cp .barras{height:54px;margin-top:22px;background:repeating-linear-gradient(90deg,#1b1b1b 0 3px,transparent 3px 6px,#1b1b1b 6px 7px,transparent 7px 11px,#1b1b1b 11px 15px,transparent 15px 18px);opacity:.85}
"""
CSS += CSS_DA


def _k_noticia(s):
    ps = s.get("paragrafos") or [s.get("texto", "")]
    fonte = html.escape(s.get("chapeu") or "NOTÍCIA"); data = html.escape(s.get("rotulo") or "")
    linha = f'<div class="fonte">{fonte}{f"<span>· {data}</span>" if data else ""}</div>'
    texto = f'<div class="texto fit" data-max="52">{"".join(f"<p>{marcar(p, cor=True)}</p>" for p in ps)}</div>'
    if s.get("foto"):
        cred = f'<div class="cred">{html.escape(s["credito"])}</div>' if s.get("credito") else ""
        return (f'<div class="slide nt"><img class="foto" src="{s["foto"]}" style="--foco:{_foco(s,"50% 30%")}"><div class="sombra"></div>{cred}'
                f'<div class="topo"><span class="pil">NOTÍCIA</span>{f"<span class=pil esc>{data}</span>" if data else ""}</div>'
                f'<div class="card">{linha}{texto}</div>{_assin()}</div>')
    grande = f'<div class="data"><span class="dt">{data or "AGORA"}</span><small>{fonte}</small></div>'
    return (f'<div class="slide nt semfoto"><div class="topo"><span class="pil">NOTÍCIA</span></div>{grande}'
            f'<div class="card">{linha}{texto}</div>{_assin()}</div>')


def _k_cupom(s):
    ps = s.get("paragrafos") or ([s["texto"]] if s.get("texto") else [])
    itens = s.get("itens") or []
    linhas = []
    for k, it in enumerate(itens):
        if "|" in it:
            nome, val = [x.strip() for x in it.split("|", 1)]
        else:
            m = re.search(r"(R\$\s?[\d.,]+)\s*$", it); nome, val = (it[:m.start()].strip(), m.group(1)) if m else (it, "")
        novo = " novo" if k == len(itens) - 1 else ""
        linhas.append(f'<div class="lin{novo}"><b>{html.escape(nome)}</b><i></i><span>{html.escape(val)}</span></div>')
    titulo = html.escape(s.get("titulo") or "CUPOM")
    texto = f'<div class="texto fit" data-max="56">{"".join(f"<p>{marcar(p, cor=True)}</p>" for p in ps)}</div>' if ps else ""
    return (f'<div class="slide cp">{texto}<div class="zona"><div class="papel"><div class="cab">{titulo}<small>{html.escape(s.get("sub") or "")}</small></div><div class="tr"></div>'
            f'{"".join(linhas)}<div class="tr"></div><div class="tot"><span>TOTAL</span><b>{html.escape(s.get("rotulo") or "")}</b></div><div class="barras"></div></div></div>{_assin()}</div>')


KIT2["noticia"] = _k_noticia
KIT2["cupom"] = _k_cupom


def _normalizar(s: dict) -> dict:
    s = dict(s)
    ps = [p for p in (s.get("paragrafos") or []) if p and p.strip()]
    if not ps and s.get("texto") and not s["molde"].startswith("capa_"):
        ps = [p.strip() for p in re.split(r"\n\s*\n|\n", s["texto"]) if p.strip()]
    s["paragrafos"] = ps
    if s["molde"].startswith("capa_") and not s.get("texto"):
        s["texto"] = " ".join(ps)
    return s


PERFIL = None  # perfil visual aprovado do ambiente (layouts de marca mk_*)


def slide_html(s: dict) -> str:
    if str(s.get("molde", "")).startswith("mk_"):
        import moldes_marca
        return moldes_marca.html_slide(s, {**(PERFIL or {}), "handle": HANDLE or (PERFIL or {}).get("handle", "")})
    s = _normalizar(s)
    m = s["molde"]
    if m == "capa_f1":
        foco = html.escape(s.get("foco") or "50% 60%")
        corpo = (f'<div class="slide f1"><img class="foto" src="{s["foto"]}" style="--foco:{foco}"><div class="degrade"></div><div class="grao"></div>'
                 f'<div class="texto fit" data-max="82"><p>{marcar(s["texto"])}</p></div><div class="handle">{HANDLE}</div></div>')
    elif m == "capa_f1b":
        foco = html.escape(s.get("foco") or "50% 50%")
        seta = '<svg viewBox="0 0 24 24"><path d="M5 12h13M13 6l6 6-6 6" fill="none" stroke="#111" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
        corpo = (f'<div class="slide f1b"><img class="foto" src="{s["foto"]}" style="--foco:{foco}"><div class="grao"></div>'
                 f'<div class="seta">{seta}</div><div class="divisor"><i></i>{PORTA}<i></i></div>'
                 f'<div class="texto fit"><p>{marcar(s["texto"], cor=True)}</p></div></div>')
    elif m == "capa_perfil":
        foco = html.escape(s.get("foco") or "50% 40%")
        corpo = (f'<div class="slide perfil"><img class="foto" src="{s["foto"]}" style="--foco:{foco}"><div class="grao"></div>'
                 f'<div class="divisor"><i></i><div class="chip"><img src="{AVATAR}"><div><b>{NOME}</b><span>{HANDLE}</span></div></div><i></i></div>'
                 f'<div class="texto fit"><p>{marcar(s["texto"], cor=True)}</p></div></div>')
    elif m == "capa_comparacao":
        foco = html.escape(s.get("foco") or "50% 45%")
        e, d = (s.get("rotulos") or ["Antes", "Depois"])[:2]
        corpo = (f'<div class="slide comp"><img class="foto" src="{s["foto"]}" style="--foco:{foco}"><div class="corte"></div>'
                 f'<div class="rot e">{html.escape(e)}</div><div class="rot d">{html.escape(d)}</div>'
                 f'<div class="texto fit" data-max="80"><p>{marcar(s["texto"])}</p></div><div class="handle">{HANDLE}</div></div>')
    elif m == "capa_tweet":
        foco = html.escape(s.get("foco") or "50% 45%")
        ps = [p.strip() for p in re.split(r"\n+", s["texto"]) if p.strip()]
        corpo = (f'<div class="slide tw"><div class="topo"><img src="{AVATAR}"><div><b>{NOME}</b><span>{HANDLE}</span></div></div>'
                 f'<div class="texto fit" data-max="66">{paras(ps)}</div><div class="img"><img src="{s["foto"]}" style="--foco:{foco}"></div></div>')
    elif m == "capa_tweet2":
        ps = [p.strip() for p in re.split(r"\n+", s["texto"]) if p.strip()]
        f1, f2 = (s.get("fotos") or [s.get("foto"), s.get("foto")])[:2]
        corpo = (f'<div class="slide tw tw2"><div class="topo"><img src="{AVATAR}"><div><b>{NOME}</b><span>{HANDLE}</span></div></div>'
                 f'<div class="texto fit" data-max="64" style="height:380px">{paras(ps)}</div><div class="duas"><img src="{f1}"><img src="{f2}"></div></div>')
    elif m in ("esc_titulo_moldura", "esc_cards", "esc_checklist", "esc_rede"):
        rod = f'<div class="rod"><i></i>{HANDLE}<i></i></div>'
        tit = marcar(s.get("titulo", ""), cor=True)
        if m == "esc_titulo_moldura":
            foco = html.escape(s.get("foco") or "50% 40%")
            corpo = (f'<div class="slide esc tm"><div class="tit">{tit}</div><div class="moldura"><img src="{s["foto"]}" style="--foco:{foco}"></div>'
                     f'<div class="sub fit" data-max="46">{paras(s.get("paragrafos") or [s.get("texto", "")])}</div>{rod}</div>')
        elif m == "esc_cards":
            def _card(i, c):
                ic = f'<img class="ic" src="{c["icone"]}">' if c.get("icone") else ""
                nome = re.sub(r"^\s*\d+\s*[.)\-–:]\s*", "", c["nome"])  # o número já vem no 01, 02...
                return f'<div class="card"><div class="n">{i:02d}</div>{ic}<b>{marcar(nome)}</b><span>{marcar(c["texto"])}</span></div>'
            cards = "".join(_card(i, c) for i, c in enumerate(s["cards"], 1))
            sub = f'<div class="sub">{marcar(s["sub"])}</div>' if s.get("sub") else ""
            corpo = f'<div class="slide esc cd"><div class="tit">{tit}</div>{sub}<div class="cards">{cards}</div>{rod}</div>'
        elif m == "esc_checklist":
            foco = html.escape(s.get("foco") or "50% 35%")
            itens = "".join(f'<div class="it"><span>{marcar(t)}</span></div>' for t in s["itens"])
            sub = f'<div class="sub"><u>{marcar(s["sub"], cor=True)}</u></div>' if s.get("sub") else ""
            corpo = (f'<div class="slide esc ck"><div class="tit">{tit}</div>{sub}<div class="corpo"><div class="itens">{itens}</div>'
                     f'<div class="moldura"><img src="{s["foto"]}" style="--foco:{foco}"></div></div>{rod}</div>')
        else:  # esc_rede: até 6 rostos em hexágono ao redor de um centro
            import math
            nos = s["nos"][:6]; cx, cy, r = 540, 280, 200
            pts = [(cx + r * math.sin(2 * math.pi * k / len(nos)), cy - r * math.cos(2 * math.pi * k / len(nos))) for k in range(len(nos))]
            linhas = "".join(f'<line x1="{cx}" y1="{cy}" x2="{x:.0f}" y2="{y:.0f}"/>' for x, y in pts)
            linhas += "".join(f'<line x1="{pts[k][0]:.0f}" y1="{pts[k][1]:.0f}" x2="{pts[(k+1)%len(pts)][0]:.0f}" y2="{pts[(k+1)%len(pts)][1]:.0f}"/>' for k in range(len(pts)))
            svg = f'<svg viewBox="0 0 1080 560"><g stroke="#FFD21F" stroke-opacity=".75" stroke-width="3">{linhas}</g></svg>'
            nos_html = "".join(f'<div class="no" style="left:{x:.0f}px;top:{y:.0f}px"><img src="{n["foto"]}"><b>{html.escape(n["nome"])}</b><span>{html.escape(n.get("papel",""))}</span></div>'
                               for n, (x, y) in zip(nos, pts))
            lista = "".join(f'<div><b>{i}.</b>{marcar(t)}</div>' for i, t in enumerate(s.get("itens", []), 1))
            caixa = f'<div class="caixa">{marcar(s["caixa"])}</div>' if s.get("caixa") else ""
            corpo = (f'<div class="slide esc rd"><div class="tit">{tit}</div><div class="lista">{lista}</div>'
                     f'<div class="rede">{svg}<div class="centro">{html.escape(s.get("centro","VOCÊ"))}</div>{nos_html}</div>{caixa}{rod}</div>')
    elif m in KIT2:
        corpo = KIT2[m](s)
    elif m in ("capa_f3a", "capa_f3b"):
        foco = html.escape(s.get("foco") or "50% 50%")
        cls = m[-3:]
        extra = '<div class="vinheta"></div>' if cls == "f3a" else '<div class="sombra"></div>'
        dmax = ' data-max="76"' if cls == "f3b" else ""
        corpo = (f'<div class="slide {cls}"><img class="foto" src="{s["foto"]}" style="--foco:{foco}">{extra}<div class="grao"></div>'
                 f'<div class="texto fit"{dmax}><p>{marcar(s["texto"])}</p></div><div class="handle">{HANDLE}</div></div>')
    elif m == "papel_f2":
        corpo = f'<div class="slide f2"><div class="texto fit" data-max="62">{paras(s["paragrafos"])}</div><div class="handle">{HANDLE}</div></div>'
    elif m == "preto_f5":
        rot = f'<div class="rotulo">{html.escape(s["rotulo"])}</div>' if s.get("rotulo") else ""
        if s.get("rotulo") and s["paragrafos"]:  # não repetir "Moral:" no texto quando já está no rótulo
            s["paragrafos"][0] = re.sub(rf"^\s*{re.escape(s['rotulo'])}\s*[:\-–]\s*", "", s["paragrafos"][0], flags=re.I)
        corpo = f'<div class="slide f5"><div class="texto fit" data-max="64">{rot}{paras(s["paragrafos"])}</div><div class="handle">{HANDLE}</div></div>'
    elif m == "cta_f6":
        perg = f'<p class="pergunta">{marcar(s["pergunta"])}</p>' if s.get("pergunta") else ""
        corpo = (f'<div class="slide f6"><div class="moldura"></div><div class="texto fit">{perg}{paras(s["paragrafos"])}</div>'
                 f'<div class="siga">Siga {HANDLE}</div><img class="logo" src="{LOGO}"></div>')
    else:
        raise ValueError(m)
    if s.get("credito") and m != "noticia" and corpo.endswith("</div>"):
        corpo = corpo[:-6] + f'<div class="credito">{html.escape(s["credito"])}</div></div>'
    css = CSS.replace("__PAPEL__", PAPEL)
    return _tematizar(f'<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{FONTES}">'
                      f"<style>{css}</style></head><body>{SVG_FILTROS}{corpo}</body></html>")
