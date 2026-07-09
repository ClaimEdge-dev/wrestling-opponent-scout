# Wrestling Platform Reference

## USA Bracketing

### Login Flow
1. GET https://www.usabracketing.com/login
2. POST username + password to login form
3. Follow redirects to dashboard
4. Navigate to /events/<uuid>
5. Extract bracket data

### Bracket Page Structure
```
/events/<uuid>
  → Shows event overview
  → /events/<uuid>/brackets
    → Lists weight classes
    → /events/<uuid>/brackets/<weight_class_id>
      → Full bracket with seeds
      → Wrestler names, teams, states
      → Match results (live updates)
```

### Key Selectors (for scraping)
| Element | CSS Selector |
|---------|-------------|
| Bracket container | `.bracket-container` or `.bracket` |
| Wrestler name | `.wrestler-name` |
| Team/club | `.wrestler-team` |
| Seed number | `.seed-number` |
| Match result | `.match-result` |
| Weight class tabs | `.weight-class-tab` |

### Rate Limits
- No documented rate limits
- Be respectful: max 1 request per 2 seconds
- Use session cookies to maintain login state

---

## Trackwrestling

### Profile URL Pattern
```
https://www.trackwrestling.com/tw/membership/ViewProfile.jsp?twId=<ID>
```

### Profile Data Available
- Name, team, state
- Season record (wins-losses)
- Rank Value (0.00-1.00)
- Tournament history
- Match-by-match results
- Pins, tech falls, majors count

### Search URL
```
https://www.trackwrestling.com/tw/membership/findmembers.jsp
```

---

## FloWrestling

### Profile URL Pattern
```
https://www.flowrestling.org/people/<id>-<name>
https://www.flowwrestling.org/nextgen/people/<id>
```

### Profile Data Available
- Name, team, state
- Match videos (requires subscription)
- Ranking position
- Tournament coverage articles
- Event results

### Video URL Pattern
```
https://www.flowwrestling.org/video/<id>
```
