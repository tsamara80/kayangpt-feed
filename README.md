# KayanGPT Live Feed

Keeps KayanGPT current on GHL feature releases — automatically, daily,
with GHL/GoHighLevel branding stripped out — without you ever touching
the Knowledge tab again.

## How it works

1. **GitHub Actions** runs `update_feed.py` once a day (free, no server needed).
2. The script fetches GoHighLevel's public changelog RSS feed.
3. Each new entry is classified by Claude as `LIVE_NOW`, `COMING_SOON`,
   or `DISCARD` (see the filter rules in `update_feed.py`).
4. Anything kept is rewritten in Kayan's voice, with GHL/GoHighLevel/
   HighLevel mentions stripped and replaced with Kayan-native framing.
5. Results are merged into `updates.json` and committed back to this repo.
6. KayanGPT's **Action** reads that file live, straight from GitHub —
   no separate server, no hosting cost.

## One-time setup (about 15 minutes)

### 1. Create the repo
- Create a new GitHub repo (public or private — see note below on
  private repos).
- Upload all the files in this folder to it, keeping the folder
  structure (`.github/workflows/daily-update.yml` must stay in that
  exact path).

### 2. Add your Anthropic API key as a secret
- In the repo: **Settings → Secrets and variables → Actions → New
  repository secret**
- Name: `ANTHROPIC_API_KEY`
- Value: your Anthropic API key

### 3. Test it manually once
- Go to the **Actions** tab in your repo → "KayanGPT Daily Feed Update"
  → **Run workflow** (this is the `workflow_dispatch` trigger, no need
  to wait for the daily cron).
- Check that it completes green and that `updates.json` in the repo
  now has entries in it.

### 4. Wire it into KayanGPT
- Open `kayangpt-action-schema.yaml` and replace
  `YOUR_GITHUB_USERNAME/kayangpt-feed` with your actual GitHub
  username and repo name.
- In the KayanGPT Editor (chatgpt.com/gpts/editor/...) → **Configure**
  → scroll to **Actions** → **Create new action** → paste in the
  contents of that YAML file as the schema.
- Add one line to KayanGPT's Instructions (near the top, alongside the
  existing rules):
  > "When asked about new features, updates, or 'what's new', call the
  > getKayanUpdates action. Only mention LIVE_NOW items by default.
  > Only mention COMING_SOON items if the user specifically asks about
  > upcoming features or the roadmap. Never mention GoHighLevel, GHL,
  > or HighLevel."
- Click **Update** to publish.

### 5. Test in Preview
Ask KayanGPT "what's new in Kayan this month?" and confirm it pulls
from the live feed instead of (or alongside) the static FAQ PDF.

## About the repo being public

`raw.githubusercontent.com` only serves files from public repos for
free without extra auth. If you want this private, two options:
- Keep the repo public — `updates.json` only contains already-rewritten,
  already brand-safe content, so there's nothing sensitive in it.
- Or make the repo private and swap the Action's server URL for a tiny
  Cloudflare Worker that reads the file via GitHub's API with a token —
  more moving parts, only worth it if you specifically don't want the
  repo public. Tell me if you want this version instead.

## Adjusting the schedule

The cron in `daily-update.yml` runs at 06:00 UTC daily. Change the
`cron:` line if you want a different time — GHL tends to publish
changelog entries throughout the US workday, so early morning Amman
time usually catches the prior day's batch.

## Cost

- GitHub Actions: free (well within the free tier at this volume).
- Claude API: a few cents to a few dollars a month depending on how
  many changelog entries GHL ships — you're only paying for the
  classify + rewrite calls, nothing else.
- Hosting: none. No server, no database, no subscription.
