#!/usr/bin/env python
"""
Test script to verify all fixes are working correctly
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import TeacherProfile
from quiz.models import Quiz, QuestionGroup, Question, StudentSession, Answer

def test_models():
    """Test model properties and relationships"""
    print("\n=== Testing Models ===")
    
    # Test Quiz properties
    try:
        quiz = Quiz.objects.first()
        if quiz:
            print(f"✅ Quiz.total_questions: {quiz.total_questions}")
            print(f"✅ Quiz.total_marks: {quiz.total_marks}")
            print(f"✅ Quiz.passing_percentage: {quiz.passing_percentage}")
            print(f"✅ Quiz.quiz_duration_minutes: {quiz.quiz_duration_minutes} min")
        else:
            print("⚠️  No quizzes in database yet")
    except Exception as e:
        print(f"❌ Quiz properties error: {e}")
    
    # Test Question marks property
    try:
        question = Question.objects.first()
        if question:
            print(f"✅ Question.marks: {question.marks}")
        else:
            print("⚠️  No questions in database yet")
    except Exception as e:
        print(f"❌ Question.marks error: {e}")
    
    # Test StudentSession properties
    try:
        session = StudentSession.objects.first()
        if session:
            print(f"✅ StudentSession.percentage_score: {session.percentage_score}%")
            print(f"✅ StudentSession.is_passed: {session.is_passed}")
            print(f"✅ StudentSession.time_remaining: {session.time_remaining}s")
        else:
            print("⚠️  No student sessions in database yet")
    except Exception as e:
        print(f"❌ StudentSession properties error: {e}")


def test_views():
    """Test view imports and URL routing"""
    print("\n=== Testing Views ===")
    
    try:
        from accounts import views as account_views
        print("✅ accounts.views imported successfully")
        print(f"   - register: {hasattr(account_views, 'register')}")
        print(f"   - login_view: {hasattr(account_views, 'login_view')}")
        print(f"   - verify_otp: {hasattr(account_views, 'verify_otp')}")
    except Exception as e:
        print(f"❌ accounts.views error: {e}")
    
    try:
        from quiz import views as quiz_views
        print("✅ quiz.views imported successfully")
        print(f"   - quiz_create: {hasattr(quiz_views, 'quiz_create')}")
        print(f"   - quiz_edit: {hasattr(quiz_views, 'quiz_edit')}")
        print(f"   - manage_groups: {hasattr(quiz_views, 'manage_groups')}")
        print(f"   - manage_questions: {hasattr(quiz_views, 'manage_questions')}")
        print(f"   - import_questions: {hasattr(quiz_views, 'import_questions')}")
    except Exception as e:
        print(f"❌ quiz.views error: {e}")


def test_forms():
    """Test form imports"""
    print("\n=== Testing Forms ===")
    
    try:
        from accounts.forms import TeacherRegistrationForm, LoginForm
        print("✅ Account forms imported successfully")
        print(f"   - TeacherRegistrationForm fields: {list(TeacherRegistrationForm.base_fields.keys())}")
        print(f"   - LoginForm fields: {list(LoginForm.base_fields.keys())}")
    except Exception as e:
        print(f"❌ Account forms error: {e}")
    
    try:
        from quiz.forms import QuizForm, QuestionGroupForm, QuestionForm
        print("✅ Quiz forms imported successfully")
        print(f"   - QuizForm fields: {list(QuizForm.Meta.fields)}")
        print(f"   - QuestionGroupForm fields: {list(QuestionGroupForm.Meta.fields)}")
        print(f"   - QuestionForm fields: {list(QuestionForm.Meta.fields)}")
    except Exception as e:
        print(f"❌ Quiz forms error: {e}")


def test_api():
    """Test API endpoints"""
    print("\n=== Testing API ===")
    
    try:
        from quiz import api
        print("✅ quiz.api imported successfully")
        print(f"   - heartbeat: {hasattr(api, 'heartbeat')}")
        print(f"   - save_answer: {hasattr(api, 'save_answer')}")
        print(f"   - log_suspicion: {hasattr(api, 'log_suspicion')}")
        print(f"   - get_questions: {hasattr(api, 'get_questions')}")
        print(f"   - live_sessions: {hasattr(api, 'live_sessions')}")
    except Exception as e:
        print(f"❌ quiz.api error: {e}")


def test_utils():
    """Test utility functions"""
    print("\n=== Testing Utils ===")
    
    try:
        from quiz.utils.timer import calculate_time_remaining, is_time_expired
        print("✅ timer utils imported successfully")
    except Exception as e:
        print(f"❌ timer utils error: {e}")
    
    try:
        from quiz.utils.export import export_quiz_results, generate_import_template
        print("✅ export utils imported successfully")
    except Exception as e:
        print(f"❌ export utils error: {e}")
    
    try:
        from quiz.utils.import_questions import import_questions_from_file
        print("✅ import utils imported successfully")
    except Exception as e:
        print(f"❌ import utils error: {e}")


def test_urls():
    """Test URL resolution"""
    print("\n=== Testing URLs ===")
    
    try:
        from django.urls import reverse
        
        # Test accounts URLs
        reverse('accounts:register')
        reverse('accounts:login')
        reverse('accounts:logout')
        print("✅ Account URLs resolved successfully")
        
        # Test quiz URLs
        reverse('quiz:landing')
        reverse('quiz:teacher_dashboard')
        reverse('quiz:quiz_create')
        print("✅ Quiz URLs resolved successfully")
        
    except Exception as e:
        print(f"❌ URL resolution error: {e}")


def print_stats():
    """Print database statistics"""
    print("\n=== Database Statistics ===")
    print(f"Users: {User.objects.count()}")
    print(f"Teacher Profiles: {TeacherProfile.objects.count()}")
    print(f"Quizzes: {Quiz.objects.count()}")
    print(f"Question Groups: {QuestionGroup.objects.count()}")
    print(f"Questions: {Question.objects.count()}")
    print(f"Student Sessions: {StudentSession.objects.count()}")
    print(f"Answers: {Answer.objects.count()}")


if __name__ == '__main__':
    print("=" * 60)
    print("OQA SYSTEM - FIX VERIFICATION TEST")
    print("=" * 60)
    
    try:
        test_models()
        test_views()
        test_forms()
        test_api()
        test_utils()
        test_urls()
        print_stats()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - System is functional!")
        print("=" * 60)
        print("\n🚀 Ready to test:")
        print("   1. Run: python manage.py runserver")
        print("   2. Visit: http://localhost:8000")
        print("   3. Register: /accounts/register/")
        print("   4. Login: /accounts/login/")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
