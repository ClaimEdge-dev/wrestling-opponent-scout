# Credential Classifier

## Tier Definitions

### ELITE
- National champion (USAW, NUWAY, AAU)
- Multiple top-3 national finishes
- FloWrestling ranked
- 200+ wins, 90%+ win rate

### NATIONAL
- Top-8 at major national tournament
- National qualifier with competitive record
- State champion + national exposure

### STATE
- State placer (top-4)
- Regional champion
- 100+ wins with strong state-level record

### REGIONAL
- Sectional/qualifier level
- Local tournament champion
- 50+ wins

### LOCAL
- Beginner to intermediate
- Few verified tournaments
- < 50 matches recorded

### UNKNOWN
- No verified data
- Cannot classify

## Auto-Classification Algorithm

```python
def auto_classify(wins, losses, national_places, state_places):
    if national_places and min(national_places) <= 3:
        return "ELITE"
    if national_places and min(national_places) <= 8:
        return "NATIONAL"
    if state_places and min(state_places) <= 4:
        return "STATE"
    if wins >= 50:
        return "REGIONAL"
    if wins >= 10:
        return "LOCAL"
    return "UNKNOWN"
```

## State Competitiveness

| Tier | States | Multiplier |
|------|--------|------------|
| 1 | IL, OH, PA, NJ, MN | 1.2x |
| 2 | IN, MI, WI, IA, MO | 1.0x |
| 3 | All others | 0.9x |
