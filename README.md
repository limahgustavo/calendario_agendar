# 💅 NailBook — Plataforma SaaS de Agendamento para Nail Designers

Plataforma multi-studio onde nail designers gerenciam agenda, pagamentos e clientes, e a plataforma faz repasses semanais (com taxa configurável) via PIX.

## Papéis

- **Cliente** — agenda em vários studios, paga online, acompanha histórico, edita perfil.
- **Nail Designer (Studio)** — configura disponibilidade, serviços/preços, gera link + QR, vê agendamentos e faturamento, recebe repasses.
- **Admin (plataforma)** — monitora clientes e studios, aprova repasses semanais, define a taxa.

## Stack

- **Backend:** FastAPI + SQLAlchemy 2.0 + PostgreSQL (UUID) + Celery + Redis
- **Frontend:** React + Vite + TypeScript + TailwindCSS
- **Pagamentos:** Asaas (PIX/boleto/cartão + transferências para repasses)
- **WhatsApp:** Z-API · **Email:** Resend
- **Auth:** JWT (30 dias) + bcrypt, com fluxo de criar/redefinir senha por email

## Como rodar (local, Docker)

```bash
cp .env.example .env      # preencha as chaves (Asaas/Z-API/Resend opcionais p/ testar)
docker-compose up -d --build
docker-compose exec backend python seed.py   # cria admin + planos + configurações
```

- Frontend: http://localhost:5173
- API + docs: http://localhost:8000/api/docs
- Login admin: `ADMIN_EMAIL` / `ADMIN_PASSWORD` do `.env`

### Serviços do compose
`db` (Postgres) · `redis` · `backend` (API) · `worker` (Celery) · `beat` (agendador) · `frontend` (Vite)

## Fluxos principais

**Onboarding studio:** `/auth/studio` → cria conta + studio → email para criar senha → painel `/studio`.

**Agendamento (cliente):** abre o link do studio `/booking/:slug` → escolhe serviço, data e horário → informa dados + CPF → paga (50% ou 100%, conforme o studio) via Asaas → recebe confirmação por WhatsApp/email + lembretes 24h e 2h antes. Uma conta de cliente é criada automaticamente (com link para definir senha).

**Pagamento:** webhook do Asaas (`/api/payments/webhook/asaas`) confirma o agendamento ao receber `PAYMENT_CONFIRMED`.

**Repasses:** toda sexta (Celery beat) o sistema soma os pagamentos confirmados da semana por studio, desconta a taxa da plataforma e cria um repasse `pendente_aprovacao`. O admin aprova em `/admin/repasses` → transferência PIX via Asaas.
> Regra: `repasse = Σ(pagamentos online confirmados na semana) × (1 − taxa%)`.

## Planos

`basico` (R$29, 10 ag/mês) · `premium` (R$79, 50 ag/mês) · `pro` (R$199, ilimitado). O limite é aplicado no booking.

## Testes & lint

```bash
docker-compose exec backend pytest tests/ -v
docker-compose exec backend ruff check .
docker-compose exec frontend npx vite build
```

## Deploy

- **Backend + worker + beat + Postgres + Redis:** Render via `render.yaml` (Blueprint). `DATABASE_URL`/`REDIS_URL` injetados automaticamente; `SECRET_KEY`/`ENCRYPTION_KEY` gerados. Configure `ASAAS_*`, `ZAPI_*`, `RESEND_*`, `FRONTEND_URL`, `ADMIN_*` no painel.
- **Frontend:** Vercel (ou static site do Render). Defina `VITE_API_URL` apontando para a API. SPA rewrite já configurado (`frontend/vercel.json`).
- Configure o **webhook do Asaas** para `https://SUA-API/api/payments/webhook/asaas` com o header `asaas-access-token = ASAAS_WEBHOOK_TOKEN`.

CI: GitHub Actions (`.github/workflows/ci.yml`) roda ruff + pytest no backend e build do frontend.
