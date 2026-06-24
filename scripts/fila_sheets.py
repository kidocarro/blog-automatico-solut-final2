#!/usr/bin/env python3
"""
fila_sheets.py — gerencia a fila de temas no Google Sheets via API.
Usa Service Account para LER e ESCREVER na planilha por HTTP (porta 443).

Modos:
  python scripts/fila_sheets.py                 -> imprime o próximo pendente
  python scripts/fila_sheets.py --concluir <ID> -> marca o tema como publicado

Variáveis de ambiente:
  GOOGLE_SA_JSON   conteúdo JSON inteiro da chave da Service Account
  SHEET_ID         ID da planilha (tem default abaixo)
  SHEET_ABA        nome da aba (ajuste ao nome real da planilha)

Colunas (linha 1 = cabeçalho): A:id B:pilar C:titulo D:status E:publicado_em
"""

import json
import os
import sys
from datetime import datetime, timezone

import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request as GoogleRequest

SHEET_ID = os.environ.get("SHEET_ID", "1BmPGlJ6ZfAkqqUtT-fGWjeb4CJbkM7ic30PX2IBy4KA")
ABA = os.environ.get("SHEET_ABA", "Página1")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
BASE = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}"


def _token():
    info = json.loads(os.environ["GOOGLE_SA_JSON"])
    cred = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    cred.refresh(GoogleRequest())
    return cred.token


def _headers():
    return {"Authorization": f"Bearer {_token()}"}


def _ler():
    url = f"{BASE}/values/{ABA}!A2:E1000"
    r = requests.get(url, headers=_headers(), timeout=30)
    r.raise_for_status()
    return r.json().get("values", [])


def proximo():
    for i, linha in enumerate(_ler(), start=2):
        linha = (linha + [""] * 5)[:5]
        _id, pilar, titulo, status, _ = linha
        if status.strip().lower() == "pendente":
            print(f"TEMA_ATUAL_ID={_id}")
            print(f"TEMA_ATUAL_PILAR={pilar}")
            print(f"TEMA_ATUAL_TITULO={titulo}")
            print(f"TEMA_ATUAL_LINHA={i}")
            return
    print("FILA_VAZIA: todos os temas já foram publicados.")
    sys.exit(0)


def concluir(tema_id):
    alvo = None
    status_atual = ""
    for i, linha in enumerate(_ler(), start=2):
        linha = (linha + [""] * 5)[:5]
        if str(linha[0]).strip() == str(tema_id):
            alvo = i
            status_atual = linha[3].strip().lower()
            break
    if alvo is None:
        print(f"ERRO_CONCLUIR: tema id={tema_id} não encontrado.")
        sys.exit(1)
    if status_atual == "publicado":
        print(f"AVISO: tema id={tema_id} já estava publicado.")
        sys.exit(0)

    agora = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    url = f"{BASE}/values/{ABA}!D{alvo}:E{alvo}"
    r = requests.put(
        url, headers=_headers(),
        params={"valueInputOption": "RAW"},
        json={"values": [["publicado", agora]]}, timeout=30,
    )
    r.raise_for_status()
    print(f"TEMA_CONCLUIDO_OK id={tema_id} linha={alvo}")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--concluir":
        concluir(sys.argv[2])
    else:
        proximo()
