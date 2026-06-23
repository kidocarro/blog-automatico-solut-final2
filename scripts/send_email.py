#!/usr/bin/env python3
"""
send_email.py — envia o artigo do dia por email via API HTTP do Resend.

Usa requisição HTTPS (porta 443), que funciona no ambiente da Routine —
ao contrário de SMTP, que é bloqueado.

Uso:
    python scripts/send_email.py \
        --assunto "Artigo do dia: ..." \
        --corpo-html corpo_email.html \
        --imagens imagens/capa.png imagens/interna.png

Variáveis de ambiente esperadas (configurar na Routine):
    RESEND_API_KEY    chave de API do Resend (re_...)
    EMAIL_REMETENTE   remetente verificado (ex: blog@solutconsultoria.com.br)
                      ou onboarding@resend.dev para testes
    EMAIL_DESTINO     destinatário (ex: dupanisson@gmail.com)
"""

import argparse
import base64
import os
from pathlib import Path

import requests

API_KEY = os.environ["RESEND_API_KEY"]
REMETENTE = os.environ.get("EMAIL_REMETENTE", "onboarding@resend.dev")
DESTINO = os.environ.get("EMAIL_DESTINO", "dupanisson@gmail.com")

ENDPOINT = "https://api.resend.com/emails"


def enviar(assunto: str, corpo_html_path: str, imagens: list) -> None:
    with open(corpo_html_path, "r", encoding="utf-8") as f:
        corpo_html = f.read()

    anexos = []
    for caminho in imagens:
        p = Path(caminho)
        if not p.exists():
            print(f"AVISO: imagem não encontrada, pulando: {caminho}")
            continue
        with open(p, "rb") as img:
            conteudo_b64 = base64.b64encode(img.read()).decode("utf-8")
        anexos.append({"filename": p.name, "content": conteudo_b64})

    payload = {
        "from": REMETENTE,
        "to": [DESTINO],
        "subject": assunto,
        "html": corpo_html,
    }
    if anexos:
        payload["attachments"] = anexos

    resposta = requests.post(
        ENDPOINT,
        json=payload,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        timeout=30,
    )

    if resposta.status_code >= 400:
        print(f"ERRO_ENVIO status={resposta.status_code} corpo={resposta.text}")
        resposta.raise_for_status()

    email_id = resposta.json().get("id", "")
    print(f"EMAIL_ENVIADO_OK para={DESTINO} id={email_id}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--assunto", required=True)
    parser.add_argument("--corpo-html", required=True)
    parser.add_argument("--imagens", nargs="*", default=[])
    args = parser.parse_args()
    enviar(args.assunto, args.corpo_html, args.imagens)


if __name__ == "__main__":
    main()
