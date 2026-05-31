# PropViz — Monthly Cost Breakdown
**Prepared for:** Partner Review
**Date:** May 2026
**App:** AI-powered real estate property visualization platform (Bangladesh market)

---

## What the App Does (Cost Context)

A user uploads a floor plan and property brochure. The app then automatically:
1. Reads and extracts room data from the floor plan (Claude AI)
2. Reads property specs from the brochure (Claude AI)
3. Generates photorealistic interior render prompts per room (Claude AI)
4. Generates a 5-second cinematic video clip for each room — up to 6 rooms (Runway AI)
5. Writes and voices a 90-second narration script (Claude AI + ElevenLabs)
6. Stores all assets and serves the final output to the user (Cloud Storage + Hosting)

This means every single property job triggers real, paid API calls across multiple services.

---

## Cost Structure: Fixed vs Variable

Costs fall into two buckets:

- **Fixed costs** — paid every month regardless of how many properties are processed
- **Variable costs** — scale directly with the number of properties processed

---

## Fixed Monthly Costs

### 1. Railway (Hosting Platform) — ~$14–24/month

Railway hosts all 5 backend services: the database, the job queue, the API server, the background worker, and the frontend. Without this, the app cannot run.

| Service | Estimated Monthly Cost |
|---|---|
| PostgreSQL database | $2–4 |
| Redis (job queue) | $1–3 |
| FastAPI backend server | $2–5 |
| Celery background worker | $4–8 |
| Next.js frontend | $1–3 |
| Railway platform base fee | $5 |
| **Total** | **~$15–28/month** |

> The Celery worker is the most resource-intensive service because it runs long video generation tasks in the background.

### 2. ElevenLabs (Voice Narration) — $5–22/month

ElevenLabs converts the narration script (~200 words, ~1,000 characters) into a professional voice recording. This is a fixed subscription plan.

| Plan | Price | Characters/month | Properties supported |
|---|---|---|---|
| Starter | $5/month | 30,000 chars | ~30 properties |
| Creator | $22/month | 100,000 chars | ~100 properties |
| Pro | $99/month | 500,000 chars | ~500 properties |

**Recommendation:** Start with Creator ($22/month) to allow for growth.

### 3. Domain Name — ~$1–2/month (~$12–20/year)

A custom domain (e.g., propviz.com.bd) for professional presentation. One-time annual cost.

---

## Variable Costs (Per Property Processed)

These are pay-per-use charges billed directly by AI providers.

### Per-Property API Cost Breakdown

| Service | What it does | Cost per property |
|---|---|---|
| **Claude Opus 4.7** (Anthropic) | Reads floor plan, reads brochure, writes render prompts, writes narration script — 4 AI calls per job | ~$0.40–0.70 |
| **Runway Gen-4 Turbo** | Generates up to 6 × 5-second video clips (one per room) | ~$1.50–3.60 |
| **AWS S3 / Cloudflare R2** | Stores video files, audio, and images (~60–100MB per property) | ~$0.03–0.08 |
| **Total per property** | | **~$2.00–4.40** |

> **Note on Runway:** This is the dominant variable cost. Each 5-second clip costs approximately $0.25–0.60 depending on the Runway API plan. A property with 6 rooms generates 6 clips.

---

## Total Monthly Cost Projections

### Scenario 1: Testing / Early Launch (10 properties/month)

| Cost Type | Amount |
|---|---|
| Railway hosting | $20 |
| ElevenLabs (Starter) | $5 |
| Claude API (10 × ~$0.55) | $5.50 |
| Runway API (10 × ~$2.50) | $25 |
| Storage | $1 |
| **Total** | **~$56/month** |

### Scenario 2: Soft Launch (30 properties/month)

| Cost Type | Amount |
|---|---|
| Railway hosting | $22 |
| ElevenLabs (Creator) | $22 |
| Claude API (30 × ~$0.55) | $16.50 |
| Runway API (30 × ~$2.50) | $75 |
| Storage | $3 |
| **Total** | **~$138/month** |

### Scenario 3: Active Use (75 properties/month)

| Cost Type | Amount |
|---|---|
| Railway hosting | $28 |
| ElevenLabs (Creator) | $22 |
| Claude API (75 × ~$0.55) | $41.25 |
| Runway API (75 × ~$2.50) | $187.50 |
| Storage | $6 |
| **Total** | **~$285/month** |

---

## Cost per Property (Break-even Pricing Guide)

If you charge per property processed, here is the minimum to cover costs at scale:

| Volume | Cost per property (all-in) | Suggested charge |
|---|---|---|
| 10/month | ~$5.60 | $15–25 |
| 30/month | ~$4.60 | $12–20 |
| 75/month | ~$3.80 | $10–18 |

At even a modest charge of BDT 1,500–2,500 (~$13–22 USD) per property, the platform becomes profitable within the first 10–15 properties per month.

---

## What We Cannot Run for Free

We evaluated free tiers across all major cloud platforms. The app requires 5 always-on services simultaneously (database, job queue, API server, background worker, frontend). No free hosting plan supports this architecture reliably:

- **Render free tier** — database expires after 90 days, no free Redis, services sleep
- **Fly.io free tier** — insufficient for 5 services simultaneously
- **Vercel / Netlify** — frontend only, cannot run the backend or video worker
- **Heroku** — free tier discontinued in 2022

Railway is the most cost-effective paid option for our multi-service setup and the best developer experience for deploying Docker-based apps.

---

## Summary

| Category | Low Estimate | High Estimate |
|---|---|---|
| Monthly fixed (hosting + ElevenLabs) | $25 | $50 |
| Variable (per property, Claude + Runway + storage) | $2.00 | $4.40 |
| **Breakeven (30 properties/month)** | **~$115** | **~$182** |

The largest single cost driver is **Runway video generation**, which scales linearly with usage. All other costs are modest. The platform is economically viable at launch-level volumes with a per-property pricing model.

---

*Prices are estimates based on current API provider pricing (May 2026). Verify current rates at railway.app, runwayml.com, elevenlabs.io, and anthropic.com before finalizing budgets.*
