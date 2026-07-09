#!/usr/bin/env python3
"""
Bracket HTML Parser
Parses USA Bracketing HTML into structured JSON.
Works with downloaded HTML files or raw HTML strings.

Usage:
    python bracket-parser.py --html bracket.html --output bracket.json
    python bracket-parser.py --html bracket.html --format neon
"""

import argparse
import json
import re
from bs4 import BeautifulSoup


def parse_bracket_html(html_content):
    """Parse bracket HTML and extract structured data."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    bracket = {
        "wrestlers": [],
        "matches": [],
        "rounds": []
    }
    
    # Try multiple selector patterns
    # Pattern 1: Wrestler cards
    wrestler_cards = soup.find_all('div', class_=re.compile('wrestler|participant|competitor'))
    
    for card in wrestler_cards:
        wrestler = {}
        
        # Name
        name_elem = card.find(class_=re.compile('name|wrestler-name'))
        if name_elem:
            wrestler['name'] = name_elem.get_text(strip=True)
        
        # Team
        team_elem = card.find(class_=re.compile('team|club|school'))
        if team_elem:
            wrestler['team'] = team_elem.get_text(strip=True)
        
        # Seed
        seed_elem = card.find(class_=re.compile('seed|seed-number'))
        if seed_elem:
            wrestler['seed'] = seed_elem.get_text(strip=True)
        
        # State
        state_elem = card.find(class_=re.compile('state|location'))
        if state_elem:
            wrestler['state'] = state_elem.get_text(strip=True)
        
        if wrestler.get('name'):
            bracket['wrestlers'].append(wrestler)
    
    # Pattern 2: Table rows
    if not bracket['wrestlers']:
        rows = soup.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                wrestler = {
                    'name': cells[0].get_text(strip=True),
                }
                if len(cells) > 1:
                    wrestler['team'] = cells[1].get_text(strip=True)
                if len(cells) > 2:
                    wrestler['seed'] = cells[2].get_text(strip=True)
                bracket['wrestlers'].append(wrestler)
    
    # Extract matches
    match_elements = soup.find_all('div', class_=re.compile('match|bout|pairing'))
    for match_elem in match_elements:
        match_data = {}
        wrestlers_in_match = match_elem.find_all(class_=re.compile('wrestler|participant'))
        if len(wrestlers_in_match) >= 2:
            match_data['wrestler1'] = wrestlers_in_match[0].get_text(strip=True)
            match_data['wrestler2'] = wrestlers_in_match[1].get_text(strip=True)
            bracket['matches'].append(match_data)
    
    return bracket


def convert_to_neon_format(bracket_data, event_name="", weight_class=0, division="10U"):
    """Convert parsed bracket data to Neon database format."""
    neon_data = []
    
    for wrestler in bracket_data.get('wrestlers', []):
        neon_entry = {
            "name": wrestler.get('name', ''),
            "team": wrestler.get('team', ''),
            "state": wrestler.get('state', ''),
            "division": division,
            "primary_weight": weight_class,
            "seed": wrestler.get('seed'),
            "event": event_name,
            "sources": json.dumps([{
                "source": "USA Bracketing",
                "event": event_name,
                "date": "2026-07-09"
            }])
        }
        neon_data.append(neon_entry)
    
    return neon_data


def main():
    parser = argparse.ArgumentParser(description="Parse bracket HTML")
    parser.add_argument("--html", required=True, help="HTML file to parse")
    parser.add_argument("--output", default="parsed_bracket.json", help="Output JSON file")
    parser.add_argument("--format", choices=["json", "neon"], default="json", help="Output format")
    parser.add_argument("--event", default="NUWAY Rumble 2026", help="Event name")
    parser.add_argument("--weight", type=int, default=0, help="Weight class")
    
    args = parser.parse_args()
    
    # Read HTML
    with open(args.html, 'r') as f:
        html = f.read()
    
    # Parse
    bracket_data = parse_bracket_html(html)
    print(f"Found {len(bracket_data['wrestlers'])} wrestlers")
    print(f"Found {len(bracket_data['matches'])} matches")
    
    # Convert format if needed
    if args.format == "neon":
        output_data = convert_to_neon_format(bracket_data, args.event, args.weight)
    else:
        output_data = bracket_data
    
    # Save
    with open(args.output, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"Saved to {args.output}")


if __name__ == "__main__":
    main()
