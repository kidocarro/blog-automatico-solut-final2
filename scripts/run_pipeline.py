#!/usr/bin/env python3
"""
run_pipeline.py — orquestrador diário da Routine do blog Solut.

Fluxo:
1. Lê temas.json e pega o primeiro tema com status "pendente"
2. Salva o tema escolhido para o Claude Code processar (etapa de escrita)
3. Após o Claude gerar o JSON do artigo, este script publica no WordPress
4. Marca o tema como "publicado" e registra a data

Este script é chamado pela Routine. A geração do conteúdo em si (pesquisa,
escrita, fact-check) é feita pelo Claude Code seguindo o CLAUDE.md do repo.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FILA = REPO / "temas.json"


def carregar_fila():
    with open(FILA, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_fila(dados):
    with open(FILA, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def proximo_tema(dados):
    for tema in dados["temas"]:
        if tema["status"] == "pendente":
            return tema
    return None


def marcar_publicado(dados, tema_id, link):
    for tema in dados["temas"]:
        if tema["id"] == tema_id:
            tema["status"] = "publicado"
            tema["publicado_em"] = datetime.now(timezone.utc).isoformat()
            tema["link"] = link
    salvar_fila(dados)


def main():
    dados = carregar_fila()
    tema = proximo_tema(dados)

    if tema is None:
        print("FILA_VAZIA: todos os 30 temas já foram publicados.")
        sys.exit(0)

    # Imprime o tema para o Claude Code capturar e processar
    print(f"TEMA_ATUAL_ID={tema['id']}")
    print(f"TEMA_ATUAL_PILAR={tema['pilar']}")
    print(f"TEMA_ATUAL_TITULO={tema['titulo']}")
    print("---")
    print("Claude: gere o artigo completo seguindo o CLAUDE.md, depois chame")
    print("post_to_wp.py com o JSON gerado e por fim marque o tema como publicado.")


if __name__ == "__main__":
    main()
