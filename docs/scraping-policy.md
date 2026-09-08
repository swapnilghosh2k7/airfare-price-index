# AirFareX Ethical Scraping Policy & Data Access Architecture

## 1. Ethical Principles & Compliance Statement

AirFareX strictly adheres to legal, ethical, and technical compliance standards for automated web data collection:

1. **No CAPTCHA Bypass**: AirFareX does NOT implement CAPTCHA solving, OCR bypass, or automated challenge solving.
2. **No Anti-Bot Evasion**: AirFareX does NOT implement browser fingerprint spoofing, stealth evasions, or unauthorized IP/proxy rotations intended to circumvent access controls.
3. **Robots.txt Adherence**: All live HTTP requests check site `robots.txt` permissions prior to initiating requests.
4. **Conservative Rate Limiting**: Minimum 5.0 second delays are enforced between consecutive requests to source endpoints to prevent server load.
5. **Session & Auth Respect**: Does NOT bypass login walls, paywalls, or authentication barriers.

---

## 2. Fallback Adapter Architecture

To ensure 100% full operational readiness during hackathons, demonstrations, or restricted access environments, AirFareX implements provider abstractions:

- `MockFareProvider`: Generates realistic synthetic airfare quotes using economic pricing curves.
- `DatasetFareProvider`: Loads CSV reference airfare datasets.
- `PermittedLiveScraperAdapter`: Rate-limited, robots.txt-compliant adapter for authorized endpoints.
