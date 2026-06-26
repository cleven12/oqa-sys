#!/usr/bin/env python
"""
Generate sample data for OQA System.
Useful for development, demos, and testing.
Run: python scripts/generate_sample_data.py
"""
import os
import sys
import django
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.models import User
from quiz.models import Quiz, QuestionGroup, Question, StudentSession, Answer

def create_sample_quiz():
    # Create or get teacher
    teacher, _ = User.objects.get_or_create(
        username="demo_teacher",
        defaults={
            "email": "teacher@demo.local",
            "first_name": "Demo",
            "last_name": "Teacher",
        }
    )
    if not teacher.has_usable_password():
        teacher.set_password("demo1234")
        teacher.save()

    quiz = Quiz.objects.create(
        title="Sample Math Assessment",
        description="A demo quiz showing stratified questions and timers.",
        quiz_duration=20 * 60,
        pass_mark=60,
        timer_mode="quiz",
        randomize_questions=True,
        randomize_choices=True,
        is_active=True,
        created_by=teacher,
    )

    # Groups
    easy = QuestionGroup.objects.create(quiz=quiz, name="Easy", marks_per_question=1, pick_count=5, order=1)
    medium = QuestionGroup.objects.create(quiz=quiz, name="Medium", marks_per_question=2, pick_count=3, order=2)

    # Easy questions
    for i in range(8):
        Question.objects.create(
            quiz=quiz,
            group=easy,
            question_text=f"What is {i+2} + {i+1}?",
            question_type="mcq",
            option_a=str(i+2+i+1-1),
            option_b=str(i+2+i+1),
            option_c=str(i+2+i+1+1),
            option_d=str(i+2+i+1+2),
            correct_answer="option_b",
            order=i,
        )

    # Medium
    for i in range(5):
        Question.objects.create(
            quiz=quiz,
            group=medium,
            question_text=f"Calculate {i*3 + 5} × 2",
            question_type="mcq",
            option_a=str((i*3+5)*2 - 2),
            option_b=str((i*3+5)*2),
            option_c=str((i*3+5)*2 + 2),
            option_d=str((i*3+5)*2 + 4),
            correct_answer="option_b",
            order=10+i,
        )

    print(f"Created sample quiz: {quiz.quiz_code} - {quiz.title}")
    print("Teacher login: demo_teacher / demo1234")
    return quiz

if __name__ == "__main__":
    create_sample_quiz()
    print("Sample data generated successfully!")
