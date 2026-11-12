# 🔬 Breaking Science & Tech News Dashboard

An AI-powered agent that fetches the **top 3 highest-impact worldwide science & technology stories** every hour and displays them on a live web dashboard.

---

## Architecture

```
RSS Feeds ──► Python Agent ──► CAP Service (SQLite) ──► React Dashboard
               (hourly)          (REST API)               (auto-refresh)
```

| Component | Technology | Purpose |
|---|---|---|
| `news-agent/` | Python + OpenAI | Fetches & ranks news every hour |
| `news-service/` | SAP CAP (Node.js) | Stores & serves news via REST API |
| `news-service/ui/` | React + UI5 Web Components | Live dashboard UI |

---

## Quick Start

### 1. Set up the CAP service

```bash
cd news-service
npm install
cd ui && npm install && npm run build && cd ..
npx cds deploy --to sqlite
npm start
```

The service starts at **http://localhost:4004**
The dashboard opens at **http://localhost:4004/app/**

### 2. Set up the Python agent

```bash
cd news-agent
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
python agent.py
```

The agent runs once immediately, then every hour automatically.

---

## Configuration

Edit `news-agent/.env`:

| Variable | Default | Description |
|---|---|---|
| `NEWS_SERVICE_URL` | `http://localhost:4004/api` | URL of the CAP service |
| `OPENAI_API_KEY` | *(required)* | Your OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | AI model for story ranking |
| `TOP_N` | `3` | Number of top stories per cycle |

---

## How it works

1. **Every hour**, the agent pulls articles from 9 major science & tech RSS feeds (Nature, WIRED, NASA, Ars Technica, TechCrunch, New Scientist, and more).
2. It sends all articles to **GPT-4o-mini**, which selects the 3 most globally significant stories and assigns an **impact score (1–10)**.
3. The stories are stored via the **CAP REST API**.
4. The **React dashboard** auto-refreshes every minute and shows the latest 3 stories with their impact badge and source link.
5. Stories older than 24 hours are automatically cleaned up.

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/LatestNews` | Get latest 3 news items |
| `POST` | `/api/ingestNews` | Agent ingests new stories |
| `GET` | `/api/FetchLog` | View agent run history |

---

## Dashboard Features

- 🟥 **Critical** badge — impact score 8–10
- 🟠 **High Impact** badge — impact score 5–7
- 🔵 **Notable** badge — impact score 1–4
- **Read full story →** link to original article
- Auto-refreshes every 60 seconds
- Manual refresh button
