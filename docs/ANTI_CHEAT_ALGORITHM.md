# 🛡️ Anti-Cheat System

**Simple. Effective. Transparent.**

The OQA anti-cheat system raises the cost of cheating without being overly intrusive. It logs suspicious behavior for teachers to review later.

---

## ✨ Core Features

- **Tab Switch & Window Blur Detection** — Logs when students leave the quiz tab or window.
- **Copy / Paste / Right-Click Blocking** — Prevents easy content copying.
- **Keyboard Shortcut Blocking** — Blocks common dev tools and copy shortcuts (Ctrl+C, F12, etc.).
- **Time-per-Question Logging** — Records how long each answer took.
- **Suspicion Scoring** — Teachers see a clean / low / high suspicion indicator per student.

---

## 🔄 How the Anti-Cheat Algorithm Works

### High-Level Flow

```mermaid
flowchart TD
    A[Student starts quiz] --> B[JS listeners attached]
    B --> C{Event triggered?}
    C -->|Yes| D[Log event + question index]
    D --> E[Send to /api/.../log-suspicion/]
    E --> F[Server saves SuspiciousEvent]
    F --> G[Teacher sees count in Results]
    C -->|No| H[Continue quiz]
    H --> C
```

### Detailed Algorithm (Client + Server)

1. **Client Side (JavaScript in `attempt.html` + `anticheat.js`)**
   - On page load → attach event listeners:
     - `visibilitychange` → if `document.hidden` → log `tab_switch`
     - `blur` → log `window_blur`
     - `copy` / `paste` / `cut` → preventDefault + log event
     - `contextmenu` → prevent right click
     - `keydown` → block Ctrl+C, Ctrl+V, F12, etc.
   - Each detection calls:
     ```js
     logSuspicion(eventType, currentQuestionIndex)
     ```
   - Sends POST with `{ event_type, question_index, details? }`

2. **Server Side (`api.py` → `log_suspicion`)**
   - Validate session is active
   - Create `SuspiciousEvent` record
   - Return total suspicion count for that session

3. **Scoring Logic (Displayed in Results & Monitor)**
   ```python
   count = session.suspicious_events.count()

   if count == 0:
       "Clean ✅"
   elif count <= 3:
       "Minor ⚠️"
   else:
       "High 🔴"
   ```

4. **Additional Signals**
   - Extremely fast answers (time_taken_seconds very low)
   - Auto-submit due to timer
   - High number of events during difficult questions

---

## 🕵️ Suspicion Scoring Table

| Events | Level     | Color in UI     | Action for Teacher          |
|--------|-----------|-----------------|-----------------------------|
| 0      | Clean     | Green           | No action needed            |
| 1-3    | Minor     | Yellow          | Review results              |
| 4+     | High      | Red             | Investigate + possible flag |

---

## 📐 Architecture Diagram

```mermaid
flowchart LR
    subgraph Student Browser
        JS[Vanilla JS + Alpine]
        Listeners[Anti-cheat Listeners]
    end

    subgraph Server
        API[DRF / Django Views]
        Model[SuspiciousEvent Model]
        DB[(Database)]
    end

    subgraph Teacher
        Dashboard[Live Monitor]
        Results[Results Page]
    end

    JS -->|POST /log-suspicion| API
    Listeners --> JS
    API --> Model
    Model --> DB
    DB --> Results
    DB --> Dashboard
```

---

## 🔁 Sequence: Anti-Cheat Event

```mermaid
sequenceDiagram
    participant S as Student
    participant J as JavaScript
    participant API as Server API
    participant DB as Database
    participant T as Teacher

    S->>J: Leaves tab / copies text
    J->>API: POST log-suspicion {event, question_index}
    API->>DB: Save SuspiciousEvent
    API-->>J: {status: logged, total: X}
    T->>Results: View student results
    Results->>DB: Query events count
    DB-->>Results: count + events
    Results-->>T: Shows suspicion badge
```

---

## ✅ Why This Design?

- **Client is display-only** — all validation on server
- **No false accusations** — events are logged, not auto-penalized
- **Lightweight** — pure vanilla JS, no extra libraries
- **Teacher-controlled** — final decision always with the human

---

**Note:** No system is 100% cheat-proof. This system makes casual cheating much harder and gives teachers evidence when needed.

For the full Pro version, we offer enhanced detection (keystroke analysis, webcam flags, etc.) — email **clevengodsontech@gmail.com**
```