# SETUP — Blog Automático Solut (Routine)

Checklist para deixar a automação funcionando ponta a ponta. Três frentes
independentes: **GitHub (push/PR)**, **Google Sheets (fila)** e **Email/imagens**.

---

## 1. GitHub — liberar push e PR (resolve o erro 403)

O push da sessão passa por um proxy que usa o **GitHub App do Claude Code**.
Erro `403 "Resource not accessible by integration"` = o app não está
**instalado** no repositório com permissão de escrita.

> Atenção: ter o Claude em **"Authorized OAuth Apps"** NÃO basta — isso é só
> login/leitura. É preciso **instalar o GitHub App** com escrita em Contents.

Passos:
1. Acesse https://github.com/apps/claude → **Install / Configure**
   (ou: Claude Code na web → conexão do GitHub → **Install GitHub App**).
2. Selecione a conta dona do repo: **`kidocarro`**.
3. Repository access → **Only select repositories** →
   marque **`blog-automatico-solut-final2`** (ou "All repositories").
4. Aceite as permissões, incluindo:
   - **Contents: Read and write** (para `git push`)
   - **Pull requests: Read and write** (para abrir o PR)
5. Confirme. O app deve passar a aparecer em **Installed GitHub Apps**.

Se a conta logada não for `kidocarro` nem admin do repo, a instalação precisa
ser aprovada por quem é dono.

---

## 2. Google Sheets — credencial da fila

A fila vive na planilha "Fila Blog Solut - Temas"
(ID `1BmPGlJ6ZfAkqqUtT-fGWjeb4CJbkM7ic30PX2IBy4KA`) e é lida/escrita por
`scripts/fila_sheets.py` via **Service Account** (API do Google Sheets, HTTPS).

Variáveis de ambiente na Routine:

| Variável         | Obrigatória | Observação |
|------------------|-------------|------------|
| `GOOGLE_SA_JSON` | **Sim**     | Conteúdo JSON inteiro da chave da Service Account |
| `SHEET_ID`       | Não         | Default no script (`1BmPGl…By4KA`) |
| `SHEET_ABA`      | Não         | Default `Página1`; só defina se a aba tiver outro nome |

Além disso:
- **Compartilhe a planilha como _Editor_** com o `client_email` que está dentro
  do `GOOGLE_SA_JSON`. Sem isso → `403 permission denied` mesmo com a credencial.
- Variáveis novas só entram no ambiente em uma **execução nova** da Routine
  (são injetadas no início da sessão).

---

## 3. Email — envio do artigo (Resend)

`scripts/send_email.py` envia via API HTTP do Resend.

| Variável          | Obrigatória | Observação |
|-------------------|-------------|------------|
| `RESEND_API_KEY`  | **Sim**     | Chave `re_...` |
| `EMAIL_REMETENTE` | Não         | Default `onboarding@resend.dev` (teste) |
| `EMAIL_DESTINO`   | Não         | Default `dupanisson@gmail.com` |

---

## 4. Rede (egress allowlist)

Liberar saída HTTPS para:
- `sheets.googleapis.com`
- `oauth2.googleapis.com`
- `api.resend.com`

---

## 5. Setup script da Routine

```
pip install requests google-auth
```

Reforço recomendado (o `cryptography` do sistema costuma vir com o binding
`_cffi_backend` quebrado neste ambiente):

```
pip install --user --ignore-installed cffi cryptography
```

---

## 6. Teste rápido de leitura da fila

```
python scripts/fila_sheets.py
```

- Retorna `TEMA_ATUAL_TITULO=...` → conexão com o Sheets OK.
- `Unable to parse range` → `SHEET_ABA` não bate com o nome real da aba.
- `403 / permission denied` → planilha não compartilhada como Editor com a
  Service Account.
- `KeyError: 'GOOGLE_SA_JSON'` → credencial não chegou ao ambiente
  (configure e inicie uma execução nova).
