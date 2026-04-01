# API Documentation

## Overview
This document describes the AJAX API endpoints used by the Online Quiz Assessment System.

All endpoints return JSON responses.

---

## Endpoints

### 1. Get Questions
Load all questions for a quiz session (without correct answers for security).

**URL:** `GET /api/session/<session_id>/questions/`

**Response:**
```json
{
  "status": "ok",
  "session_id": 1,
  "quiz_title": "Python Basics Test",
  "time_remaining": 1622,
  "total_questions": 3,
  "questions": [
    {
      "id": 1,
      "index": 0,
      "text": "What is the output of print(2 ** 3)?",
      "type": "mcq",
      "marks": 2,
      "options": [
        {"key": "option_a", "label": "A)", "text": "6"},
        {"key": "option_b", "label": "B)", "text": "8"},
        {"key": "option_c", "label": "C)", "text": "9"},
        {"key": "option_d", "label": "D)", "text": "16"}
      ],
      "chosen_answer": null
    }
  ]
}
```

---

### 2. Heartbeat
Check session status and sync time with server. Called every 10 seconds.

**URL:** `POST /api/heartbeat/`

**Request:**
```json
{
  "session_id": 1
}
```

**Response:**
```json
{
  "status": "ok",
  "time_remaining": 1614,
  "is_expired": false,
  "current_question": 0
}
```

**Auto-Submit Response (when time expires):**
```json
{
  "status": "auto_submitted",
  "time_remaining": 0,
  "is_expired": true,
  "message": "Time expired - quiz auto-submitted"
}
```

---

### 3. Save Answer
Save or update a student's answer to a question.

**URL:** `POST /api/session/<session_id>/save-answer/`

**Request:**
```json
{
  "question_id": 1,
  "chosen_answer": "option_b",
  "time_taken": 15
}
```

**Response:**
```json
{
  "status": "saved",
  "is_correct": true,
  "marks_awarded": 2,
  "created": true,
  "total_score": 2
}
```

**Note:** `created` is `true` if this is a new answer, `false` if updating existing.

---

### 4. Log Suspicious Activity
Record anti-cheat events (tab switch, copy attempt, etc.).

**URL:** `POST /api/session/<session_id>/log-suspicion/`

**Request:**
```json
{
  "event_type": "tab_switch",
  "question_index": 0,
  "details": "User switched to another tab"
}
```

**Valid event types:**
- `tab_switch`
- `window_blur`
- `shortcut_blocked`
- `copy_attempt`
- `paste_attempt`

**Response:**
```json
{
  "status": "logged",
  "event_id": 1,
  "total_suspicions": 1,
  "timestamp": "2026-04-01T21:01:22.443569+00:00"
}
```

---

### 5. Live Sessions (Teacher Monitoring)
Get all active (not submitted) sessions for a quiz.

**URL:** `GET /api/quiz/<quiz_id>/live-sessions/`

**Response:**
```json
{
  "status": "ok",
  "quiz_code": "QZ-ETE8NP",
  "quiz_title": "Python Basics Test",
  "active_sessions": 1,
  "sessions": [
    {
      "session_id": 1,
      "student_name": "Test Student",
      "reg_number": "TEST001",
      "email": "test@example.com",
      "start_time": "2026-04-01T20:58:05.844336+00:00",
      "time_remaining": 1597,
      "progress": 33.3,
      "answered": 1,
      "total_questions": 3,
      "current_score": 2,
      "suspicion_count": 1,
      "current_question_index": 0
    }
  ]
}
```

---

## Error Responses

All endpoints return error responses in this format:

```json
{
  "error": "Error message here"
}
```

Common HTTP status codes:
- `200` - Success
- `400` - Bad Request (missing parameters, invalid data)
- `404` - Not Found (session/quiz doesn't exist)
- `500` - Server Error

---

## Security Notes

1. **CSRF Protection:** Currently disabled with `@csrf_exempt` for easier testing. Should be enabled in production.

2. **Correct Answers:** Never sent to client. Server validates answers.

3. **Time Authority:** Server owns time calculations. Client timer is display-only.

4. **Session Validation:** All endpoints validate session exists and is not submitted.

5. **Anti-Cheat:** Suspicious events are logged but don't automatically invalidate quiz (teacher review required).

---

## Testing Examples

### Using curl:

```bash
# Get questions
curl http://localhost:8001/api/session/1/questions/

# Heartbeat
curl -X POST http://localhost:8001/api/heartbeat/ \
  -H "Content-Type: application/json" \
  -d '{"session_id": 1}'

# Save answer
curl -X POST http://localhost:8001/api/session/1/save-answer/ \
  -H "Content-Type: application/json" \
  -d '{"question_id": 1, "chosen_answer": "option_b", "time_taken": 15}'

# Log suspicion
curl -X POST http://localhost:8001/api/session/1/log-suspicion/ \
  -H "Content-Type: application/json" \
  -d '{"event_type": "tab_switch", "question_index": 0}'

# Live sessions
curl http://localhost:8001/api/quiz/2/live-sessions/
```

### Using JavaScript (from frontend):

```javascript
// Load questions
const response = await fetch(`/api/session/${sessionId}/questions/`);
const data = await response.json();

// Heartbeat
fetch('/api/heartbeat/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ session_id: sessionId })
});

// Save answer
fetch(`/api/session/${sessionId}/save-answer/`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question_id: questionId,
    chosen_answer: 'option_b',
    time_taken: 15
  })
});
```
