"""AGENTE DO PRODUTO (caminho B escolhido pelo dono em 10/11/2026): põe a embalagem REAL na cena, no lugar certo e com realismo.

1. Lugar: acha a parte mais limpa da foto dentro da zona permitida (longe do texto do molde).
2. 3D: desenha a embalagem como objeto 3D (three.js no Chromium do robô) com a arte real do rótulo como textura,
   girada para combinar com a cena. O rótulo fica idêntico (nenhuma IA redesenha o texto).
3. Composição: sombra de contato + sombra projetada suave + leve ajuste de cor à luz da cena.
4. Acabamento IA: a IA integra borda, sombra e luz na cena inteira.
5. Rótulo de volta: os pixels originais do produto são colados de novo por cima (com borda suave), então o rótulo nunca muda.
6. Conferente com visão: produto visível, em pé, sem flutuar, tamanho real, fora do texto. Nota baixa → fica a versão sem IA (passo 3).
"""
import base64, io, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageStat
import robo
from foto_fiel import CAPAS

HTML = Path(__file__).resolve().parent / "assets" / "pacote3d.html"

# zonas permitidas (frações da foto): onde o pé do produto pode ficar
ZONAS = {
    "capa": [(0.56, 0.95, 0.40, 0.60), (0.05, 0.44, 0.40, 0.60)],   # na capa o texto fica embaixo: produto no meio da altura
    "miolo": [(0.56, 0.95, 0.66, 0.92), (0.05, 0.44, 0.66, 0.92)],  # no miolo a foto é livre: produto na superfície de baixo
}


PROIBIDA = {"capa": "a faixa de baixo da foto, de 60% da altura até o fim (é onde vai a frase da capa)", "miolo": "nenhuma"}


def _ch(corpo, timeout=220):
    return robo.chamar(corpo, timeout=timeout, url=CAPAS)


def escolher_lugar(foto: Path, zona="miolo", altura_frac=None):
    """Janela com menos detalhe (menos bordas) dentro das zonas permitidas: é onde a superfície está livre."""
    im = Image.open(foto).convert("L"); W, H = im.size
    bordas = im.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(3))
    alt = int(H * (altura_frac or (0.27 if zona == "capa" else 0.31))); larg = int(alt * 0.72)
    melhor = None
    for (x0, x1, y0, y1) in ZONAS.get(zona, ZONAS["miolo"]):
        for fx in [x0 + (x1 - x0) * t for t in (0.2, 0.5, 0.8)]:
            for fy in [y0 + (y1 - y0) * t for t in (0.0, 0.5, 1.0)]:
                cx, base = int(W * fx), int(H * fy)
                box = (max(0, cx - larg // 2), max(0, base - alt), min(W, cx + larg // 2), min(H, base))
                if box[2] - box[0] < larg * 0.8 or box[3] - box[1] < alt * 0.8:
                    continue
                energia = ImageStat.Stat(bordas.crop(box)).mean[0]
                if melhor is None or energia < melhor[0]:
                    melhor = (energia, cx, base, fx)
    _, cx, base, fx = melhor
    return {"cx": cx, "base_y": base, "altura": alt, "lado": "dir" if fx > 0.5 else "esq"}


def render_3d(textura: Path, destino: Path, ry=-22, rx=3, lx=-1.3):
    from playwright.sync_api import sync_playwright
    asp = Image.open(textura).width / Image.open(textura).height
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--allow-file-access-from-files", "--enable-unsafe-swiftshader"])
        pg = b.new_page(viewport={"width": 900, "height": 1100})
        pg.goto(HTML.as_uri() + f"?w=900&h=1100&ry={ry}&rx={rx}&lx={lx}&ly=2.2&asp={asp:.3f}&tex={textura.resolve().as_uri()}")
        pg.wait_for_function("window.PRONTO===true", timeout=40000); pg.wait_for_timeout(300)
        data = pg.evaluate("document.querySelector('canvas').toDataURL('image/png')")
        b.close()
    im = Image.open(io.BytesIO(base64.b64decode(data.split(",")[1]))).convert("RGBA")
    im = im.crop(im.getbbox()); im.save(destino)
    return im


def compor(foto: Path, prod: Image.Image, lugar, lado_luz="esq"):
    bg = Image.open(foto).convert("RGBA")
    k = lugar["altura"] / prod.height
    pr = prod.resize((max(1, round(prod.width * k)), lugar["altura"]), Image.LANCZOS)
    x = round(lugar["cx"] - pr.width / 2); y = lugar["base_y"] - pr.height; base = lugar["base_y"]
    a = pr.getchannel("A")
    cont = Image.new("L", bg.size, 0)
    ImageDraw.Draw(cont).ellipse([x + pr.width * 0.06, base - pr.height * 0.03, x + pr.width * 0.96, base + pr.height * 0.035], fill=175)
    cont = cont.filter(ImageFilter.GaussianBlur(max(2, pr.width * 0.035)))
    proj = Image.new("L", bg.size, 0)
    sq = a.resize((pr.width, max(1, round(pr.height * 0.2)))).point(lambda v: int(v * 0.5))
    dx = round(pr.width * (0.2 if lado_luz == "esq" else -0.2))
    proj.paste(sq, (x + dx, base - round(sq.height * 0.85)), sq)
    proj = proj.filter(ImageFilter.GaussianBlur(max(3, pr.width * 0.06)))
    tom = Image.new("RGBA", bg.size, (35, 20, 25, 255)); tom.putalpha(ImageChops.lighter(cont, proj))
    out = Image.alpha_composite(bg, tom)
    media = bg.crop((max(0, x), max(0, y), min(bg.width, x + pr.width), min(bg.height, base))).convert("RGB").resize((1, 1)).getpixel((0, 0))
    prc = Image.blend(pr.convert("RGB"), Image.new("RGB", pr.size, media), 0.06).convert("RGBA"); prc.putalpha(a)
    out.alpha_composite(prc, (x, y))
    return out.convert("RGB"), prc, (x, y)


def _subir(img: Image.Image, caminho):
    buf = io.BytesIO(); img.save(buf, "PNG")
    robo.chamar({"acao": "salvar", "caminho": caminho, "base64": base64.b64encode(buf.getvalue()).decode()})


def integrar(foto: Path, produto: dict, base_storage: str, nome: str, zona="miolo", ev=None, acabamento=True):
    """Coloca o produto na foto (sobrescreve `foto`). Devolve um resumo do que foi feito."""
    ev = ev or (lambda *a, **k: None)
    pasta = foto.parent
    original = Image.open(foto).convert("RGB")
    W, H = original.size
    lado_luz = random.choice(["esq", "dir"])
    lugar = None
    try:  # olho de IA: onde existe superfície de verdade para a embalagem ficar em pé
        cam_o = f"{base_storage}/{nome}_orig.png"; _subir(original, cam_o)
        lg = (_ch({"acao": "lugar_produto", "caminho": cam_o, "produto": produto.get("nome", ""),
                   "proibida": PROIBIDA.get(zona, "nenhuma")}).get("lugar") or {})
        if lg and not lg.get("tem_lugar"):
            ev("fotografo", f"Nesta foto não há onde apoiar {produto.get('nome', 'o produto')} de forma crível; deixei sem produto.")
            return {"modo": "sem_lugar", "motivo": lg.get("motivo", "")}
        if lg:
            alt = int(H * min(0.42, max(0.12, float(lg["altura"]))))
            lugar = {"cx": int(W * float(lg["x"])), "base_y": int(H * min(0.98, float(lg["y_base"]))), "altura": alt,
                     "lado": "dir" if float(lg["x"]) > 0.5 else "esq"}
            lado_luz = lg.get("lado_luz", lado_luz)
    except Exception:
        lugar = None
    lugar = lugar or escolher_lugar(foto, zona)
    ry = -24 if lugar["lado"] == "dir" else 24  # a frente vira para o centro da cena
    prod = render_3d(Path(produto["arquivo"]), pasta / f"{nome}_3d.png", ry=ry, lx=-1.3 if lado_luz == "esq" else 1.3)
    comp, prc, (x, y) = compor(foto, prod, lugar, lado_luz)
    comp.save(pasta / f"{nome}_comp.png")
    resumo = {"lugar": lugar, "modo": "3d"}
    final = comp
    if acabamento:
        try:
            vert = comp.height > comp.width
            cam_c, cam_ia = f"{base_storage}/{nome}_comp.png", f"{base_storage}/{nome}_ia.png"
            _subir(comp, cam_c)
            e = _ch({"acao": "editar", "caminho": cam_c, "destino": cam_ia, "size": "1024x1536" if vert else "1536x1024", "quality": "medium",
                     "instrucao": "This photo has a product package standing in the scene. Make it look naturally photographed in this place: "
                                  "realistic contact shadow on the surface, light direction and color temperature matching the room, soft edges, "
                                  "subtle reflections. Do NOT move, resize, redraw or change the package: same position, shape, colors, logo and printed text. "
                                  "Do not add any other package or text. Keep everything else identical."})
            if e.get("ok"):
                robo.baixar(cam_ia, pasta / f"{nome}_ia.png")
                ia = Image.open(pasta / f"{nome}_ia.png").convert("RGB").resize(comp.size, Image.LANCZOS)
                # o rótulo volta por cima, pixel por pixel (borda suave para não aparecer recorte)
                m = prc.getchannel("A").filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
                ia.paste(prc.convert("RGB"), (x, y), m)
                ia.save(pasta / f"{nome}_final.png")
                cam_f = f"{base_storage}/{nome}_final.png"; _subir(ia, cam_f)
                cf = _ch({"acao": "conferir", "caminho": cam_f,
                          "texto": f"A embalagem real de {produto.get('nome', 'produto')} aparece inteira e visível, em pé sobre uma superfície, "
                                   "com sombra coerente, tamanho real em relação à cena, sem flutuar, sem ficar torta, sem duplicar e sem parecer colada.",
                          "cena": {"produto": produto.get("nome", ""), "regra": "julgue só a integração do produto na foto"}})
                nota = (cf.get("conferencia") or {}).get("nota", 0)
                resumo.update({"nota": nota, "defeitos": (cf.get("conferencia") or {}).get("defeitos", [])})
                if nota >= 6:
                    final = ia; resumo["modo"] = "3d+ia"
                elif nota <= 4:  # integração reprovada: melhor sem produto do que produto falso
                    final = original; resumo["modo"] = "reprovado"
        except Exception as x_:
            resumo["erro_acabamento"] = str(x_)[:120]
    final.save(foto)
    if resumo["modo"] == "reprovado":
        ev("fotografo", f"O conferente reprovou o produto nesta foto (nota {resumo.get('nota')}); deixei a foto sem produto.")
    else:
        ev("fotografo", f"Coloquei {produto.get('nome', 'o produto')} em 3D com o rótulo real"
           + (f" e a IA integrou na cena (nota {resumo.get('nota')})." if resumo["modo"] == "3d+ia" else " (versão sem acabamento de IA)."))
    return resumo
