# Deployment Guide

## Recommended: Docker (Easiest Pro Path)

```bash
cp .env.example .env
# Edit .env with production values (strong SECRET_KEY, DEBUG=False, DB settings)
docker compose up -d --build
```

## Traditional (VPS)

1. Install Python 3.12, Postgres (recommended), nginx
2. `git clone ...`
3. `pip install -r requirements.txt`
4. Setup systemd + gunicorn (example in nginx/quiz.conf)
5. Use Certbot for SSL

## Environment Variables (Important)

See `.env.example` for all options.

For Pro hosted, we manage all of this for you.

## Scaling Notes

For > 200 concurrent students:
- Use Postgres
- Run with 4-8 gunicorn workers
- Consider Redis for future caching/session (Pro feature)

Questions? Email the freelancer.
