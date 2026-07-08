# Morning Market Brief

A daily 20–40 minute two-host business news podcast, generated automatically every morning by ~4:45am ET from WSJ headlines + full free coverage, voiced with Gemini multi-speaker TTS, and delivered to your podcast app via a private RSS feed.

**Running cost: ~$0.35–0.55/episode → roughly $12–17/month** (Gemini API only; GitHub is free).

## How it works

1. **4:15am ET** — GitHub Actions wakes up (cloud; your computer can be off).
2. Pulls headlines from official WSJ RSS feeds (Markets, Business, Tech, Economy, World) plus CNBC, MarketWatch, Yahoo Finance.
3. Gemini picks and de-duplicates the 9–12 stories that matter, using WSJ's editorial judgment for ranking.
4. Fetches full free articles on each story (Google News), plus optional WSJ full text if you've added cookies (see below).
5. Gemini writes a ~4,500-word Morning Brew-style dialogue between Alex and Sam.
6. Gemini multi-speaker TTS voices it; ffmpeg produces the MP3.
7. Episode is published and your podcast feed updates. New episode appears in your app by 5am.

## Setup (one time, ~20 minutes)

### 1. Accounts
- Create a **GitHub** account at github.com (free). Use a strong password + enable 2FA.
- Create a **Gemini API key** at [aistudio.google.com](https://aistudio.google.com) → "Get API key". You must enable billing (pay-as-you-go) for daily TTS volume; expect ~$12–17/mo.

### 2. Create the repository
- GitHub → New repository → name it `wsj-daily-brief` → **Public** → Create.
  (Public is required for free GitHub Pages hosting of the feed. The feed URL is obscure but technically public — it only contains news summaries. If you want it fully private, GitHub Pro at $4/mo allows Pages on private repos.)
- Upload everything in this folder (drag-and-drop works: "uploading an existing file"). Keep the folder structure, including `.github/workflows/daily.yml` and `src/`.

### 3. Add secrets
Repo → Settings → Secrets and variables → Actions → New repository secret:
- `GEMINI_API_KEY` — your key from step 1.
- `WSJ_COOKIES_TXT` — *optional*, see WSJ section below. Skip it; everything works without it.

### 4. Enable GitHub Pages
Repo → Settings → Pages → Source: "Deploy from a branch" → Branch: `main`, folder `/docs` → Save.

### 5. Test run
Repo → Actions → "Daily episode" → Run workflow. Takes ~10–15 min. When green, your feed is live at:

```
https://YOUR_USERNAME.github.io/wsj-daily-brief/feed.xml
```

### 6. Subscribe in your podcast app
- **Apple Podcasts (iPhone)**: Library → ⋯ → Follow a Show by URL → paste the feed URL.
- **Overcast**: + → Add URL.
- **Pocket Casts**: Discover → search bar → paste URL.

Done. Episodes appear automatically every morning.

## Optional: WSJ full-article access

The show works well without this — WSJ feeds drive story selection and free outlets provide full detail. If you still want WSJ full text mixed in:

1. Install a "cookies.txt export" browser extension (e.g. *Get cookies.txt LOCALLY* for Chrome).
2. Log in at wsj.com, export cookies for wsj.com in Netscape format.
3. Paste the file contents into the `WSJ_COOKIES_TXT` secret.
4. Re-export every few weeks when cookies expire.

**Know the risks:** WSJ's terms of service prohibit automated access, even by subscribers. Their bot detection may block requests from GitHub's servers or, in the worst case, flag/lock your account. The pipeline treats WSJ full text as best-effort: any failure is silently skipped and never blocks your 5am episode.

## Tuning

Edit env values in `.github/workflows/daily.yml`:
- `TARGET_MINUTES` — episode length (20–40 works well; cost scales linearly).
- `SHOW_NAME`, plus `HOST_A_NAME` / `HOST_B_NAME`, `VOICE_A` / `VOICE_B` (see [Gemini voice list](https://ai.google.dev/gemini-api/docs/speech-generation)).
- Cron schedule: `15 8 * * *` is 4:15am EDT / 3:15am EST. GitHub cron is UTC and can start a few minutes late; the buffer keeps you safely before 5am.
- `GEMINI_TTS_MODEL` / `GEMINI_TEXT_MODEL` — defaults may lag Google's newest releases; check [current model names](https://ai.google.dev/gemini-api/docs/models) if you see model-not-found errors.

## Troubleshooting

- **Run failed**: Actions tab → click the run → read the log. Most common: invalid/over-quota API key, or a renamed Gemini model (update the env var).
- **No new episode in app**: podcast apps poll feeds on their own schedule; Overcast/Pocket Casts refresh fastest. Pull-to-refresh usually forces it.
- **Episode too short/long**: adjust `TARGET_MINUTES`; the script writer targets ±10%.
