# Blog Solut — Routine (envio automático via Resend)

Routine de produção diária no Claude Code. Gera UM artigo por execução (HTML +
2 imagens Canva) e ENVIA automaticamente por email para dupanisson@gmail.com,
com um resumo do processo para conferência manual.

O envio usa a API HTTP do Resend (porta 443). SMTP NÃO funciona no ambiente da
Routine — é bloqueado pela rede.

## Estrutura

```
solut-blog-routine/
├── temas.json          fila dos 30 temas
├── CLAUDE.md           instruções que o Claude segue a cada run
├── imagens/            PNGs exportados do Canva (capa.png, interna.png)
└── scripts/
    ├── run_pipeline.py pega o próximo tema da fila
    └── send_email.py   envia via API HTTP do Resend com anexos
```

## Setup (uma vez)

1. Crie conta gratuita em resend.com
2. Gere uma API Key no painel (formato re_...)
3. Para REMETENTE, escolha um caminho:
   - TESTE: use onboarding@resend.dev (só envia para o email que criou a conta)
   - PRODUÇÃO: verifique solutconsultoria.com.br no Resend (adiciona registros
     DNS) e use blog@solutconsultoria.com.br
4. Suba este repositório no GitHub e conecte à Routine
5. Conecte o conector do Canva à Routine
6. Configure as variáveis de ambiente da Routine:
   - RESEND_API_KEY   = sua chave re_...
   - EMAIL_REMETENTE  = onboarding@resend.dev (teste) ou blog@seudominio (prod)
   - EMAIL_DESTINO    = dupanisson@gmail.com
7. Setup script: pip install requests
8. Trigger: Schedule diário no horário desejado
9. Prompt da Routine: já configurado (lê a fila e segue o CLAUDE.md)

## Importante

- O envio é via API HTTP (Resend), não SMTP. SMTP é bloqueado no ambiente.
- A API Key NUNCA vai no código nem em chat — só nas variáveis de ambiente.
- No modo de teste (onboarding@resend.dev), só dá para enviar ao email que
  criou a conta Resend. Para mandar a dupanisson@gmail.com, ou crie a conta
  Resend com esse email, ou verifique um domínio próprio.

## Teste

Use Run now (não conta no limite diário). Confira se o email chegou com o
resumo do processo, o artigo em HTML e as duas imagens anexadas.
Se vier ERRO_ENVIO, o corpo da resposta do Resend explica a causa (geralmente
remetente não verificado ou destinatário não autorizado no modo teste).
