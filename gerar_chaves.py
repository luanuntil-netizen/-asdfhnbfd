"""Gera o ativacoes.json com o arquivo de ativação de cada dia (o segredo vem do segredo SEGREDO_CHAVE do GitHub, nunca fica num ficheiro do repositório).

A chave de cada dia = 40 caracteres tirados de 3 MD5 seguidos de (bloco + segredo [+ "1" / "2"]), igual ao cc1.py e ao Licenca.kt. Bloco = "AAAA-MM-DD-D" (1 por dia, até à
meia-noite, na hora LOCAL de quem usa).

28/10: a ativação passou a ser por ARQUIVO (já não se digita a chave; a página não mostra a chave). O arquivo é a linha "DDT1|bloco|chave" misturada byte a byte com uma
máscara e escrita em hexadecimal. Isto não é segurança, só impede de ler e copiar a chave à vista: quem manda é o segredo, que não está aqui. Tem de ser IGUAL ao
ler_arquivo_ativacao do cc1.py e ao Licenca.lerArquivo do Android.

Publicam-se os dias de ontem a depois de amanhã (em UTC): cobre qualquer fuso e atrasos do agendador."""
import datetime
import hashlib
import json
import os
import sys

ALFABETO = "abcdefghijklmnopqrstuvwxyz0123456789@$"
MARCA = "DDT1"
MASCARA = (0x5A, 0xA7, 0x13, 0x6E, 0xC4, 0x39, 0x81)


def chave_do_bloco(bloco, segredo):
    base = bloco + segredo
    octetos = b"".join(hashlib.md5((base + suf).encode()).digest() for suf in ("", "1", "2"))
    return "".join(ALFABETO[b % len(ALFABETO)] for b in octetos[:40])


def arquivo_de_ativacao(bloco, chave):
    """O conteúdo do arquivo de um dia: "DDT1|bloco|chave" misturado com a máscara, em hexadecimal (minúsculas, sem espaços)."""
    carga = f"{MARCA}|{bloco}|{chave}".encode("ascii")
    return "".join("%02x" % (b ^ MASCARA[i % len(MASCARA)] ^ ((i * 37 + 11) & 0xFF)) for i, b in enumerate(carga))


def main():
    segredo = os.environ.get("SEGREDO_CHAVE", "").strip()
    if len(segredo) < 16:
        sys.exit("Falta o segredo SEGREDO_CHAVE (Settings > Secrets and variables > Actions).")
    hoje = datetime.datetime.now(datetime.timezone.utc).date()
    arquivos = {}
    for delta in (-1, 0, 1, 2):
        dia = hoje + datetime.timedelta(days=delta)
        bloco = f"{dia.isoformat()}-D"
        arquivos[bloco] = arquivo_de_ativacao(bloco, chave_do_bloco(bloco, segredo))
    saida = {"gerado_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M"), "arquivos": arquivos}
    with open("ativacoes.json", "w", encoding="utf-8") as f:
        json.dump(saida, f, indent=1)
    print("ativacoes.json:", len(arquivos), "arquivos")


if __name__ == "__main__":
    main()
