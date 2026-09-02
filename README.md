# Marvel News Digest

Checks Variety, Hollywood Reporter, and Deadline RSS feeds daily for
Marvel-related articles and emails you a digest of anything new.

## Setup

1. **Sign up for Resend** (free tier, for sending email): https://resend.com
   - Create an API key.
   - Note: on the free tier you can only send email to the address you signed
     up with, unless you verify your own domain. That's fine for personal alerts.

2. **Add GitHub secrets** (repo Settings -> Secrets and variables -> Actions -> New repository secret):
   - `RESEND_API_KEY` — your Resend API key
   - `ALERT_EMAIL_TO` — the email address you want digests sent to
   - `ALERT_EMAIL_FROM` — sender address (Resend gives you a working default
     like `onboarding@resend.dev` for testing)

3. **Push this repo to GitHub.** The workflow in
   `.github/workflows/rss-digest.yml` will then run automatically every day
   at 08:00 UTC, and you can also trigger it manually any time from the
   "Actions" tab -> "Marvel News Digest" -> "Run workflow".

## Customizing

- Edit `KEYWORDS` in `rss_digest.py` to change what triggers an alert.
- Edit `FEEDS` in `rss_digest.py` to add/remove news sources.
- Edit the `cron` line in the workflow file to change how often it runs.
