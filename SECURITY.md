# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, **please do not open a public issue**.

Instead, email the maintainer directly:

**`freelance@cleven.dev`**

Please include as much detail as possible (steps to reproduce, affected versions, etc.).

We aim to respond within 48 hours for security reports.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| Latest  | ✅ Full support     |
| Older   | Best effort        |

## Best Practices for Self-Hosting

- Always use a strong `SECRET_KEY`
- Set `DEBUG=False` in production
- Use HTTPS
- Keep Django and dependencies updated
- Consider rate limiting / WAF in front of the app

Thank you for helping keep OQA System secure.
