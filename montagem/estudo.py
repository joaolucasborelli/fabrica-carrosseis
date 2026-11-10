"""Estudo de marca de um ambiente novo (~20 min) e vigia diário dos ambientes ativos.

Roda no GitHub (estudo.yml). Cada agente é uma chamada à função "ambientes" (que fala com a OpenAI e busca na web);
aqui só se organiza o time: 7 agentes de pesquisa em paralelo → roteirista e editor → documento visual → configuração da fábrica.
"""
import sys, time
from concurrent.futures import ThreadPoolExecutor
from robo import chamar

AMB = "https://kfvugtrjuqdakbpzvsxq.supabase.co/functions/v1/ambientes"
PESQUISA = [("empresa", "Pesquisador da empresa"), ("leitor_redes", "Leitor das redes"), ("mercado", "Pesquisador de mercado"),
            ("publico", "Analista de público"), ("marca", "Estrategista de marca"), ("regras", "Guardião das regras"), ("arte", "Diretor de Arte")]


def _agente(aid, papel, contexto=None, tentativas=2):
    ultimo = None
    for _ in range(tentativas):
        r = chamar({"acao": "agente", "id": aid, "papel": papel, "contexto": contexto}, timeout=200, url=AMB)
        if r.get("ok"):
            return r["resultado"]
        ultimo = r.get("erro") or r
        if "créditos" in str(ultimo):
            break
    raise RuntimeError(f"{papel}: {str(ultimo)[:200]}")


def estudar(a):
    aid, t0 = a["id"], time.time()
    linhas = []

    def log(txt):
        linhas.append(f"{time.strftime('%H:%M')} {txt}")
        chamar({"acao": "progresso", "id": aid, "log": "em andamento\n" + "\n".join(linhas[-30:])}, url=AMB)

    log(f"O time começou a estudar {a['nome']}: 7 agentes pesquisando ao mesmo tempo.")
    achados, falhas = {}, []

    def um(par):
        papel, nome = par
        try:
            r = _agente(aid, papel)
            log(f"✓ {nome} terminou ({len(r.get('itens', []))} respostas).")
            return papel, r
        except Exception as e:
            log(f"✗ {nome} não conseguiu: {str(e)[:120]}")
            falhas.append(str(e))
            return papel, None

    with ThreadPoolExecutor(4) as ex:
        for papel, r in ex.map(um, PESQUISA):
            if r:
                achados[papel] = r
    if not achados:
        raise RuntimeError(falhas[0] if falhas else "nenhum agente respondeu")

    log("Roteirista e Editor-chefe cruzando tudo.")
    with ThreadPoolExecutor(2) as ex:
        fr = ex.submit(_agente, aid, "roteirista", achados)
        fe = ex.submit(_agente, aid, "editor", achados)
        achados["roteirista"] = fr.result()
        log("✓ Roteirista terminou os pilares, o arco e os 3 posts-modelo.")
        achados["editor"] = fe.result()
        log("✓ Editor-chefe apontou brechas e perguntas para o cliente.")

    log("Montando o documento visual.")
    doc = _agente(aid, "documento", achados)
    log("Transformando o estudo nas regras, presets e personas da fábrica.")
    fab = _agente(aid, "fabrica", doc)
    chamar({"acao": "salvar_estudo", "id": aid, "estudo": {"documento": doc, "fabrica": fab, "agentes": achados,
                                                         "minutos": round((time.time() - t0) / 60, 1), "falhas": falhas}}, url=AMB)
    print(aid, "estudo pronto em", round((time.time() - t0) / 60, 1), "min")


def vigiar():
    lista = chamar({"acao": "vigia_lista"}, url=AMB)
    for a in lista.get("ambientes", []) if lista.get("ok") else []:
        try:
            r = chamar({"acao": "agente", "id": a["id"], "papel": "vigia", "desde": a.get("vigia_em")}, timeout=200, url=AMB)
            avisos = (r.get("resultado") or {}).get("avisos", []) if r.get("ok") else []
            chamar({"acao": "vigia_salvar", "id": a["id"], "avisos": avisos}, url=AMB)
            print(a["id"], "vigia:", len(avisos), "avisos")
        except Exception as e:
            print(a["id"], "vigia ERRO", e)


def main():
    fila = chamar({"acao": "fila_estudo"}, url=AMB)
    print("estudos na fila:", [a["id"] for a in fila.get("ambientes", [])] if fila.get("ok") else fila)
    for a in fila.get("ambientes", []) if fila.get("ok") else []:
        try:
            estudar(a)
        except Exception as e:
            print(a["id"], "ERRO", e)
            msg = "a OpenAI está sem créditos: recarregue e clique em estudar de novo" if "créditos" in str(e) else str(e)[:300]
            chamar({"acao": "salvar_estudo", "id": a["id"], "erro": msg}, url=AMB)
    if "--vigia" in sys.argv:
        vigiar()


if __name__ == "__main__":
    main()
