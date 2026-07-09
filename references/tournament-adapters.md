# Tournament Adapters

## USA Bracketing
- Export: JSON from bracket view
- Fields: name, team, state, weight
- Adapter: Direct JSON import

## Trackwrestling
- Export: CSV from tournament page
- Fields: Name, Team, W-L, Place
- Adapter: `scripts/tw_adapter.py`

## NUWAY
- Export: PDF brackets
- Fields: Name, Team, State, Results
- Adapter: Manual entry or PDF parse

## Manual Entry
Format:
```json
{
  "name": "Wrestler Name",
  "team": "Club Name",
  "state": "ST",
  "weight": 75,
  "division": "10U"
}
```
