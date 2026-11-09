"""Foto fiel ao texto: diretor de cena -> foto -> conferente (visão) -> correção, até 2 rodadas.
Usado pelo lote de capas e (depois) pelo montador.
"""
import json, time
import robo

CAPAS = "https://kfvugtrjuqdakbpzvsxq.supabase.co/functions/v1/capas"
MONTADOR = "https://kfvugtrjuqdakbpzvsxq.supabase.co/functions/v1/montador"


def _chamar(url, corpo, timeout=200):
    return robo.chamar(corpo, timeout=timeout, url=url)


def foto_fiel(texto, molde, ideia, caminho_base, vertical=False, nota_minima=8, max_edicoes=2, log=print):
    size = "1024x1536" if vertical else "1536x1024"
    c = _chamar(CAPAS, {"acao": "cena", "texto": texto, "molde": molde, "ideia": ideia})
    if not c.get("ok"):
        raise RuntimeError(f"cena: {c}")
    cena = c["cena"]
    log(f"  cena: {cena['momento'][:110]} | detalhes: {', '.join(cena['detalhes_do_texto'])[:120]}")
    cam = f"{caminho_base}_v0.png"
    g = _chamar(MONTADOR, {"acao": "imagem", "prompt": cena["prompt"], "caminho": cam, "size": size, "quality": "medium"})
    if not g.get("ok"):
        raise RuntimeError(f"imagem: {g}")
    historico = []
    melhor = (-1, cam)
    for rodada in range(max_edicoes + 1):
        cf = _chamar(CAPAS, {"acao": "conferir", "caminho": cam, "texto": texto, "cena": cena})
        if not cf.get("ok"):
            log(f"  conferente falhou: {cf}"); break
        k = cf["conferencia"]; historico.append({"versao": cam, **k})
        log(f"  v{rodada}: nota {k['nota']} | faltando: {k['detalhes_faltando']} | expressão: {k['expressao_problema'] or 'ok'} | defeitos: {k['defeitos']}")
        if k["nota"] > melhor[0]:
            melhor = (k["nota"], cam)
        if k["nota"] >= nota_minima or rodada == max_edicoes or not k["correcao"]:
            break
        novo = f"{caminho_base}_v{rodada+1}.png"
        e = _chamar(CAPAS, {"acao": "editar", "caminho": cam, "destino": novo, "instrucao": k["correcao"], "size": size})
        if not e.get("ok"):
            log(f"  edição falhou: {e}"); break
        cam = novo
    return {"cena": cena, "melhor": melhor[1], "nota": melhor[0], "historico": historico}
