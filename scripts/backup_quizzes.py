#!/usr/bin/env python
"""
Simple backup script for quizzes (useful for Pro users).
"""
import json
from quiz.models import Quiz

def backup_all_quizzes():
    data = []
    for q in Quiz.objects.all():
        data.append({
            "code": q.quiz_code,
            "title": q.title,
            "questions": q.questions.count(),
        })
    with open("quizzes_backup.json", "w") as f:
        json.dump(data, f, indent=2)
    print("Backup written to quizzes_backup.json")

if __name__ == "__main__":
    backup_all_quizzes()
