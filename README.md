# OQA System — Online Quiz & Assessment

[![CI](https://github.com/YOUR_USERNAME/oqa-sys/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/oqa-sys/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/YOUR_USERNAME/oqa-sys)](LICENSE)
[![Open Source](https://img.shields.io/badge/Open%20Source-Yes-brightgreen)](README.md)

A professional, secure, open-source web application for running timed online quizzes and assessments. Designed for teachers and schools who want a fair, low-friction testing experience with strong anti-cheat features and stratified question pools.

No student accounts required. Students enter via a short code + basic details.

**Status:** Production-ready open source core.  
**Pro version & freelance support available** — see below.

## Key Features

- **Manual question creation only** — clean manual forms for MCQ and True/False (Excel import removed for simplicity and reliability).
- **Stratified question groups** — define groups (Easy/Medium/Hard or topic sections) with `pick_count`. Each student gets a randomized balanced subset.
- **Multiple timer modes** — Quiz timer, per-question timer, or both.
- **Server-side time authority** + auto-submit on expiry.
- **Powerful anti-cheat** — tab-switch / blur / copy / paste / right-click logging + visible suspicion counts for teachers.
- **Live monitoring** — real-time view of active students (progress, time left, suspicion).
- **Results & CSV export** — detailed per-student results with answer breakdown for auto-submitted sessions.
- **Choice & question order randomization** per student.
- **No student login friction** — just name + reg # + email. Duplicate attempt prevention via unique (quiz + reg#).
- Modern responsive UI powered by Tailwind CDN + Alpine.js + Lucide (no build step).

### Architecture at a Glance

```mermaid
flowchart TB
    subgraph Student
        A[Landing → Enter Code]
        B[Submit Details]
        C[Timed Quiz + Anti-Cheat]
    end
    subgraph Backend
        D[Session + Timer Authority]
        E[Stratified Question Selection]
        F[Suspicion Logging]
    end
    subgraph Teacher
        G[Create Quiz + Groups]
        H[Live Monitor]
        I[Results + Export]
    end

    A --> B --> C
    C --> D & E & F
    G --> H & I
```

See full anti-cheat algorithm + more diagrams in [docs/ANTI_CHEAT_ALGORITHM.md](docs/ANTI_CHEAT_ALGORITHM.md)

## ❤️ Support the Developer

If OQA System helps you run fair assessments, please consider supporting the creator:

**[👉 Support Cleven](https://snippe.me/pay/support-cleven)**

Your support directly helps maintain the open source core and develop new features (including Pro enhancements).

---

## Tech Stack

- Django 5.2
- Vanilla JS + Alpine.js (CDNs)
- SQLite (dev) / MySQL/Postgres (prod)
- Minimal dependencies

## Quick Start (Development)

> **Pro Tip:** Use Docker for the fastest professional setup:
> ```bash
> docker compose up --build
> ```

```bash
git clone https://github.com/YOUR_USERNAME/oqa-sys.git
cd oqa-sys

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env: set a strong SECRET_KEY, DEBUG=True

python manage.py migrate
python manage.py createsuperuser   # or register via web

python manage.py runserver
```

Visit http://127.0.0.1:8000/

- Student flow: enter quiz code on landing
- Teacher: `/accounts/register/` then login → dashboard

## Production / Self-Host Notes

1. Set `DEBUG=False`
2. Strong `SECRET_KEY`
3. Set `ALLOWED_HOSTS`
4. Use a real DB (Postgres recommended)
5. Collect static: `python manage.py collectstatic`
6. Run behind gunicorn + nginx (sample config in `nginx/`)
7. Configure proper email backend if extending notifications

See docs/ for more.

## Making a Quiz (Teacher Flow)

1. Create quiz → set title, duration (minutes), pass %, timer mode, randomization options.
2. Create Question Groups (optional but recommended for fairness):
   - e.g. "Easy" pick 6 of 12, 1 mark each
   - "Medium" pick 3 of 8, 3 marks each
3. Add questions manually under each group (or ungrouped).
4. Activate the quiz.
5. Share the `QZ-XXXXXX` code or direct link.

## Student Experience

- Clean focused UI
- Auto-save answers
- Navigator + progress
- Timer always synced to server
- Anti-cheat events are logged (teachers review later)
- Score shown immediately on submit. Detailed correctness only shown on timer auto-submit.

## Important Design Decisions

- **Manual entry only** — removed bulk Excel to keep deployment simple and remove external dependency surface.
- **Groups drive selection** — if you define groups with `pick_count`, students receive different questions while preserving difficulty balance.
- CSRF is enforced on AJAX APIs.
- Time calculations are server authoritative.

## Project Structure

```
oqa-sys/
├── accounts/          # Teacher auth (password + profile)
├── quiz/
│   ├── models.py
│   ├── views.py
│   ├── api.py         # Student session + heartbeat + answer + monitor
│   ├── forms.py
│   ├── utils/
│   │   ├── timer.py
│   │   ├── export.py   # CSV results
│   │   └── selection.py # Stratified question picking
│   └── templates/...
├── static/
├── config/
├── manage.py
└── requirements.txt
```

## Roadmap / Ideas for Contributors

- Optional written-answer / calculation question type (future Pro + OSS candidate)
- Better analytics dashboard
- Optional email notifications on quiz completion
- Docker + one-click deploy scripts
- Multi-language

## Security & Fairness

See the dedicated [Anti-Cheat Algorithm + Diagrams](docs/ANTI_CHEAT_ALGORITHM.md) and [Architecture Overview](docs/ARCHITECTURE.md) (includes Mermaid flows).

This system raises the cost of casual cheating. Determined remote cheating (phones etc.) still requires human invigilation.

**Pro version** adds deeper analytics and optional webcam/proctoring hooks.
```

I should insert this in a good place, perhaps after features.

To make it attractive, place it under a new section.

Since search_replace needs exact match, find a good insertion point.

## License

See [LICENSE](LICENSE)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Pull requests are welcome!

## 💖 Sponsor the Project

If OQA System saves you time or helps your school, please consider sponsoring the maintainer:

**[👉 Support Cleven](https://snippe.me/pay/support-cleven)**

- GitHub Sponsors link also available in [.github/FUNDING.yml](.github/FUNDING.yml) (set your username)

Every sponsor helps keep the project maintained and improves the open source core.

## 🚀 Pro Version & Freelance Services

The **core OQA System is completely free and open source**.

I also offer a **Pro version** and professional freelance services:

### Pro Features (examples)
- Hosted SaaS / managed instance (no self-hosting hassle)
- Advanced analytics dashboard + export options
- Student bulk import & class roster management
- Custom branding, themes, and white-labeling
- LMS / Google Classroom / integration hooks
- Enhanced reporting, audit logs, and compliance features
- Priority email + video support + SLA
- Custom development of missing features

### Contact the Freelancer

📧 **Email me directly for Pro licensing, demos, quotes, or custom development work:**

**`clevengodsontech@gmail.com`**

I reply within 24–48 hours. Please include:
- Number of expected students / quizzes
- Self-hosted vs hosted preference
- Any custom requirements

This is how I fund ongoing development of the open source project while offering value-added services.

---

Made with ❤️ to be simple, fair, and professional for real classrooms and educators.

Happy teaching!
