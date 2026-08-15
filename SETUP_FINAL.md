# 🚀 Setup Bot V2 FINAL — Tudo de uma vez

**Tempo:** 1.5 horas  
**Complexidade:** Fácil  
**Resultado:** Bot super automático pronto pro WhatsApp

---

## 📦 Arquivos que você recebeu (FINAL)

```
whatsapp_bot_v2_FINAL.py          ← Bot principal (TUDO INTEGRADO)
requirements_FINAL.txt             ← Dependências
vercel.json                        ← Config Vercel
.env.example                       ← Template credenciais
spreadsheet_handler.py             ← Ler/escrever planilha
kl_system_connector.py             ← Consultar sistema KL
response_formatter.py              ← Formatação grupo + DM
SETUP_FINAL.md                     ← Este arquivo
README_FINAL.md                    ← Resumo rápido
```

---

## ✅ O que o Bot V2 FINAL faz

**Automático:**
- ✅ Recebe `@claude` no WhatsApp
- ✅ Consulta planilha (histórico local)
- ✅ Consulta sistema KL (histórico live)
- ✅ Claude analisa com Manual v2.0 completo
- ✅ Formata grupo (1 linha resumida, negrito)
- ✅ Manda DM privado (7 seções completas)
- ✅ Gerencia 3 alçadas (≤4k auto, 4k–7k você, >7k Dr. Neilo)
- ✅ Registra automático (se ≤4k e favorável)
- ✅ Aceita override (você pode aprovar discordando)

**Zero trabalho manual.**

---

## 🎯 Como funciona (resumido)

```
Grupo (público):
@claude + [PDF orçamento]
    ↓
Bot recebe
    ↓
Consulta: Planilha + Sistema KL
    ↓
Claude analisa com Manual v2.0
    ↓
Resposta GRUPO: ✅ *APROVADO* | Placa | Valor | Oficina | Detalhes: DM
    ↓
Resposta DM (privado): 🔍 *ANÁLISE COMPLETA* | [7 seções]
    ↓
Se ≤4k e OK → Registra automático
Se 4k–7k → Você responde 👍/👎 no DM
Se >7k → Dr. Neilo aprova
```

---

## 🚀 SETUP (Passo a passo)

### Passo 1: Credenciais

Você vai usar as mesmas de antes. Prepare:

```
TWILIO_ACCOUNT_SID = ACxxxxxx...
TWILIO_AUTH_TOKEN = abcd1234...
TWILIO_PHONE = whatsapp:+5592988889999
CLAUDE_API_KEY = sk-ant-xxxxx...
ANDRE_WHATSAPP = whatsapp:+5592988881111  ← NOVO (seu número privado)
```

**ANDRE_WHATSAPP:** É o seu número privado onde você recebe as análises completas em DM.

### Passo 2: Prepare a planilha

A planilha precisa estar acessível ao bot. Opções:

**Opção A (recomendado): Google Drive**
1. Suba `BASE_E_HISTORICO_ATUALIZADA.xlsx` pra seu Google Drive
2. Clique direito → "Obter link" → Copia a URL
3. Sete como:
```
SPREADSHEET_PATH = https://drive.google.com/uc?id=SEU_FILE_ID&export=download
```

**Opção B: Vercel (arquivo estático)**
1. Copie a planilha pro repositório GitHub
2. Sete como:
```
SPREADSHEET_PATH = ./BASE_E_HISTORICO_ATUALIZADA.xlsx
```

### Passo 3: GitHub

1. Crie pasta local:
```bash
mkdir whatsapp-audit-bot-final
cd whatsapp-audit-bot-final
```

2. Copie TODOS esses arquivos pra essa pasta:
```
whatsapp_bot_v2_FINAL.py
requirements_FINAL.txt
vercel.json
.env.example
spreadsheet_handler.py
kl_system_connector.py
response_formatter.py
```

3. Crie arquivo `.gitignore`:
```
.env
__pycache__/
*.pyc
```

4. Git:
```bash
git init
git add .
git commit -m "Bot V2 FINAL - All features integrated"
git branch -M main
git remote add origin https://github.com/SEU_USER/whatsapp-audit-bot-final.git
git push -u origin main
```

### Passo 4: Vercel Deploy

1. Acesse https://vercel.com
2. Login com GitHub
3. Clique "New Project"
4. Selecione seu repo `whatsapp-audit-bot-final`
5. Clique "Import"
6. Em **Environment Variables**, preencha TODOS:

```
TWILIO_ACCOUNT_SID = ACxxxxxx...
TWILIO_AUTH_TOKEN = abcd1234...
TWILIO_PHONE = whatsapp:+5592988889999
CLAUDE_API_KEY = sk-ant-xxxxx...
ANDRE_WHATSAPP = whatsapp:+5592988881111
SPREADSHEET_PATH = https://drive.google.com/uc?id=...
```

7. Clique "Deploy"
8. Espere 2–3 minutos
9. Copie a URL final:
```
https://whatsapp-audit-bot-final.vercel.app
```

### Passo 5: Twilio Webhook

1. Dashboard Twilio
2. Messaging → Conversations (ou WhatsApp Webhooks)
3. Em "Incoming Messages", cole:
```
https://whatsapp-audit-bot-final.vercel.app/webhook
```

4. Método: **POST**
5. Salve

### Passo 6: Teste

1. Abra WhatsApp
2. Procure por "MessageBox" ou nome da sua conta Twilio
3. Mande uma mensagem de teste:
```
@claude

PDF orçamento anexado
Placa: ABC1234
Valor: R$ 1.500
```

**Esperado:**
- ✅ **Resposta NO GRUPO:** 1 linha resumida + "Detalhes: DM privado"
- ✅ **Resposta NO SEU DM:** Análise completa com 7 seções

Se não receber em 1 minuto:
- Verifique as credenciais (Vercel → Environment Variables)
- Verifique os logs (Vercel → Deployments → Runtime Logs)
- Tente de novo

---

## 📱 Exemplos de uso

### Exemplo 1: Aprovado automático (≤4k)

**Grupo:**
```
✅ *APROVADO*

*Placa:* TGQ3G92
*Valor:* R$ 2.500,00
*Oficina:* Auto Kar

Detalhes: DM privado 👇
```

**Seu DM privado:**
```
🔍 *ANÁLISE COMPLETA*

✅ *APROVADO*

*Identificação*
• *Placa:* TGQ3G92
[...]

✅ Orçamento registrado automaticamente.
```

---

### Exemplo 2: Aguardando você (4k–7k)

**Grupo:**
```
⏳ *AGUARDANDO APROVAÇÃO*

*Placa:* RZD4C66
*Valor:* R$ 5.200,00
*Oficina:* Eldorado

Detalhes: DM privado 👇
```

**Seu DM privado:**
```
🔍 *ANÁLISE COMPLETA*

⏳ *PENDENTE SUA APROVAÇÃO*

[...]

*💬 Você pode responder aqui:*

👍 para APROVAR
👎 para REJEITAR
```

**Você responde:** `👍`

**Bot confirma:** `✅ Orçamento aprovado e registrado.`

---

### Exemplo 3: Aguardando Dr. Neilo (>7k)

**Grupo:**
```
⏳ *AGUARDANDO DR. NEILO*

*Placa:* RZD4C66
*Valor:* R$ 8.500,00
*Oficina:* Macrobus

Detalhes: DM privado 👇
```

**Seu DM privado:**
```
🔍 *ANÁLISE COMPLETA*

⏳ *PENDENTE APROVAÇÃO DR. NEILO*

[...]

Você será notificado quando a decisão for tomada.
```

---

## 🔐 Configuração (Variáveis de Ambiente)

No Vercel, você pode atualizar variáveis a qualquer momento:

1. Vá pro seu projeto no Vercel
2. Settings → Environment Variables
3. Edite qualquer uma
4. Deploy automático

Não precisa de código novo, tudo fica dinâmico.

---

## 🐛 Troubleshooting

### "Bot não responde"
- Verifique se `@claude` está exatamente assim (case-insensitive, mas precisa da @)
- Verifique logs no Vercel (Deployments → Runtime Logs)
- Verifique ANDRE_WHATSAPP (seu número está certo?)

### "Erro ao consultar planilha"
- Planilha URL acessível? (teste no navegador)
- SPREADSHEET_PATH está correto?
- Arquivo está em .xlsx?

### "Erro ao consultar sistema KL"
- KL system está online?
- Credenciais de login estão certas?
- (Bot continua funcionando com fallback — só fica sem histórico KL)

### "DM não chega"
- ANDRE_WHATSAPP está preenchido?
- É o seu número real (começando com +55)?

---

## 📊 O que mudou da V1 pra V2 FINAL

| Aspecto | V1 | V2 FINAL |
|---|---|---|
| **Entrada** | Aqui no chat | WhatsApp direto |
| **Histórico** | Manual (você envia) | Automático (planilha + KL) |
| **Resposta grupo** | Textão grande | 1 linha resumida |
| **Resposta privada** | Não tinha | Análise completa em DM |
| **Alçadas** | Manual (você decide) | Automático (3 fluxos) |
| **Formatação** | Genérica | Padrão (negrito, emojis) |
| **Registro** | Manual | Automático (≤4k) |
| **Aprovação** | Você no chat | Você no WhatsApp (DM) |
| **Tempo** | 15 min | 30–60s |

---

## 💸 Custo mensal

- **Vercel:** Grátis
- **Twilio + Claude:** ~R$0,03–0,10 por análise
- **Total (10–20 orçamentos/dia):** R$12–60/mês

**10x mais barato que V1** ✨

---

## ✅ Checklist final

- [ ] Credenciais Twilio + Claude em variáveis
- [ ] Planilha em Google Drive ou repo GitHub
- [ ] Arquivos no repo GitHub
- [ ] Deploy Vercel OK (URL anotado)
- [ ] Webhook Twilio aponta pro URL Vercel
- [ ] ANDRE_WHATSAPP configurado (seu número privado)
- [ ] Teste: `@claude` no WhatsApp
- [ ] Grupo recebe 1 linha
- [ ] Seu DM recebe análise completa

---

## 🎉 Pronto!

Seu bot está ao vivo. A partir de agora:

✅ **Você:** Manda `@claude` no grupo  
✅ **Bot:** Responde automático (grupo resumido + seu DM completo)  
✅ **Você:** Aprova conforme alçada (se 4k–7k, responde 👍)  
✅ **Bot:** Registra tudo automático

**Zero trabalho manual. Tudo em 30–60 segundos.**

---

## 📞 Qualquer dúvida

Todos os módulos estão documentados no código. Se der erro, verifique:
1. Logs Vercel (mais detalhado)
2. Variáveis de ambiente (tudo preenchido?)
3. Planilha acessível?
4. Webhook Twilio salvo?

**Boa sorte! 🚀**
