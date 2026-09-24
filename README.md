# Kayan updates feed (private)

Daily pipeline that turns upstream changelog entries into Kayan feature updates in English and Arabic.

This repo must stay PRIVATE. It holds the source links, the raw upstream text and the prompts. Only the clean file is published, to the separate public repo named in the PUBLIC_REPO variable.

## Files

* update_feed.py: the pipeline (classify, rewrite in English and Arabic, guard, publish)
* data/updates_full.json: full working data, including source links and held items (private)
* public/updates.json: the clean file, created on each run and pushed to the public repo
* .github/workflows/daily-update.yml: runs daily at 06:00 UTC, or manually from the Actions tab
* kayangpt-action-schema.yaml: the action schema for KayanGPT until it retires on 11 December 2026

## Settings this repo needs

* Secret ANTHROPIC_API_KEY
* Secret PUBLIC_REPO_TOKEN: fine grained token with Contents read and write on the public repo only
* Variable PUBLIC_REPO: owner/name of the public repo

## Statuses in data/updates_full.json

* published: in the public feed
* discarded: not relevant to Kayan users
* held: failed the brand and rules guard twice; see its "problems" field, fix the rules or the item, then run with reclean
* legacy: written by version 1, waiting for the one time reclean run

## Rules

The Kayan rules live in KAYAN_RULES inside update_feed.py. Keep them in step with kayan_rules.md in the Support Assistant package.
