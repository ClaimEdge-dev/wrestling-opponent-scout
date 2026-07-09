# kimi-find-skills Integration

## Overview

This skill integrates with `kimi-find-skills` to discover complementary capabilities in the wrestling skill ecosystem. Use this when building multi-skill workflows or when you need to locate related skills.

## Related Skills Map

```
wrestling-bracket-scraper (this skill)
  ├── wrestling-opponent-scout      → Four-pillar matchup analysis, credential tiers
  ├── wrestling-analytics-coach     → Elo ratings, bracket builders, social content
  └── nuway-rumble-command-center   → Tournament command center, dual simulator
```

## When to Use kimi-find-skills

### Scenario 1: Post-Scouting Analysis
After scraping bracket data, you need matchup analysis:
```
1. Run wrestling-bracket-scraper to extract bracket
2. Use kimi-find-skills to locate wrestling-opponent-scout
3. Run four-pillar matchup analysis on extracted opponents
```

### Scenario 2: Building Tournament Dashboard
You want a complete tournament management system:
```
1. Use kimi-find-skills to find all wrestling skills
2. Combine wrestling-bracket-scraper (data extraction)
   + wrestling-analytics-coach (ratings/brackets)
   + wrestling-opponent-scout (scouting reports)
```

### Scenario 3: NUWAY-Specific Workflows
For NUWAY tournament prep:
```
1. Use kimi-find-skills to find nuway-rumble-command-center
2. Combine with wrestling-bracket-scraper for bracket extraction
3. Get dual simulator, lineup optimizer, parent strategy
```

## Integration Patterns

### Pattern A: Sequential Pipeline
```
Scrape → Scout → Analyze → Report
   |        |        |         |
   v        v        v         v
[bracket] [opponent] [Elo]   [output]
```

### Pattern B: Parallel Discovery
```
                    [bracket data]
                   /      |      \
                  v       v       v
            [scout]  [analyze]  [video]
                  
            [kimi-find-skills discovers all 3]
```

## Skill Discovery Checklist

Before building a wrestling workflow, always run:
1. `kimi-find-skills` → "Find wrestling-related skills"
2. Read each skill's SKILL.md for capabilities
3. Map the workflow to the right skill sequence
4. Execute with data passing between skills

## Event-Specific Configs

### NUWAY Rumble 2026
- Primary event: `f5f0a32a-d13d-4973-b124-cd2b18f0a17c`
- Secondary event: `08d86a57-5b8d-4f1c-9efb-90065573c46f`
- Related skill: `nuway-rumble-command-center`

### Generic Events
- Extract event UUID from USA Bracketing URL
- Pass extracted bracket JSON to `wrestling-opponent-scout`
- Use `wrestling-analytics-coach` for ratings
