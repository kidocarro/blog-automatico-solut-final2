#!/usr/bin/env python3
"""
update_sheet.py — atualiza status e data na planilha "Fila Blog Solut - Temas"
usando Service Account via Google Sheets API v4.
Assina o JWT com openssl subprocess para evitar dependências de cryptography/_cffi.

Uso:
    python scripts/update_sheet.py --row 5 --status publicado --data 2026-06-27
"""

import argparse
import base64
import json
import os
import subprocess
import tempfile
import time

import requests


SPREADSHEET_ID = "1BmPGlJ6ZfAkqqUtT-fGWjeb4CJbkM7ic30PX2IBy4KA"
SCOPES = "https://www.googleapis.com/auth/spreadsheets"
TOKEN_URL = "https://oauth2.googleapis.com/token"
SHEETS_BASE = "https://sheets.googleapis.com/v4/spreadsheets"


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def make_jwt(sa_json: dict) -> str:
    header = {"alg": "RS256", "typ": "JWT"}
    now = int(time.time())
    payload = {
        "iss": sa_json["client_email"],
        "scope": SCOPES,
        "aud": TOKEN_URL,
        "iat": now,
        "exp": now + 3600,
    }
    h = _b64url(json.dumps(header, separators=(",", ":")).encode())
    p = _b64url(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{h}.{p}".encode()

    with tempfile.NamedTemporaryFile(suffix=".pem", delete=False, mode="w") as f:
        f.write(sa_json["private_key"])
        keyfile = f.name

    try:
        result = subprocess.run(
            ["openssl", "dgst", "-sha256", "-sign", keyfile],
            input=signing_input,
            capture_output=True,
            timeout=10,
        )
        if result.returncode != 0:
            raise RuntimeError(f"openssl error: {result.stderr.decode()}")
        sig_bytes = result.stdout
    finally:
        os.unlink(keyfile)

    return f"{h}.{p}.{_b64url(sig_bytes)}"


def get_access_token(sa_json: dict) -> str:
    signed_jwt = make_jwt(sa_json)
    resp = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": signed_jwt,
        },
        timeout=30,
    )
    if resp.status_code >= 400:
        print(f"ERRO_TOKEN status={resp.status_code} corpo={resp.text}")
        resp.raise_for_status()
    return resp.json()["access_token"]


def update_cells(token: str, row: int, status: str, data: str) -> None:
    range_notation = f"D{row}:E{row}"
    url = f"{SHEETS_BASE}/{SPREADSHEET_ID}/values/{range_notation}?valueInputOption=USER_ENTERED"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    body = {"range": range_notation, "majorDimension": "ROWS", "values": [[status, data]]}
    resp = requests.put(url, headers=headers, json=body, timeout=30)
    if resp.status_code >= 400:
        print(f"ERRO_SHEET status={resp.status_code} corpo={resp.text}")
        resp.raise_for_status()
    updated = resp.json().get("updatedCells", 0)
    print(f"SHEET_ATUALIZADO linha={row} status={status} data={data} celulas={updated}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--row", type=int, required=True)
    parser.add_argument("--status", required=True)
    parser.add_argument("--data", required=True)
    args = parser.parse_args()

    sa_json = json.loads(os.environ["GOOGLE_SA_JSON"])
    token = get_access_token(sa_json)
    update_cells(token, args.row, args.status, args.data)


if __name__ == "__main__":
    main()
