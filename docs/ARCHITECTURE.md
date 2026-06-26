# OQA Architecture & Design

**Simple. Secure. Scalable.**

This document gives a clean visual overview of how OQA System is designed.

---

## High-Level Architecture

```mermaid
flowchart TB
    subgraph "Public / Student Side"
        Landing[Landing Page<br/>Quiz Code Entry]
        Entry[Student Entry Form]
        Attempt[Quiz Attempt UI<br/>Anti-Cheat Active]
    end

    subgraph "Backend (Django)"
        Auth[Accounts App<br/>Simple Auth]
        QuizCore[Quiz App<br/>Models + Views]
        API[API Layer<br/>Heartbeat / Save / Log]
        Selection[Stratified Selection<br/>Algorithm]
    end

    subgraph "Teacher Side"
        Dashboard[Teacher Dashboard]
        Groups[Group + Question Management]
        Monitor[Live Monitor]
        Results[Results + CSV]
    end

    Landing --> Entry --> Attempt
    Attempt --> API
    API --> QuizCore
    QuizCore --> Selection
    Auth -->|Teacher Login| Dashboard
    Dashboard --> Groups & Monitor & Results
```

---

## Quiz Lifecycle (Simplified)

```mermaid
sequenceDiagram
    participant Student
    participant Server
    participant Teacher

    Student->>Server: Enter code + details
    Server->>Server: Create StudentSession + select questions
    loop Every 10s + on answer
        Student->>Server: Heartbeat + Save Answer + Log Suspicion
        Server->>Server: Validate time + score
    end
    Student->>Server: Submit (or auto-submit)
    Server->>Server: Calculate final score
    Student->>Server: View result
    Teacher->>Server: View results + suspicion
```

---

## Anti-Cheat Integration

Anti-cheat is deeply integrated but non-blocking:

- Client detects → Server records → Teacher reviews
- See [ANTI_CHEAT_ALGORITHM.md](ANTI_CHEAT_ALGORITHM.md) for full details and diagrams.

---

## Key Design Principles (Kept Simple)

- **No heavy frontend frameworks** — Vanilla + Alpine + Tailwind CDN
- **Server owns time & scoring** — Client is untrusted
- **Groups enable fairness** — Stratified random selection
- **Events are evidence, not punishment** — Teacher decides
- **Minimal dependencies** — Easy to self-host (or use Pro hosted)

---

**Contact for Pro version or custom architecture work:**  
📧 **clevengodsontech@gmail.com**

---

*Diagrams rendered with Mermaid. Simple by design.*
