"""Moldes visuais da fábrica (F1, F2, F5, F6 do estudo dna_visual.md), em HTML/CSS para 1080x1350.

Cada slide é um dict: {"molde": "capa_f1" | "papel_f2" | "preto_f5" | "cta_f6", ...campos}
Marcação no texto: **palavra** = marca-texto amarelo; [[PALAVRA]] = carimbo da palavra do CTA.
"""
import html, re
from pathlib import Path

LOGO = (Path(__file__).resolve().parent / "assets" / "logo-horizontal.svg").as_uri()
AVATAR = (Path(__file__).resolve().parent / "assets" / "logo-perfil.svg").as_uri()
HANDLE = "@ahistoriaquemuda"

PORTA = ('<svg class="emblema" viewBox="380 280 280 560" aria-hidden="true">'
         '<rect x="470" y="300" width="170" height="512" fill="#FFD21F"/>'
         '<polygon points="470,300 392,338 392,850 470,812" fill="#262626" stroke="#F5F5F0" stroke-width="10" stroke-linejoin="round"/>'
         '<rect x="458" y="288" width="194" height="536" fill="none" stroke="#F5F5F0" stroke-width="18" stroke-linejoin="round"/></svg>')

FONTES = ("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Bebas+Neue&family=Barlow+Condensed:wght@500;600;700"
          "&family=Archivo:wdth,wght@62..125,500..900&family=Bitter:wght@400;600"
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

/* F1b · portal: foto em cima, divisor com emblema, manchete em caixa alta condensada com palavras amarelas */
.f1b{background:#0b0b0b}
.f1b .foto{position:absolute;left:0;top:0;width:1080px;height:1000px;object-fit:cover;object-position:var(--foco,50% 50%);filter:contrast(1.04) saturate(.95);
  -webkit-mask-image:linear-gradient(to bottom,#000 0,#000 640px,rgba(0,0,0,.6) 820px,transparent 990px);mask-image:linear-gradient(to bottom,#000 0,#000 640px,rgba(0,0,0,.6) 820px,transparent 990px)}
.f1b .grao{position:absolute;inset:0;background-image:url("__PAPEL__");opacity:.10;mix-blend-mode:overlay}
.f1b .divisor{position:absolute;left:150px;right:150px;top:968px;height:64px;display:flex;align-items:center;gap:26px}
.f1b .divisor i{flex:1;height:2px;background:rgba(255,255,255,.7)}
.f1b .emblema{width:34px;height:64px}
.f1b .texto{position:absolute;left:70px;right:70px;top:1046px;height:200px;display:flex;align-items:center;justify-content:center}
.f1b .texto p{font:400 104px/.98 'Bebas Neue',sans-serif;letter-spacing:.005em;color:#fff;text-align:center;text-transform:uppercase;text-wrap:balance}
.f1b .texto p .am{color:#FFD21F}
.f1b .arraste{position:absolute;left:0;right:0;top:1276px;text-align:center;font:600 25px/1 'Barlow Condensed',sans-serif;letter-spacing:.06em;color:rgba(255,255,255,.85);text-transform:uppercase}
.f1b .arraste b{color:#FFD21F;font-weight:700}
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
.perfil .texto{position:absolute;left:56px;right:56px;top:972px;height:280px;display:flex;align-items:center;justify-content:center}
.perfil .texto p{font:400 92px/.98 'Bebas Neue',sans-serif;color:#fff;text-align:center;text-transform:uppercase;text-wrap:balance}
.perfil .texto p .am{color:#FFD21F}
.perfil .arraste{position:absolute;left:0;right:0;top:1282px;text-align:center;font:600 26px/1 'Barlow Condensed',sans-serif;letter-spacing:.06em;color:#fff;text-transform:uppercase}

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
.esc.cd .cards{position:absolute;left:44px;right:44px;top:360px;bottom:150px;display:flex;flex-direction:column;justify-content:center;gap:22px}
.esc.cd .card{display:flex;align-items:center;gap:26px;background:#141416;border:2px solid #2a2a2e;border-radius:22px;padding:24px 30px;min-height:122px}
.esc.cd .card .n{font:400 70px/1 'Bebas Neue',sans-serif;color:#FFD21F;width:70px}
.esc.cd .card .ic{width:84px;height:84px;border-radius:18px;object-fit:cover;flex:none}
.esc.cd .card b{font:700 38px/1.15 'Inter',sans-serif;color:#fff;flex:0 0 300px}
.esc.cd .card span{flex:1;border-left:2px solid #3a3a3e;padding-left:24px;font:400 31px/1.3 'Inter',sans-serif;color:#d7d7d3}
/* checklist + foto */
.esc.ck .tit{top:110px;font-size:112px}
.esc.ck .sub{top:232px;font-weight:700;color:#fff}
.esc.ck .sub u{text-decoration:none;border-bottom:3px solid #FFD21F;padding-bottom:6px}
.esc.ck .corpo{position:absolute;left:60px;right:60px;top:320px;bottom:150px;display:flex;flex-direction:column;gap:44px}
.esc.ck .itens{display:flex;flex-direction:column;gap:26px}
.esc.ck .corpo .moldura{position:relative;left:auto;right:auto;top:auto;height:auto;flex:1;min-height:380px}
.esc.ck .it{display:flex;gap:22px;font:400 38px/1.3 'Inter',sans-serif;color:#f2f2ef}
.esc.ck .it::before{content:"✓";flex:none;width:44px;height:44px;margin-top:4px;border-radius:9px;background:#FFD21F;color:#111;font:800 30px/44px 'Inter',sans-serif;text-align:center}
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
.ah .meia{position:absolute;left:0;right:0;height:560px;overflow:hidden}
.ah .meia img{width:100%;height:100%;object-fit:cover;object-position:var(--foco,50% 40%)}
.ah .m1{top:0}.ah .m2{top:566px}
.ah .rot{position:absolute;left:40px;top:34px;font:400 64px/1 'Bebas Neue',sans-serif;padding:10px 20px 6px;border-radius:8px}
.ah .m1 .rot{background:rgba(17,17,17,.88);color:#F5F5F0}.ah .m2 .rot{background:#FFD21F;color:#111}
.ah .texto{position:absolute;left:70px;right:70px;top:1140px;height:150px;display:flex;align-items:center;justify-content:center}
.ah .texto p{font:700 44px/1.2 'Inter',sans-serif;color:#F5F5F0;text-align:center}
/* miolo · lista com linhas sobre foto escura */
.ll{background:#0b0b0b}
.ll .foto{position:absolute;inset:0;width:1080px;height:1350px;object-fit:cover;filter:brightness(.6)}
.ll .veu{position:absolute;inset:0;background:rgba(10,10,10,.82)}
.ll .chapeu{position:absolute;left:84px;top:150px;display:flex;align-items:center;gap:16px;font:800 28px/1 'Archivo',sans-serif;letter-spacing:.22em;color:#FFD21F;text-transform:uppercase}
.ll .chapeu::before{content:"";width:40px;height:4px;background:#FFD21F}
.ll .tit{position:absolute;left:84px;right:84px;top:205px;font:400 116px/.95 'Bebas Neue',sans-serif;color:#fff;text-transform:uppercase}
.ll .linhas{position:absolute;left:84px;right:84px;top:var(--ly,470px);bottom:150px;display:flex;flex-direction:column;justify-content:center}
.ll .lin{display:flex;align-items:center;gap:30px;min-height:120px;border-bottom:2px solid rgba(255,255,255,.28)}
.ll .lin b{font:400 64px/1 'Bebas Neue',sans-serif;color:#FFD21F;width:64px}
.ll .lin span{font:500 38px/1.25 'Inter',sans-serif;color:#fff}
.ll .barra{position:absolute;left:0;bottom:0;height:10px;background:#FFD21F}
.ll .handle{color:#cfcfcb;top:1290px}
/* miolo · conta visual */
.cv{background:#111}
.cv .tit{position:absolute;left:70px;right:70px;top:110px;text-align:center;font-size:104px;color:#F5F5F0}
.cv .conta{position:absolute;left:110px;right:110px;top:300px;bottom:170px;display:flex;flex-direction:column;justify-content:center;align-items:stretch;gap:10px}
.cv .cx{background:#1b1d22;border:2px solid #2c2f36;border-radius:22px;padding:22px 34px;display:flex;align-items:baseline;justify-content:space-between;gap:20px}
.cv .cx b{font:900 72px/1 'Archivo',sans-serif;font-stretch:80%;color:#F5F5F0}
.cv .cx span{font:500 30px/1.2 'Inter',sans-serif;color:#b8bcc4;text-align:right}
.cv .op{text-align:center;font:800 46px/1 'Inter',sans-serif;color:#FFD21F}
.cv .cx.fim{background:#FFD21F;border-color:#FFD21F}.cv .cx.fim b,.cv .cx.fim span{color:#111}
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
.f3a .texto{position:absolute;left:190px;right:190px;top:330px;height:420px;display:flex;align-items:center;justify-content:center}
.f3a .texto p{font:500 46px/1.28 'Inter',sans-serif;color:#fff;text-align:center;text-shadow:0 2px 14px rgba(0,0,0,.55);text-wrap:balance}
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
  for (const t of document.querySelectorAll('.esc .tit')) {
    t.style.whiteSpace = 'nowrap'; let fs = parseFloat(getComputedStyle(t).fontSize), g = 0;
    while (t.scrollWidth > t.clientWidth + 1 && fs > 62 && g++ < 60) { fs *= 0.96; t.style.fontSize = fs + 'px'; }
    if (t.scrollWidth > t.clientWidth + 1) { t.style.whiteSpace = 'normal'; t.dataset.duas = '1'; }
  }
  // se o título quebrou em 2 linhas, empurra o resto do slide para baixo
  for (const s of document.querySelectorAll('.esc')) {
    const t = s.querySelector('.tit'); if (!t || !t.dataset.duas) continue;
    const extra = t.getBoundingClientRect().height - parseFloat(getComputedStyle(t).fontSize) * 1.0;
    for (const el of s.querySelectorAll('.sub, .cards, .corpo, .itens, .lista, .rede, .moldura')) {
      if (el.closest('.corpo') && el !== s.querySelector('.corpo')) continue;
      el.style.top = (parseFloat(getComputedStyle(el).top) + extra) + 'px';
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
})();
"""

SVG_FILTROS = """<svg width="0" height="0" style="position:absolute"><filter id="aspero">
<feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" result="t"/>
<feDisplacementMap in="SourceGraphic" in2="t" scale="3"/></filter></svg>"""


def marcar(txt: str, cor: bool = False) -> str:
    t = html.escape(txt, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r'<span class="am">\1</span>' if cor else r"<mark>\1</mark>", t)
    t = re.sub(r"\[\[(.+?)\]\]", r'<span class="carimbo">\1</span>', t)
    return t


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
    tit = marcar(s.get("titulo", ""), cor=False).replace("<mark>", "<u>").replace("</mark>", "</u>")
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
    return (f'<div class="slide ah"><div class="meia m1"><img src="{f1}"><div class="rot">{html.escape(r1)}</div></div>'
            f'<div class="meia m2"><img src="{f2}"><div class="rot">{html.escape(r2)}</div></div>'
            f'<div class="texto fit"><p>{marcar(s.get("texto",""))}</p></div></div>')


def _k_lista(s):
    lins = "".join(f'<div class="lin"><b>{i}</b><span>{marcar(t)}</span></div>' for i, t in enumerate(s.get("itens") or [], 1))
    fundo = f'<img class="foto" src="{s["foto"]}">' if s.get("foto") else ""
    prog = s.get("progresso") or 0
    return (f'<div class="slide ll">{fundo}<div class="veu"></div><div class="chapeu">{html.escape(s.get("chapeu",""))}</div>'
            f'<div class="tit">{marcar(s.get("titulo",""), cor=True)}</div><div class="linhas">{lins}</div>'
            f'<div class="barra" style="width:{max(0,min(1,prog))*100:.0f}%"></div><div class="handle">{HANDLE}</div></div>')


def _k_conta(s):
    partes = []
    for i, c in enumerate(s.get("caixas") or []):
        if i and c.get("op"):
            partes.append(f'<div class="op">{html.escape(c["op"])}</div>')
        partes.append(f'<div class="cx{" fim" if c.get("fim") else ""}"><b>{html.escape(c["valor"])}</b><span>{html.escape(c.get("rotulo",""))}</span></div>')
    return (f'<div class="slide cv"><div class="tit cond">{marcar(s.get("titulo",""), cor=True)}</div><div class="conta">{"".join(partes)}</div>{_assin()}</div>')


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


def _normalizar(s: dict) -> dict:
    s = dict(s)
    ps = [p for p in (s.get("paragrafos") or []) if p and p.strip()]
    if not ps and s.get("texto") and not s["molde"].startswith("capa_"):
        ps = [p.strip() for p in re.split(r"\n\s*\n|\n", s["texto"]) if p.strip()]
    s["paragrafos"] = ps
    if s["molde"].startswith("capa_") and not s.get("texto"):
        s["texto"] = " ".join(ps)
    return s


def slide_html(s: dict) -> str:
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
                 f'<div class="texto fit"><p>{marcar(s["texto"], cor=True)}</p></div>'
                 f'<div class="arraste">Arrasta pro lado <b>&gt;&gt;&gt;&gt;</b></div></div>')
    elif m == "capa_perfil":
        foco = html.escape(s.get("foco") or "50% 40%")
        corpo = (f'<div class="slide perfil"><img class="foto" src="{s["foto"]}" style="--foco:{foco}"><div class="grao"></div>'
                 f'<div class="divisor"><i></i><div class="chip"><img src="{AVATAR}"><div><b>A História que Muda</b><span>{HANDLE}</span></div></div><i></i></div>'
                 f'<div class="texto fit"><p>{marcar(s["texto"], cor=True)}</p></div><div class="arraste">Deslize e veja &gt;&gt;&gt;</div></div>')
    elif m == "capa_comparacao":
        foco = html.escape(s.get("foco") or "50% 45%")
        e, d = (s.get("rotulos") or ["Antes", "Depois"])[:2]
        corpo = (f'<div class="slide comp"><img class="foto" src="{s["foto"]}" style="--foco:{foco}"><div class="corte"></div>'
                 f'<div class="rot e">{html.escape(e)}</div><div class="rot d">{html.escape(d)}</div>'
                 f'<div class="texto fit" data-max="80"><p>{marcar(s["texto"])}</p></div><div class="handle">{HANDLE}</div></div>')
    elif m == "capa_tweet":
        foco = html.escape(s.get("foco") or "50% 45%")
        ps = [p.strip() for p in re.split(r"\n+", s["texto"]) if p.strip()]
        corpo = (f'<div class="slide tw"><div class="topo"><img src="{AVATAR}"><div><b>A História que Muda</b><span>{HANDLE}</span></div></div>'
                 f'<div class="texto fit" data-max="66">{paras(ps)}</div><div class="img"><img src="{s["foto"]}" style="--foco:{foco}"></div></div>')
    elif m == "capa_tweet2":
        ps = [p.strip() for p in re.split(r"\n+", s["texto"]) if p.strip()]
        f1, f2 = (s.get("fotos") or [s.get("foto"), s.get("foto")])[:2]
        corpo = (f'<div class="slide tw tw2"><div class="topo"><img src="{AVATAR}"><div><b>A História que Muda</b><span>{HANDLE}</span></div></div>'
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
    css = CSS.replace("__PAPEL__", PAPEL)
    return (f'<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{FONTES}">'
            f"<style>{css}</style></head><body>{SVG_FILTROS}{corpo}</body></html>")
