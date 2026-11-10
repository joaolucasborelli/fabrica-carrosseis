"""Robô montador. Roda no GitHub Actions (a cada 5 min) ou no PC.
1. pede a fila ao `montador` (Supabase)
2. para cada post: diagramar (IA) -> foto da capa (IA) -> desenha os slides (Chromium) -> envia -> concluir
Identidade: no GitHub usa o token OIDC do próprio repositório (nenhum segredo guardado);
no PC usa o código da carga (variável MONTADOR_CARGA_ARQ aponta o arquivo; o valor nunca é impresso).
"""
import base64, json, os, sys, time, urllib.request, urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

URL = "https://kfvugtrjuqdakbpzvsxq.supabase.co/functions/v1/montador"
AUD = "fabrica-montador"
SAIDA = Path(os.environ.get("MONTADOR_SAIDA", Path(__file__).resolve().parent / "_saida"))


def _cabecalho():
    if os.environ.get("ACTIONS_ID_TOKEN_REQUEST_URL"):
        req = urllib.request.Request(os.environ["ACTIONS_ID_TOKEN_REQUEST_URL"] + f"&audience={AUD}",
                                     headers={"Authorization": "Bearer " + os.environ["ACTIONS_ID_TOKEN_REQUEST_TOKEN"]})
        with urllib.request.urlopen(req, timeout=30) as r:
            return {"x-github-oidc": json.loads(r.read())["value"]}
    arq = os.environ.get("MONTADOR_CARGA_ARQ")
    if arq and Path(arq).exists():
        return {"x-carga": Path(arq).read_text().strip()}
    raise SystemExit("sem identidade: rode no GitHub Actions ou defina MONTADOR_CARGA_ARQ")


_CAB = None


def chamar(corpo, timeout=200, url=None):
    global _CAB
    if _CAB is None or "x-github-oidc" in _CAB and time.time() - _CAB.get("_t", 0) > 240:
        _CAB = _cabecalho(); _CAB["_t"] = time.time()
    cab = {k: v for k, v in _CAB.items() if k != "_t"}
    req = urllib.request.Request(url or URL, data=json.dumps(corpo).encode(), method="POST",
                                 headers={"Content-Type": "application/json", **cab})
    for tentativa in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            res = {"ok": False, "status": e.code, "erro": e.read().decode(errors="replace")[:600]}
            if e.code < 500 or corpo.get("acao") in ("diagramar", "fila") or "créditos" in res["erro"] or "credits" in res["erro"].lower():
                return res
            # foto: tenta de novo em erro passageiro da OpenAI (página de erro, 5xx), mas não quando foi barrada por segurança
            if corpo.get("acao") == "imagem" and (tentativa >= 2 or any(k in res["erro"].lower() for k in ("safety", "moderation", "policy"))):
                return res
        except (urllib.error.URLError, TimeoutError) as e:
            res = {"ok": False, "erro": str(e)}
        time.sleep(3 * (tentativa + 1))
    return res


EVENTOS = "https://kfvugtrjuqdakbpzvsxq.supabase.co/functions/v1/eventos"


def evento(post_id, agente, fala, estado="trabalhando", **detalhe):
    """O agente avisa o que está fazendo (aparece ao vivo no escritório dentro do post). Nunca derruba a montagem."""
    if not post_id:
        return
    try:
        chamar({"post_id": post_id, "agente": agente, "fala": fala, "estado": estado, "detalhe": detalhe}, timeout=20, url=EVENTOS)
    except Exception:
        pass


def baixar(caminho, destino: Path):
    r = chamar({"acao": "baixar", "caminho": caminho})
    if not r.get("ok"):
        raise RuntimeError(f"baixar {caminho}: {r}")
    urllib.request.urlretrieve(r["url"], destino)


ROTEIRO = "https://kfvugtrjuqdakbpzvsxq.supabase.co/functions/v1/roteiro"


def entregar(post_id, arquivos, passos, t0, ev):
    ev("entregador", "Guardando os slides no banco e mandando para a sua tela.")
    caminhos = []
    for i, arq in enumerate(arquivos, 1):
        c = f"post_{post_id}/slide_{i:02d}.png"
        r = chamar({"acao": "salvar", "caminho": c, "base64": base64.b64encode(Path(arq).read_bytes()).decode()})
        if not r.get("ok"):
            raise RuntimeError(f"salvar {c}: {r}")
        caminhos.append(c)
    passos.append(f"{len(caminhos)} slides em {time.time()-t0:.0f}s")
    chamar({"acao": "concluir", "post_id": post_id, "imagens": caminhos, "log": " · ".join(passos)})
    ev("entregador", f"Entregue! {len(caminhos)} slides prontos no post em {time.time()-t0:.0f}s.", "pronto")
    return passos


def montar(post_id: int):
    """Caminho novo (kit 2 + receitas). Se a diagramação perder frases do texto aprovado, cai no caminho antigo."""
    import kit
    t0 = time.time(); passos = []
    ev = lambda agente, fala, estado="trabalhando", **k: evento(post_id, agente, fala, estado, **k)
    ev("diagramador", "Peguei o texto aprovado. Vou escolher a receita e os moldes do kit para cada slide, sem mudar as frases.")
    melhor = None
    for tentativa in range(2):
        d = chamar({"acao": "diagramar", "post_id": post_id}, timeout=220, url=ROTEIRO)
        if not d.get("ok"):
            continue
        cob = kit.cobertura(d["pecas"], d["post"])
        if not melhor or cob > melhor[0]:
            melhor = (cob, d["post"])
        if cob >= 0.97:
            break
        ev("diagramador", f"Conferi: {cob:.0%} das palavras do texto aprovado apareceram. Vou refazer para não perder nenhuma frase.")
    if not melhor or melhor[0] < 0.93:
        ev("diagramador", "A diagramação nova perdeu frases do texto. Vou usar o jeito antigo, que é seguro.", "pronto")
        return montar_antigo(post_id)
    cob, post = melhor
    nomes = sorted({s["molde"] for s in post["slides"]})
    ev("diagramador", f"Pronto: receita {post['receita'][:40]}, capa {post['capa']['molde']}, {len(post['slides'])+1} slides, {len(nomes)} moldes diferentes. "
                      f"Conferi: {cob:.0%} das palavras aprovadas estão lá.", "pronto")
    passos.append(f"kit · {post['receita'][:30]} · cobertura {cob:.0%}")
    pasta = SAIDA / f"post_{post_id}"
    import moldes; moldes.usar_marca(post.get("marca"))
    arquivos = kit.montar(post, pasta, f"post_{post_id}/kit", ev=ev, log=passos.append)
    return entregar(post_id, arquivos, passos, t0, ev)


def montar_antigo(post_id: int):
    from render import renderizar  # só carrega o navegador quando vai desenhar
    t0 = time.time(); passos = []
    ev = lambda agente, fala, estado="trabalhando", **k: evento(post_id, agente, fala, estado, **k)
    ev("diagramador", "Peguei o texto aprovado. Vou dividir em slides e escolher o molde de cada um.")
    d = chamar({"acao": "diagramar", "post_id": post_id})
    if not d.get("ok"):
        ev("diagramador", "Não consegui diagramar. Avisei o erro.", "erro")
        raise RuntimeError(f"diagramar: {d}")
    ficha = d["ficha"]; passos.append(f"diagramado por {ficha.get('modelo')} {d.get('log') or ''}".strip())
    conf = ficha.get("conferencia") or {}
    ev("diagramador", f"Pronto: {len(ficha['slides'])} slides. " + ("Conferi palavra por palavra: nenhuma mudou." if conf.get("ok") else "Usei a diagramação de reserva."), "pronto",
       slides=len(ficha["slides"]))
    from foto_fiel import foto_fiel  # diretor de cena -> foto -> conferente (visão) -> correção
    capa = next((s for s in ficha["slides"] if s["molde"].startswith("capa_")), ficha["slides"][0])
    ff = foto_fiel(capa.get("texto", ""), capa["molde"], ficha.get("foto_prompt", ""), f"post_{post_id}/foto", log=lambda *_: None, ev=ev)
    passos.append(f"foto conferida nota {ff['nota']} ({len(ff['historico'])} conferências)")
    pasta = SAIDA / f"post_{post_id}"; pasta.mkdir(parents=True, exist_ok=True)
    foto = pasta / "foto.png"; baixar(ff["melhor"], foto)
    slides = ficha["slides"]
    for s in slides:
        if s["molde"] == "capa_f1":
            s["foto"] = foto.resolve().as_uri(); s["foco"] = ficha.get("foco")
    ev("montador", f"Desenhando os {len(slides)} slides em 1080×1350 com os moldes dos vencedores.")
    feitos = renderizar(slides, pasta)
    ev("montador", f"{len(feitos)} slides desenhados. Conferi se nenhum texto ficou cortado.", "pronto")
    ev("entregador", "Guardando os slides no banco e mandando para a sua tela.")
    caminhos = []
    for f in feitos:
        c = f"post_{post_id}/slide_{f['slide']:02d}.png"
        b64 = base64.b64encode(Path(f["arquivo"]).read_bytes()).decode()
        r = chamar({"acao": "salvar", "caminho": c, "base64": b64})
        if not r.get("ok"):
            raise RuntimeError(f"salvar {c}: {r}")
        caminhos.append(c)
    encolhidos = [f["slide"] for f in feitos if any(x > 6 for x in f["encolheu"])]
    if encolhidos:
        passos.append(f"texto apertado nos slides {encolhidos}")
    passos.append(f"{len(caminhos)} slides em {time.time()-t0:.0f}s")
    chamar({"acao": "concluir", "post_id": post_id, "imagens": caminhos, "log": " · ".join(passos)})
    ev("entregador", f"Entregue! {len(caminhos)} slides prontos no post em {time.time()-t0:.0f}s.", "pronto")
    return passos


OPCOES = "https://kfvugtrjuqdakbpzvsxq.supabase.co/functions/v1/opcoes"
# só capas aprovadas como preset pelo dono (10/11) que funcionam com 1 foto + o texto aprovado
ALTERNATIVAS = ["capa_f1", "capa_f1b", "capa_f3a", "capa_perfil"]


def capas_alternativas(p):
    """Gera 3 capas em moldes diferentes da atual, com o mesmo texto aprovado e foto conferida."""
    import kit
    from foto_fiel import foto_fiel
    from render import renderizar
    from concurrent.futures import ThreadPoolExecutor
    post_id = p["id"]; ficha = p.get("ficha") or {}
    import moldes; moldes.usar_marca(ficha.get("marca"))
    ev = lambda agente, fala, estado="trabalhando", **k: evento(post_id, agente, fala, estado, **k)
    capa = (ficha.get("capa") if ficha.get("kit") else None) or {}
    texto = capa.get("texto") or ((p.get("variacoes") or {}).get("pecas") or {}).get("capa", "")
    atual = capa.get("molde") or "capa_f1"
    pers = ficha.get("personagem", "") if ficha.get("kit") else ""
    ideia = (capa.get("foto_prompt") or ficha.get("foto_prompt") or "") + (f" Main character: {pers}." if pers else "")
    moldes = [m for m in ALTERNATIVAS if m != atual][:3]
    ev("diretor", f"Você pediu outras capas. Vou montar 3 versões: {', '.join(moldes)}, com o mesmo texto aprovado.")
    pasta = SAIDA / f"post_{post_id}" / "capas"; pasta.mkdir(parents=True, exist_ok=True)

    def uma(i_m):
        i, m = i_m
        vert = m in ("capa_f3a", "capa_f3b", "capa_marcatexto")
        ff = foto_fiel(texto, m, ideia, f"post_{post_id}/opc{i}", vertical=vert, log=lambda *_: None, ev=ev)
        loc = pasta / f"foto{i}.png"; baixar(ff["melhor"], loc)
        s = {"molde": m, "foto": loc.resolve().as_uri(), "texto": texto}
        if m == "capa_marcatexto":
            s["texto"] = texto.replace(". ", ".\n", 1)
        f = renderizar([s], pasta / f"r{i}")[0]
        cam = f"post_{post_id}/capa_opc_{int(time.time())}_{i}.png"
        chamar({"acao": "salvar", "caminho": cam, "base64": base64.b64encode(Path(f["arquivo"]).read_bytes()).decode()})
        return {"molde": m, "imagem": cam}
    with ThreadPoolExecutor(3) as ex:
        opcoes = list(ex.map(uma, enumerate(moldes, 1)))
    chamar({"acao": "salvar", "post_id": post_id, "opcoes": opcoes}, url=OPCOES)
    ev("entregador", f"{len(opcoes)} capas novas prontas. Abra 'Gerar capas' no post e clique na que quiser.", "pronto")


VERT_CAPA = ("capa_f3a", "capa_f3b", "capa_circulos", "capa_marcatexto", "capa_numero")


def _existe(caminho):
    return bool(chamar({"acao": "baixar", "caminho": caminho}).get("ok"))


def retocar(p):
    """O dono pediu para corrigir a foto de um slide: edita só essa foto, redesenha só esse slide e devolve."""
    import kit
    from render import renderizar
    post_id = p["id"]; ficha = p.get("ficha") or {}; imgs = list(p.get("imagens") or [])
    fotos = p.get("fotos_retocadas") or {}
    import moldes; moldes.usar_marca(ficha.get("marca"))
    ev = lambda agente, fala, estado="trabalhando", **k: evento(post_id, agente, fala, estado, **k)
    pasta = SAIDA / f"post_{post_id}" / "retoques"; pasta.mkdir(parents=True, exist_ok=True)
    feitos = []
    for r in p["retoques"]:
        n = int(r["slide"])
        try:
            if not ficha.get("kit"):
                raise RuntimeError("este post foi montado no jeito antigo; peça para remontar o post inteiro")
            s = ficha["capa"] if n == 1 else (ficha["slides"][n - 2] if n - 2 < len(ficha["slides"]) else None)
            if not s:
                raise RuntimeError("não achei esse slide na ficha do post")
            molde = s["molde"]
            if molde == "antes_hoje":
                raise RuntimeError("slide de antes e hoje tem 2 fotos; por enquanto o retoque só corrige slides de 1 foto")
            # a foto de origem: a última já retocada deste slide, senão a foto original da montagem
            fonte = fotos.get(str(n))
            if not fonte:
                if n == 1:
                    fonte = next((f"post_{post_id}/kit/capa_v{v}.png" for v in (3, 2, 1, 0) if _existe(f"post_{post_id}/kit/capa_v{v}.png")), None)
                    fonte = fonte or (f"post_{post_id}/kit/capa.png" if _existe(f"post_{post_id}/kit/capa.png") else None)
                else:
                    c = f"post_{post_id}/kit/s{n:02d}.png"
                    fonte = c if _existe(c) else None
            if not fonte:
                raise RuntimeError("este slide não tem foto de IA para corrigir (é slide só de texto ou usa foto real de arquivo)")
            vert = molde in VERT_CAPA if n == 1 else molde in kit.VERTICAIS
            ev("retocador", f"Corrigindo a foto do slide {n}: {r['pedido'][:140]}")
            novo = f"post_{post_id}/kit/retoque_{r['id']}.png"
            e = kit._ch(kit.CAPAS, {"acao": "editar", "caminho": fonte, "destino": novo, "size": "1024x1536" if vert else "1536x1024",
                                    "instrucao": "Keep everything else exactly the same: same people, faces, clothes, place, light, colors and framing. "
                                                 "Change only what the owner asked (in Portuguese): " + r["pedido"]})
            if not e.get("ok"):
                raise RuntimeError(f"a edição da foto falhou: {str(e.get('erro', e))[:200]}")
            loc = pasta / f"foto_{r['id']}.png"; baixar(novo, loc)
            d = kit.desenho(s, eh_capa=(n == 1))
            d["foto"] = loc.resolve().as_uri()
            if n == 1 and molde == "capa_circulos" and _existe(f"post_{post_id}/kit/circulo.png"):
                cl = pasta / "circulo.png"; baixar(f"post_{post_id}/kit/circulo.png", cl); d["fotos_circulo"] = [cl.resolve().as_uri()]
            ev("montador", f"Redesenhando só o slide {n} com a foto corrigida.")
            f = renderizar([d], pasta / f"r{r['id']}")[0]
            cam = f"post_{post_id}/slide_{n:02d}_r{r['id']}.png"
            chamar({"acao": "salvar", "caminho": cam, "base64": base64.b64encode(Path(f["arquivo"]).read_bytes()).decode()})
            feitos.append({"id": r["id"], "slide": n, "imagem": cam, "foto": novo})
            fotos[str(n)] = novo
            ev("entregador", f"Slide {n} corrigido. Se não gostar, dá para desfazer no post.", "pronto")
        except Exception as e:
            print(post_id, "retoque", r["id"], "ERRO", e)
            msg = "a OpenAI está sem créditos: recarregue e peça a correção de novo" if "credits" in str(e).lower() else str(e)[:300]
            ev("retocador", f"Não consegui corrigir o slide {n}: {msg[:160]}", "erro")
            feitos.append({"id": r["id"], "erro": msg})
    chamar({"acao": "salvar", "post_id": post_id, "retoques": feitos}, url=OPCOES)


def main():
    if "--contar" in sys.argv:  # usado pelo GitHub para não instalar o navegador à toa
        c = chamar({"acao": "contar"})
        n = c.get("pendentes", 0) if c.get("ok") else 0
        c2 = chamar({"acao": "contar"}, url=OPCOES)
        n += c2.get("pendentes", 0) if c2.get("ok") else 0
        print("pendentes:", n if c.get("ok") else c)
        if os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write(f"pendentes={n}\n")
        return
    fila =chamar({"acao": "fila", "limite": int(os.environ.get("MONTADOR_LIMITE", "3"))})
    posts = fila.get("posts", [])
    print("fila:", posts if fila.get("ok") else fila)
    for pid in posts:
        try:
            print(pid, montar(pid))
        except Exception as e:  # registra o erro no post e segue
            print(pid, "ERRO", e)
            evento(pid, "entregador", f"Deu erro na montagem: {str(e)[:160]}", "erro")
            chamar({"acao": "erro", "post_id": pid, "log": str(e)})
    fc = chamar({"acao": "fila"}, url=OPCOES)
    for p in fc.get("posts", []) if fc.get("ok") else []:
        try:
            if p.get("retoques"):
                retocar(p); print(p["id"], "retoques ok"); continue
            capas_alternativas(p); print(p["id"], "capas alternativas ok")
        except Exception as e:
            print(p["id"], "ERRO capas", e)
            evento(p["id"], "entregador", f"Deu erro nas capas novas: {str(e)[:160]}", "erro")
            chamar({"post_id": p["id"], "erro": str(e)[:300], "acao": "salvar"}, url=OPCOES)


if __name__ == "__main__":
    main()
