# Online Quiz & Assessment System
### Full System Documentation — v1.0

> **Note:** This document describes the open source architecture.
> The core is free and open source. A **Pro version** with extra features and hosted options is available directly from the maintainer (see README).

**Repository:** oqa-sys
**Status:** Open source + Pro/freelance services available

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Cheating Problem & Mitigations](#2-cheating-problem--mitigations)
3. [Goals & Non-Goals](#3-goals--non-goals)
4. [Tech Stack & Dependencies](#4-tech-stack--dependencies)
5. [Security Architecture](#5-security-architecture)
6. [Application Structure](#6-application-structure)
7. [Database Design](#7-database-design)
8. [Business Logic](#8-business-logic)
9. [Teacher Verification (OTP + Email Link)](#9-teacher-verification-otp--email-link)
10. [API Endpoints](#10-api-endpoints)
11. [UI/UX & HCI Principles](#11-uiux--hci-principles)
12. [Performance & Rate Limiting](#12-performance--rate-limiting)
13. [Deployment Guide](#13-deployment-guide)
14. [Development Roadmap](#14-development-roadmap)

---

## 1. Problem Statement

A need exists for a web-based quiz and online test management system that allows teachers and administrators to create and manage quizzes efficiently, while providing students with a seamless and secure test-taking experience without requiring student accounts.

The system must support multiple question types including multiple choice, true/false, and calculation-based questions. Teachers need the ability to add questions either manually or through bulk Excel import, with each question carrying its own mark value grouped by difficulty category, optional time limit, and configurable attempt count for calculation questions.

Students access quizzes through a unique randomly generated quiz ID or shareable URL, identify themselves by submitting their full name, registration number, and email before starting, and cannot retake a quiz once completed. During the quiz, students are subject to either a whole-quiz timer, a per-question timer, or both simultaneously. If time expires before manual submission, the system automatically submits whatever has been answered, leaving unanswered questions blank.

Upon submission, students see only their total score to prevent answer sharing. However if the overall quiz timer expires and triggers auto-submission, students additionally see which questions they got correct or wrong without revealing the correct answers, discouraging cheating while still providing meaningful feedback.

Teachers require a live monitoring dashboard that shows currently active students identified by name and registration number, their progress through the quiz, and time remaining, updated through periodic AJAX polling. Teachers can also export quiz results as CSV for record keeping and further analysis.

The system is built as a monolithic Django application using SQLite3 during development with a migration path to PostgreSQL for production on DigitalOcean, using Django templates with vanilla JavaScript and Django REST Framework for internal AJAX endpoints.

---

## 2. Cheating Problem & Mitigations

### 2.1 The Reality

No software can fully prevent a determined student from using AI on a separate device, having a friend on a call, or sharing answers in person. The goal is to **raise the cost of cheating** and **detect suspicious behavior** after the fact so teachers have evidence.

### 2.2 What Can Be Controlled

#### Stratified Question Pool Randomization
The highest-impact mitigation. Teacher writes a pool of questions grouped by difficulty/topic. System randomly picks a fixed number from each group per student. Two students sitting next to each other get different questions entirely.

```
Teacher creates pool:
  Group A — Easy       (15 questions, 1 mark each)  → pick 5 per student
  Group B — Medium     (10 questions, 3 marks each)  → pick 3 per student
  Group C — Hard       (8 questions,  5 marks each)  → pick 2 per student

Result: every student gets 10 questions, same difficulty balance, different actual questions.
Sharing answers between students becomes useless.
```

#### MCQ Choice Randomization
Option labels (A/B/C/D) are shuffled per student per question. Even if two students get the same question, "B" means different things to each of them. Calling a friend to say "answer B" gives wrong information.

#### Tab Switch & Window Blur Detection
JavaScript detects when a student switches tabs or minimizes the browser. Each event is logged to the server with a timestamp and the question they were on. Teachers see a suspicion count per student in the results.

```javascript
document.addEventListener('visibilitychange', () => {
  if (document.hidden) logSuspicion('tab_switch');
});
window.addEventListener('blur', () => logSuspicion('window_blur'));
```

#### Copy & Right-Click Disable
Prevents quick copy-paste of question text into ChatGPT on the same browser.

```javascript
document.addEventListener('contextmenu', e => e.preventDefault());
document.addEventListener('copy', e => e.preventDefault());
```

#### Time-Per-Question Logging
Answer model stores `time_taken_seconds`. If a student consistently answers complex questions in under 5 seconds, that is a flag teachers can see in the results breakdown.

#### Short Per-Question Timers
Teacher-defined. A 30–45 second timer per question makes it impractical to type into an AI, wait for a response, read it, and answer in time.

#### Question Design (Teacher Responsibility)
- Questions with local Tanzanian or school-specific context
- Calculation questions requiring working (your calculation type)
- Slightly rephrased standard questions that confuse AI pattern matching

### 2.3 What Cannot Be Prevented (Be Honest)

| Method | Preventable? |
|---|---|
| ChatGPT on same browser | Partially — tab switch detection logs it |
| ChatGPT on a phone | No — physical invigilation needed |
| Screenshot to AI app | No |
| Friend on video/audio call | No |
| Screen sharing to friend | No |

Phone and external device cheating is a physical invigilation problem, same as traditional paper exams.

### 2.4 Suspicion Scoring for Teachers

A `SuspiciousEvent` model logs every detected event. Teachers see on the results page:

| Count | Indicator |
|---|---|
| 0 events | Clean |
| 1–3 events | Minor suspicion ⚠️ |
| 4+ events | High suspicion 🔴 |

---

## 3. Goals & Non-Goals

### In Scope (v1)
- Secure account-free student quiz experience
- Teacher email verification via OTP and email link
- Quiz creation with question groups and stratified randomization
- MCQ, True/False, and Calculation question types
- Manual question entry with optional Question Groups for stratified randomization
- Quiz-level timer, question-level timer, or both
- Auto-submit on timeout with server-side time authority
- Live student monitoring via AJAX polling
- Anti-cheat: tab switch detection, copy disable, time logging
- CSV export of results
- Easy self-host or Pro hosted options

### Out of Scope (v1)
- Student accounts or profiles
- Mobile native app
- GraphQL API
- Payment/subscription system (planned post-launch)
- Video or audio question types
- LMS integration (Moodle, Canvas)

---

## 4. Tech Stack & Dependencies

### Backend
| Component | Choice | Reason |
|---|---|---|
| Framework | Django 5.2 | Stable, batteries included, great ORM |
| REST API | Django REST Framework 3.15 | AJAX endpoints |
| Auth & Security | django-allauth 0.63 | Powerful, handles OTP + email verification securely |
| Email OTP | django-allauth built-in | No extra library needed |
| Rate Limiting | django-ratelimit 4.1 | Prevent brute force and DDoS on key endpoints |
| Excel Import | openpyxl 3.1 | Read .xlsx without external dependencies |
| Environment | python-decouple 3.8 | .env file management |
| WSGI Server | gunicorn 21.2 | Production app server |
| Database (dev) | SQLite3 | Built-in, zero config |
| Database (prod) | PostgreSQL 15 | Production grade |
| DB Adapter | psycopg2-binary 2.9 | PostgreSQL driver |

### Frontend
| Component | Choice | Reason |
|---|---|---|
| Templating | Django Templates | Server-rendered, no build step |
| Styling | TailwindCSS via CDN | No npm build, fast styling |
| Scripting | Vanilla JavaScript ES6+ | No framework overhead |
| AJAX | Fetch API | Native browser, no jQuery needed |
| Timers | setInterval / clearInterval | Native JS |

### Infrastructure
| Component | Choice |
|---|---|
| Hosting | DigitalOcean Droplet — Ubuntu 22.04 LTS |
| Reverse Proxy | Nginx on port 81 |
| SSL | Certbot + Let's Encrypt |
| Email Sending | Gmail SMTP (dev) → SendGrid free tier (prod) |
| Version Control | Git + GitHub |
| Process Manager | systemd |

### requirements.txt
```
Django==5.2
djangorestframework==3.15
django-allauth==0.63.6
django-ratelimit==4.1.0
openpyxl==3.1.5
python-decouple==3.8
gunicorn==21.2.0
psycopg2-binary==2.9.9
```

---

## 5. Security Architecture

### 5.1 Why django-allauth

`django-allauth` is the most battle-tested authentication library in the Django ecosystem. It handles:
- Email verification with secure token links
- OTP generation and validation
- Brute force protection on login
- Session management
- Password hashing (uses Django's Argon2/PBKDF2)

It replaces the need for rolling your own OTP system which is a common source of vulnerabilities.

### 5.2 Security Layers

#### Authentication & Session
- All teacher routes protected by `@login_required`
- Django sessions use `HttpOnly` and `Secure` cookies (HTTPS in prod)
- Session timeout set to 8 hours for teachers
- CSRF protection on every POST — Django middleware enforced

#### Timer Authority (Critical)
The server owns time. JavaScript timer is display only.
- `start_time` stored on `StudentSession` at quiz start
- Every AJAX heartbeat recalculates `remaining = quiz_duration - (now - start_time)`
- Server rejects any submission where time has clearly expired server-side regardless of what client says
- Prevents a student from pausing their JS timer via browser devtools

#### Input Sanitization
- All user input passes through Django forms with field-level validation
- Excel import sanitizes every cell — strips HTML, checks types, enforces lengths
- DRF serializers validate all AJAX payloads — no raw `request.data` used directly

#### Rate Limiting (django-ratelimit)
Applied on high-risk endpoints to prevent abuse and performance attacks:

```python
# Student session start — prevent quiz spam
@ratelimit(key='ip', rate='5/m', block=True)
def start_session(request): ...

# Teacher login — prevent brute force
@ratelimit(key='post:email', rate='10/h', block=True)
def login(request): ...

# AJAX heartbeat — prevent server overload
@ratelimit(key='ip', rate='30/m', block=True)
def heartbeat(request): ...

# OTP verification — prevent OTP brute force
@ratelimit(key='ip', rate='5/m', block=True)
def verify_otp(request): ...
```

#### Frontend Security
```javascript
// Disable right-click
document.addEventListener('contextmenu', e => e.preventDefault());

// Disable copy/cut
document.addEventListener('copy', e => e.preventDefault());
document.addEventListener('cut', e => e.preventDefault());

// Block dev tools shortcuts and copy shortcuts
document.addEventListener('keydown', (e) => {
  const blocked = ['c', 'v', 'u', 's', 'i', 'j'];
  if ((e.ctrlKey || e.metaKey) && blocked.includes(e.key.toLowerCase())) {
    e.preventDefault();
  }
  if (e.key === 'F12') e.preventDefault();
});
```

#### Correct Answers Never Sent to Client
The server never includes `correct_answer` in any API response. It is only used server-side during scoring. A student inspecting network traffic in DevTools will never see the answer.

#### Security Headers (Nginx)
```nginx
add_header X-Frame-Options "DENY";
add_header X-Content-Type-Options "nosniff";
add_header X-XSS-Protection "1; mode=block";
add_header Referrer-Policy "strict-origin-when-cross-origin";
```

#### Django Production Settings
```python
DEBUG = False
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'
```

---

## 6. Application Structure

Kept intentionally simple. One Django project, two apps, one settings file with environment switching via `python-decouple`.

```
online-quiz-assessment-system/
│
├── core/                        ← project config
│   ├── settings.py              ← single settings file, env-based switching
│   ├── urls.py
│   └── wsgi.py
│
├── accounts/                    ← teacher auth, OTP, email verification
│   ├── models.py                ← Teacher profile (extends allauth User)
│   ├── views.py
│   ├── urls.py
│   └── templates/
│       └── accounts/
│           ├── login.html
│           ├── register.html
│           ├── verify_otp.html
│           └── email_confirm.html
│
├── quiz/                        ← everything quiz related
│   ├── models.py
│   ├── views.py
│   ├── api.py                   ← DRF AJAX endpoints
│   ├── urls.py
│   ├── forms.py
│   ├── utils/
│   │   ├── import.py            ← Excel import logic
│   │   ├── export.py            ← CSV export
│   │   └── timer.py             ← server time calculations
│   └── templates/
│       └── quiz/
│           ├── base.html
│           ├── landing.html
│           ├── student/
│           │   ├── entry.html
│           │   ├── attempt.html
│           │   └── result.html
│           └── teacher/
│               ├── dashboard.html
│               ├── quiz_form.html
│               ├── group_form.html
│               ├── questions.html
│               ├── import.html
│               ├── monitor.html
│               └── results.html
│
├── static/
│   └── js/
│       ├── timer.js             ← countdown, color changes
│       ├── attempt.js           ← answer nav, dot grid
│       ├── autosave.js          ← heartbeat every 10s
│       └── anticheat.js         ← tab switch, copy disable
│
├── nginx/
│   └── quiz.conf
│
├── .env                         ← never committed to git
├── .gitignore
├── requirements.txt
└── manage.py
```

**Why one settings file:** Multiple settings files (base/dev/prod) add complexity that's hard to manage as a solo developer. Instead, `python-decouple` reads `.env` and switches behavior:

```python
# core/settings.py
DEBUG = config('DEBUG', default=False, cast=bool)
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': config('DB_NAME', default=BASE_DIR / 'db.sqlite3'),
    }
}
```

On dev your `.env` has `DEBUG=True` and SQLite. On production `.env` has `DEBUG=False` and PostgreSQL. Same file, no confusion.

---

## 7. Database Design

### Quiz
```
Quiz
├── id                    AutoField PK
├── title                 CharField(200)
├── description           TextField (optional)
├── quiz_code             CharField(10) unique     ← e.g. QZ-4X9K
├── timer_mode            CharField choices        ← quiz / question / both
├── quiz_duration         IntegerField             ← total seconds
├── pass_mark             IntegerField             ← percentage e.g. 50
├── randomize_questions   BooleanField default True
├── randomize_choices     BooleanField default True
├── is_active             BooleanField default False
├── created_by            FK → User
└── created_at            DateTimeField auto_now_add
```

### QuestionGroup
```
QuestionGroup
├── id                    AutoField PK
├── quiz                  FK → Quiz
├── name                  CharField(100)           ← e.g. "Easy", "Section A"
├── marks_per_question    IntegerField             ← all questions share same mark
├── pick_count            IntegerField             ← how many to pick per student
└── order                 IntegerField             ← display order
```

### Question
```
Question
├── id                    AutoField PK
├── quiz                  FK → Quiz
├── group                 FK → QuestionGroup (optional)
├── question_text         TextField
├── question_type         CharField choices        ← mcq / true_false / calculation
├── option_a              CharField (optional)
├── option_b              CharField (optional)
├── option_c              CharField (optional)
├── option_d              CharField (optional)
├── correct_answer        CharField
├── duration_seconds      IntegerField (optional)  ← per-question timer
├── max_attempts          IntegerField default 1   ← calculation type only
└── order                 IntegerField
```

> Note: `marks` field removed from Question — it lives on `QuestionGroup.marks_per_question` since all questions in a group share the same weight.

### StudentSession
```
StudentSession
├── id                    AutoField PK
├── quiz                  FK → Quiz
├── full_name             CharField(200)
├── reg_number            CharField(50)
├── email                 EmailField
├── start_time            DateTimeField auto_now_add
├── submitted_at          DateTimeField (null)
├── submitted_via         CharField choices        ← manual / auto_quiz / auto_question
├── total_score           IntegerField default 0
├── max_possible_score    IntegerField default 0
├── is_submitted          BooleanField default False
└── current_question_index IntegerField default 0

Constraint: unique_together = ('quiz', 'reg_number')  ← blocks retakes
```

### Answer
```
Answer
├── id                    AutoField PK
├── session               FK → StudentSession
├── question              FK → Question
├── chosen_answer         CharField (optional)     ← blank if unanswered
├── attempts_used         IntegerField default 0   ← calculation only
├── time_taken_seconds    IntegerField default 0   ← for suspicion analysis
├── is_correct            BooleanField default False
└── marks_awarded         IntegerField default 0
```

### SuspiciousEvent
```
SuspiciousEvent
├── id                    AutoField PK
├── session               FK → StudentSession
├── event_type            CharField choices        ← tab_switch / window_blur / shortcut_blocked
├── question_index        IntegerField
└── timestamp             DateTimeField auto_now_add
```

---

## 8. Business Logic

### 8.1 Quiz Access

1. Student visits `/` and enters quiz code, or uses direct URL `/quiz/<code>/`
2. System checks quiz exists and `is_active = True`
3. Student submits entry form: `full_name`, `reg_number`, `email`
4. System checks `unique_together(quiz, reg_number)` — if match exists, block with message: *"You have already attempted this quiz"*
5. On success, `StudentSession` created with `start_time = now()`
6. Question selection runs immediately (see 8.2)
7. Selected question order stored in Django server session

### 8.2 Stratified Question Selection

```python
selected = []
for group in quiz.groups.order_by('order'):
    pool = list(group.questions.all())
    if len(pool) < group.pick_count:
        raise ValueError(f"Group '{group.name}' has fewer questions than pick_count")
    picked = random.sample(pool, group.pick_count)
    selected.extend(picked)

if quiz.randomize_questions:
    random.shuffle(selected)

request.session['question_order'] = [q.id for q in selected]
request.session['question_total'] = len(selected)
```

If quiz has no groups (teacher did not use groups), falls back to picking all questions and shuffling if `randomize_questions = True`.

### 8.3 MCQ Choice Randomization

Choices are shuffled server-side when rendering each question, not on the client:

```python
def get_shuffled_choices(question, session_key):
    choices = [
        ('option_a', question.option_a),
        ('option_b', question.option_b),
        ('option_c', question.option_c),
        ('option_d', question.option_d),
    ]
    choices = [(k, v) for k, v in choices if v]  # remove blank options
    seed = f"{session_key}{question.id}"
    random.seed(seed)                              # deterministic per student
    random.shuffle(choices)
    random.seed()                                  # reset seed
    return choices
```

Using a seed based on session key + question id means the shuffle is consistent if a student navigates back to a question, but different between students.

### 8.4 Timer Logic

**Timer authority is on the server.**

On every AJAX heartbeat:
```python
elapsed = (timezone.now() - session.start_time).total_seconds()
remaining = quiz.quiz_duration - elapsed
if remaining <= 0:
    auto_submit(session, submitted_via='auto_quiz')
```

JavaScript timer is display only — it reflects the server's remaining time received on last heartbeat.

**Timer modes:**
- `quiz` — one countdown for full quiz, JS counts down, heartbeat syncs every 10 seconds
- `question` — JS counts down per question using `question.duration_seconds`, on zero POSTs current answer and loads next
- `both` — both timers run; whichever fires first acts

### 8.5 Auto-Submit Rules

| Scenario | `submitted_via` | Answer State |
|---|---|---|
| Student clicks Submit | `manual` | Whatever was selected |
| Quiz timer hits zero (server) | `auto_quiz` | All answered + blanks |
| Question timer hits zero | `auto_question` | Current question blank if not chosen |

### 8.6 Scoring

```python
total_score = 0
max_possible = 0

for answer in session.answers.all():
    group = answer.question.group
    marks = group.marks_per_question if group else 1
    max_possible += marks
    if answer.is_correct:
        answer.marks_awarded = marks
        total_score += marks

session.total_score = total_score
session.max_possible_score = max_possible
session.save()
```

Pass/fail: `(total_score / max_possible) * 100 >= quiz.pass_mark`

### 8.7 Result Display Rules

| `submitted_via` | What Student Sees |
|---|---|
| `manual` | Total score + pass/fail only |
| `auto_question` | Total score + pass/fail only |
| `auto_quiz` | Total score + pass/fail + per-question ✅/❌/⬜ (no correct answers) |

### 8.8 Calculation Questions

- Student types answer into text input
- Each submit attempt counted against `max_attempts`
- Server compares against `correct_answer` (case-insensitive, stripped)
- Correct → award marks, lock question, move on
- Wrong + attempts remain → show remaining count, allow retry
- Wrong + no attempts left → lock as wrong, `marks_awarded = 0`

### 8.9 Bulk Excel Import

Template columns:
```
question_text | type | option_a | option_b | option_c | option_d | correct_answer | duration_seconds | max_attempts | group_name
```

- `group_name` must match an existing `QuestionGroup.name` for that quiz
- Validation: required fields not empty, type is valid value, numeric fields are numbers
- Valid rows bulk-created; invalid rows skipped and reported with row number and reason
- Teacher downloads sample template from the import page

### 8.10 Live Monitoring

- Teacher page polls `GET /api/teacher/monitor/<quiz_id>/` every 10 seconds
- Returns active (non-submitted) sessions: `full_name`, `reg_number`, `current_question_index`, `time_remaining`, `suspicion_count`
- Submitted students move to a separate section below the live table

### 8.11 CSV Export

Django view streams `HttpResponse` with `content_type='text/csv'`.

Columns:
```
reg_number | full_name | email | total_score | max_possible | percentage | pass_fail | submitted_via | submitted_at | suspicion_events
```

---

## 9. Teacher Verification (OTP + Email Link)

### 9.1 Why django-allauth

`django-allauth` is the most secure and widely used authentication library for Django. It handles:
- Secure token generation for email verification links
- OTP generation and time-based expiry
- Brute force protection on login attempts
- Session management

Rolling your own OTP is a known security risk — allauth is the right choice.

### 9.2 Registration & Verification Flow

```
Teacher fills registration form
  (full name, email, password)
        ↓
Account created with is_active = False
        ↓
System sends email with TWO options:
  1. Verification link  (click to verify)
  2. 6-digit OTP       (enter manually)
        ↓
Teacher either:
  → Clicks link in email → auto-verified → redirected to dashboard
  → Enters OTP on /accounts/verify-otp/ → verified → redirected to dashboard
        ↓
Account is_active = True
Teacher can now create quizzes
```

### 9.3 OTP Configuration (allauth settings)

```python
# core/settings.py

INSTALLED_APPS = [
    ...
    'allauth',
    'allauth.account',
]

AUTHENTICATION_BACKENDS = [
    'allauth.account.auth_backends.AuthenticationBackend',
]

ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_SUBJECT_PREFIX = '[Quiz System] '
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1   # OTP/link expires in 24 hours
ACCOUNT_MAX_EMAIL_ADDRESSES = 1
LOGIN_REDIRECT_URL = '/teacher/dashboard/'
LOGOUT_REDIRECT_URL = '/'
```

### 9.4 Email Template

allauth allows custom email templates. Create:
```
templates/account/email/
├── email_confirmation_subject.txt
└── email_confirmation_message.txt
```

`email_confirmation_message.txt`:
```
Hello {{ user.get_full_name }},

Welcome to the Quiz & Assessment System.

You can verify your account in two ways:

OPTION 1 — Click the link below:
{{ activate_url }}

OPTION 2 — Enter this OTP code on the verification page:
{{ key }}

This link and OTP expire in 24 hours.

If you did not register, ignore this email.
```

### 9.5 OTP Rate Limiting

```python
@ratelimit(key='ip', rate='5/m', block=True)
@ratelimit(key='post:email', rate='10/h', block=True)
def verify_otp(request):
    ...
```

After 5 wrong OTP attempts in a minute, the IP is blocked for 1 minute. Prevents OTP brute force.

### 9.6 Teacher Profile Model

```python
# accounts/models.py
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    full_name = CharField(max_length=200)
    is_teacher = BooleanField(default=True)
    institution = CharField(max_length=200, blank=True)
    created_at = DateTimeField(auto_now_add=True)
```

Use Django's `AUTH_USER_MODEL = 'accounts.User'` in settings.

---

## 10. API Endpoints

All consumed internally by vanilla JavaScript. No external API consumers in v1.

| Method | Endpoint | Purpose | Auth | Rate Limit |
|---|---|---|---|---|
| POST | `/api/session/start/` | Create session, return start_time + first question | None | 5/min per IP |
| POST | `/api/session/answer/` | Save answer, return next question | Session cookie | 60/min |
| POST | `/api/session/submit/` | Final submission, calculate score | Session cookie | 3/min |
| GET | `/api/session/heartbeat/` | Sync server time, return remaining seconds | Session cookie | 30/min |
| POST | `/api/session/suspicious/` | Log a suspicious event from frontend | Session cookie | 60/min |
| GET | `/api/teacher/monitor/<quiz_id>/` | Active student list | Teacher login | 20/min |
| GET | `/api/teacher/export/<quiz_id>/` | Stream CSV | Teacher login | 10/min |

### Heartbeat Response Example
```json
{
  "remaining_seconds": 1247,
  "current_question": 4,
  "total_questions": 10,
  "is_submitted": false
}
```

### Answer Submission Payload
```json
{
  "question_id": 42,
  "chosen_answer": "option_b",
  "time_taken_seconds": 34
}
```

---

## 11. UI/UX & HCI Principles

### 11.1 Applied HCI Principles

**Visibility of System Status**
Students always know where they are. Progress bar shows `Q3 of 10`. Timer shows prominently at top and changes color: green → amber (under 30%) → red (under 10%). Submitted confirmation screen always shown.

**Match Between System and Real World**
Simple language throughout. "Start Quiz", "Submit", "Next", "Time Remaining". Radio buttons for MCQ. Toggle for True/False. Text input for Calculation. No jargon.

**User Control and Freedom**
Students can navigate back to previous questions when per-question timer is not active. Confirmation dialog before manual submit: *"Are you sure? You cannot change answers after submission."* Teachers can deactivate a quiz without deleting it.

**Consistency and Standards**
Same navigation bar, color scheme (blue primary, white background, gray accents), button styles across all pages. TailwindCSS enforces visual consistency.

**Error Prevention**
- Student entry form: all three fields required, HTML5 validation before server
- Duplicate attempt blocked at view level before database constraint fires
- Excel import validates every row before saving, reports errors row by row
- Teacher cannot set `pick_count` greater than available questions in a group

**Recognition Rather than Recall**
MCQ options always displayed as labeled choices — never typed. Current question number always visible. Dot grid navigator shows answered/unanswered at a glance.

**Flexibility and Efficiency of Use**
Manual entry with stratified Question Groups. Short quiz code (QZ-4X9K) shareable via text. CSV export for offline result processing.

**Aesthetic and Minimalist Design**
Student pages: question text, options, timer, navigation only. No sidebar, no ads, no distractions. Teacher pages are structured with clear headings and tables.

**Help Users Recognize and Recover from Errors**
Specific error messages — not generic. "Registration number already used for this quiz." Failed import shows row number and specific reason. AJAX errors show non-blocking toast notification.

### 11.2 Page Designs

**Landing Page (`/`)**
- Centered quiz code input
- Large "Enter Quiz" button
- System name at top
- No login for students

**Student Entry (`/quiz/<code>/`)**
- Quiz title and description shown first
- Three required fields: Full Name, Registration Number, Email
- Warning: "You cannot retake this quiz once started"
- Start Quiz button

**Quiz Attempt (`/quiz/<code>/attempt/`)**
- Top bar: quiz title + timer (color-coded) + `Q3 of 10`
- Question text in a large readable card
- MCQ: radio buttons A/B/C/D
- True/False: two large toggle buttons
- Calculation: text input + "Attempts remaining: 2"
- Dot grid navigator at bottom (gray = unanswered, blue = answered)
- Previous / Next navigation
- Submit button (shows confirmation dialog)

**Result (`/quiz/<code>/result/`)**
- Large: "You scored 18 / 25"
- Green PASSED or Red FAILED badge
- If `auto_quiz`: table with ✅ / ❌ / ⬜ per question (no answers shown)
- If `manual` or `auto_question`: score only
- No further navigation — prevents back button abuse

**Teacher Dashboard (`/teacher/dashboard/`)**
- Quiz list with: title, code, active toggle, student count, action buttons
- Buttons per quiz: Questions | Import | Results | Monitor | Export
- Create New Quiz at top right

**Live Monitor (`/teacher/quiz/<id>/monitor/`)**
- Auto-refreshing table every 10 seconds
- Columns: Name, Reg Number, Progress, Time Remaining, Suspicion
- Color coding: green = fine, amber = low time, red = critical or high suspicion

### 11.3 Accessibility
- All form inputs have proper `<label>` tags (not just placeholders)
- Color never the only status indicator — icons accompany colors
- Timer uses `aria-live` region for screen readers
- WCAG AA color contrast maintained
- All interactive elements keyboard-navigable

---

## 12. Performance & Rate Limiting

### 12.1 The Problem
A quiz with 200 students all starting at the same time can overwhelm a small DigitalOcean droplet. The heartbeat endpoint alone — 200 students × 1 request/10 seconds = 20 requests/second. Plus answer saves, page loads, and teacher monitoring.

### 12.2 Mitigations

**Django ORM Optimization**
Avoid N+1 queries using `select_related` and `prefetch_related`:
```python
# Bad — N+1 queries
sessions = StudentSession.objects.filter(quiz=quiz)
for s in sessions:
    print(s.quiz.title)  # hits DB each time

# Good — 1 query
sessions = StudentSession.objects.filter(quiz=quiz).select_related('quiz')
```

**Gunicorn Workers**
```
workers = (2 × CPU cores) + 1
```
For a 1 vCPU droplet: 3 workers. Handles ~150–200 concurrent requests comfortably.

**Nginx Static File Serving**
Nginx serves all `/static/` files directly — never reaches Gunicorn. Saves significant load.

**AJAX Heartbeat Interval**
10 seconds per student. Acceptable latency for timer sync without overwhelming the server. For 100 students: ~10 requests/second to the heartbeat endpoint — manageable.

**Rate Limiting (django-ratelimit)**
Applied on all key endpoints — see Section 5.2. Prevents a single malicious user from flooding the server.

**Database Query Count**
- Quiz attempt page: max 3 queries (session, question, previous answer)
- Heartbeat: 1 query (session lookup + time calculation)
- Monitor endpoint: 1 query with `annotate` for suspicion count

**SQLite Limitations**
SQLite handles ~100 concurrent writes before locking issues appear. Acceptable for school-level usage in dev. Migrate to PostgreSQL on DigitalOcean when concurrent users exceed 50 regularly.

---

## 13. Deployment Guide

### 13.1 DigitalOcean Droplet
```
OS:    Ubuntu 22.04 LTS
Size:  Basic — 1 vCPU, 1GB RAM, 25GB SSD ($6/month)
       Covered by $200 student credits for ~33 months
```

### 13.2 Server Setup
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3.11 python3-pip nginx git certbot python3-certbot-nginx -y
```

### 13.3 App Deployment
```bash
git clone https://github.com/<user>/online-quiz-assessment-system.git
cd online-quiz-assessment-system
pip install -r requirements.txt --break-system-packages
```

Create `.env`:
```
SECRET_KEY=your-long-random-secret-key
DEBUG=False
ALLOWED_HOSTS=<your_ip>,<your_domain>
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=/home/ubuntu/online-quiz-assessment-system/db.sqlite3
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
EMAIL_USE_TLS=True
```

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 13.4 Gunicorn systemd Service
```ini
# /etc/systemd/system/quiz.service
[Unit]
Description=Quiz System Gunicorn
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/online-quiz-assessment-system
ExecStart=/home/ubuntu/.local/bin/gunicorn core.wsgi:application \
    --bind 127.0.0.1:8000 \
    --workers 3 \
    --timeout 60 \
    --log-file /var/log/quiz_gunicorn.log
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable quiz
sudo systemctl start quiz
```

### 13.5 Nginx Config (Port 81)
```nginx
# /etc/nginx/sites-available/quiz
server {
    listen 81;
    server_name <your_ip_or_domain>;

    client_max_body_size 10M;

    add_header X-Frame-Options "DENY";
    add_header X-Content-Type-Options "nosniff";
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    location /static/ {
        alias /home/ubuntu/online-quiz-assessment-system/staticfiles/;
        expires 30d;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 60;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/quiz /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 14. Development Roadmap

| Phase | What | Priority |
|---|---|---|
| 1 | Fix attendance system bugs | High |
| 2 | Custom User model, allauth setup, OTP email verification | High |
| 3 | Quiz, QuestionGroup, Question models + migrations | High |
| 4 | Student entry flow — landing, entry form, session creation | High |
| 5 | Quiz attempt page — timer JS, answer saving, AJAX | High |
| 6 | Auto-submit — heartbeat, server time validation | High |
| 7 | Result page — score display, conditional breakdown | High |
| 8 | Anti-cheat — tab switch logging, copy disable, suspicion model | Medium |
| 9 | Teacher — question CRUD, group management | Medium |
| 10 | Bulk Excel import + download sample template | Medium |
| 11 | Live monitoring dashboard (AJAX polling) | Medium |
| 12 | CSV export | Medium |
| 13 | DigitalOcean deployment — Nginx, Gunicorn, SSL | Last |

---

*End of Documentation — v1.0*
*online-quiz-assessment-system*
