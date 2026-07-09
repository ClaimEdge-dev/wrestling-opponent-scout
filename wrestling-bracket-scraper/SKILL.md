---
name: wrestling-bracket-scraper
description: Auto-login and scraping system for USA Bracketing, Trackwrestling, and FloWrestling. Logs into wrestling bracket platforms using stored credentials, extracts bracket data, match results, and opponent profiles. Integrates with wrestling-opponent-scout Neon database. Triggers on requests to scrape wrestling brackets, login to USA Bracketing, extract bracket data, auto-scrape tournament results, or access login-protected wrestling platforms.
---

# Wrestling Bracket Scraper

Auto-login and data extraction system for wrestling bracket platforms. Logs in, navigates brackets, extracts opponent data, and persists to Neon database.

## Quick Start

```
1. Set credentials via environment variables (see references/credentials-setup.md)
2. Run: python scripts/scrape-usa-bracketing.py --event <uuid> --weight <lbs>
3. Data auto-saves to Neon DB wrestling-scout-db project
```

## Supported Platforms

| Platform | Login Method | Data Available | Skill Trigger |
|----------|-------------|----------------|---------------|
| **USA Bracketing** | Username + Password | Brackets, seeds, results, match times | "scrape USA Bracketing" |
| **Trackwrestling** | Username + Password | Profiles, records, match history | "scrape Trackwrestling" |
| **FloWrestling** | Username + Password | Videos, rankings, profiles | "scrape FloWrestling" |

## Credentials

Read `references/credentials-setup.md` for secure credential storage.

**USA Bracketing Login:**
- URL: https://www.usabracketing.com/login
- Username: chasekrapil
- Password: Set via `USABRACKETING_PASSWORD` env var
- Event URLs:
  - https://www.usabracketing.com/events/f5f0a32a-d13d-4973-b124-cd2b18f0a17c
  - https://www.usabracketing.com/events/08d86a57-5b8d-4f1c-9efb-90065573c46f

## Agent Workflow

### Agent 1: USA Bracketing Login Agent
1. Navigate to login page
2. Enter username (chasekrapil)
3. Enter password (from env var)
4. Click "Log in"
5. Navigate to event URL
6. Extract bracket HTML
7. Parse wrestler names, teams, seeds
8. Save to Neon DB

### Agent 2: Trackwrestling Profile Scraper
1. Login to Trackwrestling
2. For each opponent in bracket:
   - Search profile
   - Extract record, rank value, placements
   - Save to Neon DB

### Agent 3: FloWrestling Video Finder
1. Login to FloWrestling
2. For each opponent:
   - Search profile
   - Extract video URLs, rankings
   - Save to Neon DB

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/scrape-usa-bracketing.py` | Login + extract bracket data | `--event <uuid> --weight <lbs>` |
| `scripts/scrape-trackwrestling.py` | Extract opponent profiles | `--wrestler "Name" --state "ST"` |
| `scripts/scrape-flowrestling.py` | Find match videos | `--wrestler "Name"` |
| `scripts/bracket-parser.py` | Parse bracket HTML to JSON | `--html file.html --output bracket.json` |

## Neon Integration

All scraped data feeds into the wrestling-scout-db project:
- `wrestler_profiles` — updated with records, rank values, URLs
- `tournament_brackets` — full bracket JSON
- `match_history` — match results as they come in

## Skill Discovery Integration

This skill works alongside `kimi-find-skills` for capability discovery. When building bracket-related workflows, use `kimi-find-skills` to locate complementary skills:

```
Related skills in the ecosystem:
- wrestling-opponent-scout    → Four-pillar matchup analysis, credential classification
- wrestling-analytics-coach   → Elo ratings, tournament management, bracket builders
- nuway-rumble-command-center → Tournament command center for NUWAY events
```

See `references/kimi-find-skills-integration.md` for detailed integration patterns.
