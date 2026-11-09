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


def chamar(corpo, timeout=200):
    global _CAB
    if _CAB is None or "x-github-oidc" in _CAB and time.time() - _CAB.get("_t", 0) > 240:
        _CAB = _cabecalho(); _CAB["_t"] = time.time()
    cab = {k: v for k, v in _CAB.items() if k != "_t"}
    req = urllib.request.Request(URL, data=json.dumps(corpo).encode(), method="POST",
                                 headers={"Content-Type": "application/json", **cab})
    for tentativa in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            res = {"ok": False, "status": e.code, "erro": e.read().decode(errors="replace")[:600]}
            if e.code < 500 or corpo.get("acao") in ("diagramar", "imagem", "fila"):
                return res
        except (urllib.error.URLError, TimeoutError) as e:
            res = {"ok": False, "erro": str(e)}
        time.sleep(3 * (tentativa + 1))
    return res


def baixar(caminho, destino: Path):
    r = chamar({"acao": "baixar", "caminho": caminho})
    if not r.get("ok"):
        raise RuntimeError(f"baixar {caminho}: {r}")
    urllib.request.urlretrieve(r["url"], destino)


def montar(post_id: int):
    from render import renderizar  # só carrega o navegador quando vai desenhar
    t0 = time.time(); passos = []
    d = chamar({"acao": "diagramar", "post_id": post_id})
    if not d.get("ok"):
        raise RuntimeError(f"diagramar: {d}")
    ficha = d["ficha"]; passos.append(f"diagramado por {ficha.get('modelo')} {d.get('log') or ''}".strip())
    img = chamar({"acao": "imagem", "post_id": post_id})
    if not img.get("ok"):
        raise RuntimeError(f"imagem: {img}")
    passos.append(f"foto {img.get('modelo')} em {img.get('segundos')}s")
    pasta = SAIDA / f"post_{post_id}"; pasta.mkdir(parents=True, exist_ok=True)
    foto = pasta / "foto.png"; baixar(img["caminho"], foto)
    slides = ficha["slides"]
    for s in slides:
        if s["molde"] == "capa_f1":
            s["foto"] = foto.resolve().as_uri(); s["foco"] = ficha.get("foco")
    feitos = renderizar(slides, pasta)
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
    return passos


def main():
    if "--contar" in sys.argv:  # usado pelo GitHub para não instalar o navegador à toa
        c = chamar({"acao": "contar"})
        n = c.get("pendentes", 0) if c.get("ok") else 0
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
            chamar({"acao": "erro", "post_id": pid, "log": str(e)})


if __name__ == "__main__":
    main()
