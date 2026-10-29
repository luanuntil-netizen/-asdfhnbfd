"""Gera o chaves.json com as chaves de 12 h (o segredo vem do segredo SEGREDO_CHAVE do GitHub, nunca fica num ficheiro do repositório).

Cada chave = 40 caracteres tirados de 3 MD5 seguidos de (bloco + segredo [+ "1" / "2"]), igual ao cc1.py e ao Licenca.kt. Bloco = "AAAA-MM-DD-H0" (00h-11h) ou "-H1" (12h-23h)
na hora LOCAL de quem usa; por isso publicam-se os blocos de ontem, hoje e amanhã (em UTC): cobre qualquer fuso."""
import datetime
import hashlib
import json
import os
import sys

ALFABETO = "abcdefghijklmnopqrstuvwxyz0123456789@$"


def chave_do_bloco(bloco, segredo):
    base = bloco + segredo
    octetos = b"".join(hashlib.md5((base + suf).encode()).digest() for suf in ("", "1", "2"))
    return "".join(ALFABETO[b % len(ALFABETO)] for b in octetos[:40])


def main():
    segredo = os.environ.get("SEGREDO_CHAVE", "").strip()
    if len(segredo) < 16:
        sys.exit("Falta o segredo SEGREDO_CHAVE (Settings > Secrets and variables > Actions).")
    hoje = datetime.datetime.now(datetime.timezone.utc).date()
    chaves = {}
    for delta in (-1, 0, 1):
        dia = hoje + datetime.timedelta(days=delta)
        for h in (0, 1):
            bloco = f"{dia.isoformat()}-H{h}"
            chaves[bloco] = chave_do_bloco(bloco, segredo)
    saida = {"gerado_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M"), "chaves": chaves}
    with open("chaves.json", "w", encoding="utf-8") as f:
        json.dump(saida, f, indent=1)
    print("chaves.json:", len(chaves), "chaves")


if __name__ == "__main__":
    main()
