# Blog Solut — Routine (fila no Google Sheets)

Routine de produção diária no Claude Code. Gera UM artigo por execução (HTML +
2 imagens Canva), envia por email via Resend, e controla a fila de temas numa
planilha do Google Sheets (lida e editada pelo conector do Drive).

## Por que Google Sheets e não GitHub

O estado da fila (qual tema já foi feito) precisa ser ESCRITO a cada execução.
O GitHub exige permissão de escrita/push que falhava no ambiente da Routine.
A planilha resolve isso: o conector do Drive lê e edita sem essa fricção, e o
progresso fica visível e editável por qualquer pessoa.

## Planilha da fila

"Fila Blog Solut - Temas"
ID: 1BmPGlJ6ZfAkqqUtT-fGWjeb4CJbkM7ic30PX2IBy4KA
Colunas: A:id  B:pilar  C:titulo  D:status  E:publicado_em

Para adicionar temas: basta inserir novas linhas com status "pendente".
Para reprocessar um tema: mude o status de volta para "pendente".

## Estrutura do repositório

```
solut-blog-routine/
├── CLAUDE.md           instruções do fluxo
├── imagens/            PNGs exportados do Canva
└── scripts/
    └── send_email.py   envia o email via API do Resend
```

A fila NÃO fica mais no repositório — vive no Google Sheets.

## Setup da Routine

1. Conecte os connectors: Google Drive e Canva
2. Variáveis de ambiente: RESEND_API_KEY, EMAIL_REMETENTE, EMAIL_DESTINO
3. Allowlist de rede: api.resend.com
4. Setup script: pip install requests
5. Trigger: Schedule diário
6. Prompt: "Siga o CLAUDE.md. Leia a fila na planilha do Google Sheets, pegue o
   próximo tema pendente, produza o artigo, envie o email e marque o tema como
   publicado na planilha."

## Teste

Run now (não conta no limite diário). Verifique: email chegou, e o status do
tema 1 virou "publicado" na planilha. Rode de novo: deve pegar o tema 2.
