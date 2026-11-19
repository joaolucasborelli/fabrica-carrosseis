"""Foto REAL com licença livre para pessoa pública / notícia (nunca rosto de político feito por IA).
Fonte: Wikimedia Commons (cada arquivo traz a licença e o autor). Só aceita CC BY, CC BY-SA, CC0 e domínio público;
recusa NC (não comercial) e ND (sem derivação). Devolve o arquivo baixado e a linha de crédito para pôr no slide.
"""
import html
import json
import re
import time
import urllib.error
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "fabrica-carrosseis-bot/1.0 (montagem de slides; uso com credito)"}
LIVRE = re.compile(r"^(cc[- ]?by(-sa)?(\s*\d(\.\d)?)?(\s*\w\w)?|cc0(\s*1\.0)?|public domain|domínio público|pd\b)", re.I)
PROIBIDA = re.compile(r"-(nc|nd)\b", re.I)


def _sem_acento(t):
    return "".join(c for c in unicodedata.normalize("NFD", t or "") if unicodedata.category(c) != "Mn").lower()


def _limpa(t):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t or ""))).strip()


def _get(params):
    url = API + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
        return json.loads(r.read())


def candidatos(termos, pessoa="", limite=40):
    d = _get({"action": "query", "format": "json", "generator": "search", "gsrsearch": f"{termos} filetype:bitmap",
              "gsrnamespace": 6, "gsrlimit": limite, "prop": "imageinfo", "iiprop": "url|extmetadata|size|mime", "iiurlwidth": 1600})
    nome = _sem_acento(pessoa)
    chaves = [w for w in re.findall(r"[a-z]+", nome) if len(w) >= 4 and w not in ("silva", "santos", "souza", "oliveira", "pereira", "costa", "lima")] or ([nome] if nome else [])
    saida = []
    for pg in (d.get("query", {}).get("pages", {}) or {}).values():
        ii = (pg.get("imageinfo") or [{}])[0]; meta = ii.get("extmetadata") or {}
        lic = _limpa((meta.get("LicenseShortName") or {}).get("value", ""))
        if not lic or not LIVRE.match(lic) or PROIBIDA.search(lic):
            continue
        if ii.get("mime") not in ("image/jpeg", "image/png") or (ii.get("width") or 0) < 900:
            continue
        texto = _sem_acento(" ".join([pg.get("title", ""), _limpa((meta.get("ImageDescription") or {}).get("value", "")),
                                      _limpa((meta.get("ObjectName") or {}).get("value", "")), (meta.get("Categories") or {}).get("value", "")]))
        if chaves and not any(k in texto for k in chaves):
            continue
        data = _limpa((meta.get("DateTimeOriginal") or {}).get("value", "")) or _limpa((meta.get("DateTime") or {}).get("value", ""))
        ano = int(m.group(0)) if (m := re.search(r"(19|20)\d\d", data)) else 0
        autor = _limpa((meta.get("Artist") or {}).get("value", "")) or "autor desconhecido"
        if len(autor) > 60:
            autor = autor[:57] + "…"
        md = re.search(r"((19|20)\d\d)-(\d\d)-(\d\d)", data)
        quando = f"{md.group(4)}/{md.group(3)}/{md.group(1)}" if md else (str(ano) if ano else "data desconhecida")
        mt = re.search(r"(\d\d)\.(\d\d)\.((19|20)\d\d)", pg.get("title", ""))  # o título oficial traz a data do evento
        if mt:
            quando = f"{mt.group(1)}/{mt.group(2)}/{mt.group(3)}"; ano = int(mt.group(3))
        saida.append({"titulo": pg.get("title"), "url": ii.get("thumburl") or ii.get("url"), "pagina": ii.get("descriptionurl"),
                      "licenca": lic, "autor": autor, "ano": ano, "largura": ii.get("width"),
                      "credito": f"Foto de {quando}: {autor} · {lic} · Wikimedia Commons"})
    # mais recente primeiro; depois a maior
    saida.sort(key=lambda c: (c["ano"], min(c["largura"] or 0, 4000)), reverse=True)
    return saida


def recortar_rosto(arq: Path, proporcao=4 / 5, folga=3.2, min_lado=360):
    """Foto de palco/evento com a pessoa pequena: recorta em volta do maior rosto (retrato 4:5).
    Devolve True se recortou. Sem rosto, rosto pequeno demais ou recorte com pouca resolução: deixa como está."""
    try:
        import cv2
    except Exception:
        return False
    img = cv2.imread(str(arq))
    if img is None:
        return False
    h, w = img.shape[:2]
    cinza = cv2.equalizeHist(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
    det = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    rostos = det.detectMultiScale(cinza, scaleFactor=1.08, minNeighbors=6, minSize=(40, 40))
    if len(rostos) == 0:
        return False
    x, y, fw, fh = max(rostos, key=lambda r: r[2] * r[3])
    if fw * fh >= 0.06 * w * h:  # o rosto já é grande: a foto já é um retrato
        return False
    cw = int(fw * folga); ch = int(cw / proporcao)
    if cw > w or ch > h:
        cw = min(w, int(h * proporcao)); ch = int(cw / proporcao)
    if cw < min_lado:  # recorte com pouca resolução: borra no slide
        return False
    cx = x + fw // 2; cy = y + int(fh * 0.9)  # rosto no terço de cima
    x0 = max(0, min(w - cw, cx - cw // 2)); y0 = max(0, min(h - ch, cy - ch // 2))
    cv2.imwrite(str(arq), img[y0:y0 + ch, x0:x0 + cw], [cv2.IMWRITE_JPEG_QUALITY, 92])
    return True


USADAS = set()  # fotos já usadas nesta montagem: a mesma foto real não se repete no post


def buscar(termos, pessoa, destino: Path, log=print, aceitar=None, max_conferir=6):
    """Baixa a melhor foto livre que passar na conferência (aceitar). Devolve {"arquivo", "credito", "pagina"} ou None."""
    for tentativa in (termos, pessoa):
        if not tentativa:
            continue
        try:
            cs = candidatos(tentativa, pessoa)
        except Exception as e:  # rede, API fora
            log(f"  foto real: busca falhou ({e})")
            return None
        for c in [x for x in cs if x["titulo"] not in USADAS][:max_conferir]:
            baixou = False
            for espera in (1.5, 6, 15):  # o Wikimedia limita downloads seguidos (HTTP 429): espera e tenta de novo
                time.sleep(espera)
                try:
                    with urllib.request.urlopen(urllib.request.Request(c["url"], headers=UA), timeout=60) as r:
                        destino.parent.mkdir(parents=True, exist_ok=True); destino.write_bytes(r.read())
                    baixou = True; break
                except urllib.error.HTTPError as e:
                    if e.code != 429:
                        break
                except Exception:
                    break
            if not baixou:
                continue
            if recortar_rosto(destino):
                log(f"  foto real recortada no rosto: {c['titulo']}")
            if aceitar and not aceitar(destino, c):
                log(f"  foto real recusada: {c['titulo']}")
                continue
            USADAS.add(c["titulo"])
            log(f"  foto real: {c['titulo']} ({c['licenca']}, {c['ano'] or 's/ano'})")
            return {"arquivo": destino, "credito": c["credito"], "pagina": c["pagina"]}
    return None


if __name__ == "__main__":
    import sys
    for c in candidatos(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "")[:8]:
        print(c["ano"], c["licenca"], "|", c["titulo"], "|", c["credito"])
