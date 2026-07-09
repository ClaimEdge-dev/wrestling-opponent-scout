# Credentials Setup

## Secure Credential Storage

Never hardcode passwords in scripts. Use these methods:

### Method 1: Environment Variables (Recommended)

```bash
export USABRACKETING_USERNAME="chasekrapil"
export USABRACKETING_PASSWORD="your-password-here"
export TRACKWRESTLING_USERNAME="your-username"
export TRACKWRESTLING_PASSWORD="your-password-here"
export FLOWRESTLING_USERNAME="your-username"
export FLOWRESTLING_PASSWORD="your-password-here"
```

### Method 2: .env File

Create `.env` in the skill directory:
```
USABRACKETING_USERNAME=chasekrapil
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

The following login is pre-authorized for Chase Krapil:

| Platform | Username | Password Source |
|----------|----------|-----------------|
| USA Bracketing | chasekrapil | `USABRACKETING_PASSWORD` env var |

## USA Bracketing Event URLs

| Event | UUID | URL |
|-------|------|-----|
| NUWAY Rumble 2026 (Primary) | f5f0a32a-d13d-4973-b124-cd2b18f0a17c | [Link](https://www.usabracketing.com/events/f5f0a32a-d13d-4973-b124-cd2b18f0a17c) |
| NUWAY Rumble 2026 (Secondary) | 08d86a57-5b8d-4f1c-9efb-90065573c46f | [Link](https://www.usabracketing.com/events/08d86a57-5b8d-4f1c-9efb-90065573c46f) |

## 2-Factor Authentication

USA Bracketing does NOT use 2FA. Single username/password login.
Trackwrestling and FloWrestling may require additional verification.
