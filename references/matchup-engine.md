# Matchup Engine Reference

## Four-Pillar Model

### Pillar Weights
| Pillar | Weight | Description |
|--------|--------|-------------|
| P1 Result Strength | 35% | Win/loss quality, placements, bonus rate |
| P2 Style Profile | 30% | Scoring preferences, position strength |
| P3 Competition Level | 25% | Tournament tiers faced |
| P4 Weight Fit | 10% | Natural weight, cut difficulty |

### EGO Rating System
- Base: 1500
- K-factor: 32 (adjustable by tier)
- Margin modifiers: Fall +0.3, TF +0.2, MD +0.1
- State competitiveness: Tier 1 states (IL, OH, PA, NJ, MN) at 1.2x

### Win Probability Formula
```python
def win_probability(wrestler_a, wrestler_b, h2h=None):
    pillar_diff = sum((a.pillars[p] - b.pillars[p]) * PILLAR_WEIGHTS[p] for p in PILLARS)
    ego_diff = (a.ego - b.ego) / 400
    h2h_bonus = h2h_advantage(h2h) if h2h else 0
    
    combined = pillar_diff * 0.6 + (1 / (1 + 10**(-ego_diff))) * 0.3 + h2h_bonus * 0.1
    return 1 / (1 + math.exp(-combined * 1.5))
```

## Credential Tiers

| Tier | EGO Base | Criteria |
|------|----------|----------|
| ELITE | 1800 | National champion, multiple top-3 finishes |
| NATIONAL | 1650 | National qualifier, top-8 at major nationals |
| STATE | 1500 | State placer, top-4 at state |
| REGIONAL | 1350 | Regional qualifier, sectional champion |
| LOCAL | 1200 | Local tournament experience |
| UNKNOWN | 1300 | No verified data |
