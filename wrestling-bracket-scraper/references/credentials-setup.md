# Credentials Setup

## Secure Credential Storage

Never hardcode passwords in scripts. Use these methods:

### Method 1: Environment Variables (Recommended)

```bash
export USABRACKETING_USERNAME="krapilbobby@gmail.com"
export USABRACKETING_PASSWORD="your-password-here"
export TRACKWRESTLING_USERNAME="your-username"
export TRACKWRESTLING_PASSWORD="your-password-here"
export FLOWRESTLING_USERNAME="your-username"
export FLOWRESTLING_PASSWORD="your-password-here"
```

### Method 2: .env File

Create `.env` in the skill directory:
```
USABRACKETING_USERNAME=krapilbobby@gmail.com
USABRACKETING_PASSWORD=your-password
```

Scripts load via `python-dotenv`.

### Method 3: Prompt at Runtime

If no env var is set, the script prompts securely:
```python
import getpass
password = getpass.getpass("USA Bracketing password: ")
```

## Authorized Login

The following login is pre-authorized and validated:

| Platform | Login Field | Username | Password Source |
|----------|-------------|----------|-----------------|
| USA Bracketing | `login` (email) | krapilbobby@gmail.com | `USABRACKETING_PASSWORD` env var |

**Note:** The parent account (krapilbobby@gmail.com) manages Chase's wrestler profile. The login field accepts email, not the wrestler username (Chasekrapil).

**Validated Password:** Set via `USABRACKETING_PASSWORD` environment variable. If not set, script will prompt securely.

**Chase's Wrestler Profile:**
- USAW ID: 2401891901
- Username: Chasekrapil
- DOB: 2015-09-06 (10U division)
- State: Illinois

## USA Bracketing Event URLs

| Event | UUID | URL | Type |
|-------|------|-----|------|
| NUWAY Rumble 2026 (Individual) | f5f0a32a-d13d-4973-b124-cd2b18f0a17c | [Link](https://www.usabracketing.com/events/f5f0a32a-d13d-4973-b124-cd2b18f0a17c) | Individual Tournament |
| NUWAY Rumble 2026 (Duals) | 08d86a57-5b8d-4f1c-9efb-90065573c46f | [Link](https://www.usabracketing.com/events/08d86a57-5b8d-4f1c-9efb-90065573c46f) | Dual Tournament |

**Chase's Division:** Open 10 and Under (UUID: 12753c18-2ffb-416c-abc0-95701ac3c8d7)

## Key URL Patterns

```
# Login
POST https://www.usabracketing.com/login
  Fields: _token (CSRF), login (email), password, remember

# Event Sub-Pages
/events/{event_id}                          → Event overview
/events/{event_id}/brackets                 → Brackets
/events/{event_id}/wrestlers                → Wrestler list
/events/{event_id}/weights                  → Weight classes
/events/{event_id}/bout_board?public=true   → Bout board (public)
/events/{event_id}/schedule                 → Schedule
/events/{event_id}/teams                    → Teams
/events/{event_id}/my_wrestlers            → My wrestlers

# Weight Class Detail
/events/{event_id}/weights/{weight_uuid}/wrestlers?context=weight
/events/{event_id}/weights/{weight_uuid}/bracket

# Wrestler Profile
/my_account/athletes/{uuid}/show_profile
```

## Weight Classes (Open 10 and Under)

| Weight | UUID |
|--------|------|
| 37-40 | ae668892-9aca-4b8b-b753-4bf5c69b1a49 |
| 43 | 45714c48-ef66-4d49-8fe0-45ddb3b78558 |
| 46 | 736c892b-9d6a-4e35-b4ed-dc5ea4971924 |
| 49 | 02e14a71-a2e6-481c-8401-ca9549d159ca |
| 52 | 2b4b7c0f-8c82-45ca-b5ce-474a2b62fcc2 |
| 55 | 66ec57f3-4378-4978-8568-cce156279ca2 |
| 58 | 632d5f7a-3055-4107-926d-4a55a857ce37 |
| 64 | c1d6dde9-9c9c-457e-a0fb-29bb03b7d794 |
| 64-72 | c9520ff1-a057-4709-9c57-4fc5e0bd1794 |
| **72** | a784135d-00b4-454c-8704-7ab20c58eb7e |
| **92** | 541061d5-6f94-4f91-8ee4-0d4e2c140f93 |

**Note:** There is NO 75 or 80 lb weight class. Chase at ~75-80 lbs will most likely wrestle at **72 lbs** (if under) or **92 lbs** (next class up).

## 2-Factor Authentication

USA Bracketing does NOT use 2FA. Single username/password login.
Trackwrestling and FloWrestling may require additional verification.
