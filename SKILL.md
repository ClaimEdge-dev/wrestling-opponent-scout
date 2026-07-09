---
name: wrestling-opponent-scout
description: Comprehensive youth wrestling opponent scouting and matchup analysis system. Auto-discovers wrestler profiles from Trackwrestling, FloWrestling, NUWAY Combat, and state federation databases. Classifies credentials (national/state/regional/local), runs four-pillar matchup analysis, calculates win probabilities, and generates field-ready scouting reports. Persists data to Neon Postgres for cross-tournament intelligence. Triggers on requests involving youth wrestling opponent scouting, tournament bracket analysis, wrestler profile lookup, matchup prediction, credential verification, or any wrestling scouting task.
---

# Wrestling Opponent Scout

## Overview

Comprehensive youth wrestling opponent scouting and matchup analysis system. Auto-discovers wrestler profiles from Trackwrestling, FloWrestling, NUWAY Combat, and state federation databases. Classifies credentials (national/state/regional/local), runs four-pillar matchup analysis, calculates win probabilities, and generates field-ready scouting reports. Persists data to Neon Postgres for cross-tournament intelligence.

## When to Use This Skill

- Youth wrestling opponent scouting
- Tournament bracket analysis
- Wrestler profile lookup
- Matchup prediction
- Credential verification
- Win probability calculation
- Pre-match strategy card generation

## Quick Start

1. Load bracket data (JSON from USA Bracketing or manual entry)
2. Run `scripts/scout-engine.py --bracket bracket.json --focus "Chase Krapil"`
3. Review generated scouting reports
4. Open `assets/pre-match-card.html` for tournament-day opponent cards

## Bundled Resources

### References

- `references/scouting-workflow.md` - Complete scouting procedures for each data source
- `references/matchup-engine.md` - Four-pillar model formulas, win probability calculations, EGO ratings
- `references/credential-classifier.md` - National/state/regional/local tier classification system
- `references/tournament-adapters.md` - NUWAY, IKWF, USAW, Trackwrestling, FloWrestling adapters

### Scripts

- `scripts/scout-engine.py` - Python engine for web scraping, database operations, and matchup calculations

### Assets

- `assets/pre-match-card.html` - Single-page opponent scouting card for tournament day

## Core Workflow

1. **Data Ingestion** - Import bracket or roster data
2. **Profile Discovery** - Search Trackwrestling, FloWrestling, etc.
3. **Credential Classification** - Auto-tier assignment
4. **Matchup Analysis** - Four-pillar scoring
5. **Report Generation** - Markdown + HTML cards

## Four-Pillar Model

| Pillar | Weight | Measures |
|--------|--------|----------|
| P1 Result Strength | 35% | Win quality, placements, bonus rate |
| P2 Style Profile | 30% | Scoring method, neutral/top/bottom |
| P3 Competition Level | 25% | Local to national exposure scale |
| P4 Weight Fit | 10% | Natural weight, dual role |

## Data Sources

- USA Wrestling / TheMat
- Trackwrestling
- FloWrestling
- NUWAY Combat
- State federations (IKWF, ISWA, MHWA, etc.)

## Neon Database Integration

Project: `dry-recipe-96095818`
Tables: `wrestler_profiles`, `matchup_history`, `tournament_events`, `tournament_entries`, `scouting_reports`

## Quality Rules

- Never fabricate athlete data
- Every data point requires a source URL
- All unverified fields marked `UNVERIFIED`
- All probability estimates labeled `ESTIMATE`
