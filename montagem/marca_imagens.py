"""Gera as imagens da marca (logos e clima) pedidas em automacao/marca/pedidos.json, pelo montador (OIDC do GitHub, sem segredo guardado).
Cada imagem entra na tabela custos (funcao montador, etapa foto). Para no teto do dia (o montador confere)."""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import robo

pedidos = json.loads((Path(__file__).resolve().parent.parent / "automacao" / "marca" / "pedidos.json").read_text(encoding="utf-8"))
limite = float(pedidos.get("limite_usd", 1.5))
feitos = []
for p in pedidos["imagens"]:
    r = robo.chamar({"acao": "imagem", "prompt": p["prompt"], "caminho": p["caminho"], "size": p.get("size", "1024x1024"), "quality": p.get("quality", "medium")}, timeout=300)
    print(p["caminho"], "ok" if r.get("ok") else r)
    feitos.append({"caminho": p["caminho"], "ok": bool(r.get("ok")), "erro": None if r.get("ok") else str(r)[:200]})
    if r.get("teto"):
        break
    time.sleep(2)
print(json.dumps(feitos, ensure_ascii=False))
