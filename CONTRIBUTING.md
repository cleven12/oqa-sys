# Contributing to OQA System

Thank you for your interest in contributing! 🎉

## Ways to Contribute

- Report bugs (use the Bug report template)
- Suggest features (use the Feature request template)
- Improve documentation
- Submit code via Pull Requests
- Test on different environments

## Development Setup

```bash
git clone https://github.com/your-username/oqa-sys.git
cd oqa-sys
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
python manage.py migrate
python manage.py runserver
```

## Running Tests

```bash
python manage.py test
```

## Code Style

- Keep it simple and readable (this is a solo/small-team project)
- Prefer vanilla JS + Django templates (no heavy frontend frameworks unless justified)
- Write or update tests for new logic

## Pro vs Open Source

The core project is open source under the LICENSE file.

Some contributors / users may be interested in the **Pro version** or freelance work. Please direct commercial inquiries to the maintainer (see README).

## Pull Request Process

1. Fork the repo and create your branch from `main`
2. Make your changes + tests
3. Ensure CI passes
4. Open a PR using the PR template
5. Be patient — reviews are done in spare time

## Questions?

Open a discussion or issue, or email the maintainer for Pro/commercial matters.

Thanks for helping keep OQA System great!
