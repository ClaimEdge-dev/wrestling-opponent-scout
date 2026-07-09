#!/usr/bin/env python3
"""
USA Bracketing Auto-Login + Bracket Scraper
Logs into usabracketing.com, navigates to event, extracts bracket data.

Usage:
    python scrape-usa-bracketing.py --event f5f0a32a-d13d-4973-b124-cd2b18f0a17c --weight 75
    python scrape-usa-bracketing.py --event f5f0a32a-d13d-4973-b124-cd2b18f0a17c --all-weights
    USABRACKETING_PASSWORD="mypassword" python scrape-usa-bracketing.py --event <uuid> --weight 80

Environment Variables:
    USABRACKETING_USERNAME - defaults to "chasekrapil"
    USABRACKETING_PASSWORD - required
"""

import argparse
import json
import os
import sys
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# Configuration
BASE_URL = "https://www.usabracketing.com"
LOGIN_URL = f"{BASE_URL}/login"
EVENT_URL_TEMPLATE = f"{BASE_URL}/events/{{event_id}}"
BRACKET_URL_TEMPLATE = f"{BASE_URL}/events/{{event_id}}/brackets"

# Credentials from environment
USERNAME = os.environ.get("USABRACKETING_USERNAME", "chasekrapil")
PASSWORD = os.environ.get("USABRACKETING_PASSWORD", "")

# Known event UUIDs
KNOWN_EVENTS = {
    "rumble-2026-primary": "f5f0a32a-d13d-4973-b124-cd2b18f0a17c",
    "rumble-2026-secondary": "08d86a57-5b8d-4f1c-9efb-90065573c46f",
}


def get_credentials():
    """Get login credentials from env var or prompt."""
    username = USERNAME
    password = PASSWORD
    
    if not password:
        import getpass
        print(f"USA Bracketing login for: {username}")
        password = getpass.getpass("Enter password: ")
    
    return username, password


def login(session, username, password):
    """Login to USA Bracketing and return authenticated session."""
    print(f"[*] Logging into USA Bracketing as {username}...")
    
    # Step 1: Get login page (extract CSRF token if needed)
    resp = session.get(LOGIN_URL)
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Step 2: Find login form fields
    login_data = {
        'username': username,
        'password': password,
    }
    
    # Check for remember me checkbox
    remember = soup.find('input', {'name': 'remember'})
    if remember:
        login_data['remember'] = 'on'
    
    # Step 3: Submit login
    resp = session.post(LOGIN_URL, data=login_data, allow_redirects=True)
    
    # Step 4: Verify login
    if 'login' in resp.url.lower() and resp.status_code == 200:
        # Check for error message
        soup = BeautifulSoup(resp.text, 'html.parser')
        error = soup.find('div', class_='alert-danger') or soup.find('div', class_='error')
        if error:
            print(f"[X] Login failed: {error.get_text(strip=True)}")
            return False
    
    if resp.status_code == 200:
        print("[+] Login successful!")
        return True
    else:
        print(f"[X] Login failed: HTTP {resp.status_code}")
        return False


def extract_bracket_data(session, event_id, weight_class=None):
    """Extract bracket data from event page."""
    print(f"[*] Fetching bracket data for event {event_id}...")
    
    # Navigate to event brackets page
    bracket_url = BRACKET_URL_TEMPLATE.format(event_id=event_id)
    resp = session.get(bracket_url)
    
    if resp.status_code != 200:
        print(f"[X] Failed to fetch bracket: HTTP {resp.status_code}")
        return None
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Parse bracket data
    bracket_data = {
        "event_id": event_id,
        "event_url": EVENT_URL_TEMPLATE.format(event_id=event_id),
        "weight_classes": [],
        "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%S")
    }
    
    # Extract weight class tabs
    weight_tabs = soup.find_all('a', class_='weight-class-tab') or soup.find_all('div', class_='weight-class')
    
    for tab in weight_tabs:
        wc_name = tab.get_text(strip=True)
        wc_id = tab.get('href', '').split('/')[-1] if tab.get('href') else None
        
        bracket_data["weight_classes"].append({
            "name": wc_name,
            "id": wc_id,
            "wrestlers": []
        })
    
    # If specific weight requested, extract those wrestlers
    if weight_class:
        # Find wrestlers in the specified weight class
        wrestler_elements = soup.find_all('div', class_='wrestler') or soup.find_all('tr', class_='bracket-row')
        
        for elem in wrestler_elements:
            name_elem = elem.find(class_='wrestler-name') or elem.find('td', class_='name')
            team_elem = elem.find(class_='wrestler-team') or elem.find('td', class_='team')
            seed_elem = elem.find(class_='seed-number') or elem.find('td', class_='seed')
            
            wrestler = {
                "name": name_elem.get_text(strip=True) if name_elem else "Unknown",
                "team": team_elem.get_text(strip=True) if team_elem else "",
                "seed": seed_elem.get_text(strip=True) if seed_elem else None,
            }
            bracket_data["wrestlers"] = bracket_data.get("wrestlers", []) + [wrestler]
    
    # Save raw HTML for manual parsing if needed
    bracket_data["raw_html_sample"] = resp.text[:5000]
    
    return bracket_data


def save_to_neon(bracket_data):
    """Save bracket data to Neon database."""
    print("[*] Saving to Neon database...")
    # This would use psycopg2 to insert into tournament_brackets table
    # For now, just print the data
    print(json.dumps(bracket_data, indent=2))
    print("[+] Data ready for Neon import")


def main():
    parser = argparse.ArgumentParser(description="USA Bracketing Scraper")
    parser.add_argument("--event", required=True, help="Event UUID or alias (rumble-2026-primary, rumble-2026-secondary)")
    parser.add_argument("--weight", type=int, help="Weight class to extract (e.g., 75, 80)")
    parser.add_argument("--all-weights", action="store_true", help="Extract all weight classes")
    parser.add_argument("--output", default="bracket_data.json", help="Output file")
    parser.add_argument("--save-db", action="store_true", help="Save to Neon database")
    
    args = parser.parse_args()
    
    # Resolve event alias
    event_id = KNOWN_EVENTS.get(args.event, args.event)
    
    # Get credentials
    username, password = get_credentials()
    
    # Create session
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # Login
    if not login(session, username, password):
        sys.exit(1)
    
    # Extract bracket data
    bracket_data = extract_bracket_data(session, event_id, args.weight)
    
    if bracket_data:
        # Save to file
        with open(args.output, 'w') as f:
            json.dump(bracket_data, f, indent=2)
        print(f"[+] Bracket data saved to {args.output}")
        
        # Optionally save to Neon
        if args.save_db:
            save_to_neon(bracket_data)
    else:
        print("[X] Failed to extract bracket data")
        sys.exit(1)


if __name__ == "__main__":
    main()
