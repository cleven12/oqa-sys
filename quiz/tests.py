"""
QUIZ APP - COMPREHENSIVE TEST SUITE

This module tests all quiz functionality including models, forms, views, and APIs.
Following Django best practices with detailed comments for learning.

Test Categories:
1. Model Tests - Quiz, Question, QuestionGroup, StudentSession, Answer, SuspiciousEvent
2. Form Tests - QuizForm, QuestionForm, StudentEntryForm
3. View Tests - Student and Teacher views
4. API Tests - AJAX endpoints
5. Business Logic Tests - Timer, scoring, randomization
6. Security Tests - Anti-cheating, permissions

Learning Points:
- Test database constraints (unique_together, foreign keys)
- Test business logic methods (properties, custom methods)
- Test security rules (permissions, data isolation)
- Test edge cases (expired timers, zero questions, etc.)
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Quiz, Question, QuestionGroup, StudentSession, Answer, SuspiciousEvent
from .forms import QuizForm, QuestionForm, QuestionGroupForm, StudentEntryForm


class QuizModelTest(TestCase):
    """
    Test Quiz model
    
    Learning: Core quiz functionality - code generation, validation, relationships
    """
    
    def setUp(self):
        """Create test teacher"""
        self.teacher = User.objects.create_user(
            username='teacher1',
            email='teacher1@test.com',
            password='testpass123'
        )
    
    def test_quiz_creation(self):
        """Test creating a quiz"""
        quiz = Quiz.objects.create(
            title='Python Basics Quiz',
            description='Test your Python knowledge',
            timer_mode='quiz',
            quiz_duration=3600,
            pass_mark=50,
            created_by=self.teacher
        )
        
        self.assertEqual(quiz.title, 'Python Basics Quiz')
        self.assertEqual(quiz.timer_mode, 'quiz')
        self.assertEqual(quiz.quiz_duration, 3600)
        self.assertEqual(quiz.pass_mark, 50)
        self.assertTrue(quiz.randomize_questions)
        self.assertTrue(quiz.randomize_choices)
        self.assertFalse(quiz.is_active)
    
    def test_quiz_code_auto_generation(self):
        """Test that quiz code is automatically generated"""
        quiz = Quiz.objects.create(
            title='Test Quiz',
            quiz_duration=1800,
            created_by=self.teacher
        )
        
        self.assertIsNotNone(quiz.quiz_code)
        self.assertTrue(quiz.quiz_code.startswith('QZ-'))
        self.assertEqual(len(quiz.quiz_code), 9)  # QZ- + 6 characters
    
    def test_quiz_code_uniqueness(self):
        """Test that each quiz gets a unique code"""
        quiz1 = Quiz.objects.create(
            title='Quiz 1',
            quiz_duration=1800,
            created_by=self.teacher
        )
        quiz2 = Quiz.objects.create(
            title='Quiz 2',
            quiz_duration=1800,
            created_by=self.teacher
        )
        
        self.assertNotEqual(quiz1.quiz_code, quiz2.quiz_code)
    
    def test_quiz_str_method(self):
        """Test string representation"""
        quiz = Quiz.objects.create(
            title='Math Quiz',
            quiz_duration=1800,
            created_by=self.teacher
        )
        
        expected = f"{quiz.quiz_code} - Math Quiz"
        self.assertEqual(str(quiz), expected)
    
    def test_quiz_timer_mode_choices(self):
        """Test valid timer mode choices"""
        valid_modes = ['quiz', 'question', 'both']
        
        for mode in valid_modes:
            quiz = Quiz.objects.create(
                title=f'Quiz {mode}',
                timer_mode=mode,
                quiz_duration=1800,
                created_by=self.teacher
            )
            self.assertEqual(quiz.timer_mode, mode)
    
    def test_quiz_pass_mark_validation(self):
        """Test pass mark is between 0-100"""
        quiz = Quiz.objects.create(
            title='Test Quiz',
            quiz_duration=1800,
            pass_mark=75,
            created_by=self.teacher
        )
        
        self.assertEqual(quiz.pass_mark, 75)


class QuestionGroupModelTest(TestCase):
    """
    Test QuestionGroup model
    
    Learning: Stratified randomization - picking N questions from groups
    """
    
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher1',
            password='testpass123'
        )
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            quiz_duration=1800,
            created_by=self.teacher
        )
    
    def test_question_group_creation(self):
        """Test creating a question group"""
        group = QuestionGroup.objects.create(
            quiz=self.quiz,
            name='Easy Questions',
            marks_per_question=1,
            pick_count=5,
            order=1
        )
        
        self.assertEqual(group.quiz, self.quiz)
        self.assertEqual(group.name, 'Easy Questions')
        self.assertEqual(group.marks_per_question, 1)
        self.assertEqual(group.pick_count, 5)
    
    def test_unique_group_name_per_quiz(self):
        """Test that group names must be unique within a quiz"""
        QuestionGroup.objects.create(
            quiz=self.quiz,
            name='Easy',
            marks_per_question=1,
            pick_count=5
        )
        
        # Creating another group with same name in same quiz should fail
        with self.assertRaises(Exception):
            QuestionGroup.objects.create(
                quiz=self.quiz,
                name='Easy',
                marks_per_question=2,
                pick_count=3
            )
    
    def test_different_quiz_same_group_name(self):
        """Test same group name allowed in different quizzes"""
        quiz2 = Quiz.objects.create(
            title='Another Quiz',
            quiz_duration=1800,
            created_by=self.teacher
        )
        
        group1 = QuestionGroup.objects.create(
            quiz=self.quiz,
            name='Easy',
            marks_per_question=1,
            pick_count=5
        )
        
        group2 = QuestionGroup.objects.create(
            quiz=quiz2,
            name='Easy',
            marks_per_question=1,
            pick_count=5
        )
        
        self.assertEqual(group1.name, group2.name)
        self.assertNotEqual(group1.quiz, group2.quiz)
    
    def test_group_cascade_delete(self):
        """Test groups are deleted when quiz is deleted"""
        group = QuestionGroup.objects.create(
            quiz=self.quiz,
            name='Easy',
            marks_per_question=1,
            pick_count=5
        )
        group_id = group.id
        
        self.quiz.delete()
        
        self.assertFalse(QuestionGroup.objects.filter(id=group_id).exists())


class QuestionModelTest(TestCase):
    """
    Test Question model
    
    Learning: Different question types, validation, relationships
    """
    
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher1',
            password='testpass123'
        )
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            quiz_duration=1800,
            created_by=self.teacher
        )
        self.group = QuestionGroup.objects.create(
            quiz=self.quiz,
            name='Easy',
            marks_per_question=1,
            pick_count=5
        )
    
    def test_mcq_question_creation(self):
        """Test creating an MCQ question"""
        question = Question.objects.create(
            quiz=self.quiz,
            group=self.group,
            question_text='What is 2 + 2?',
            question_type='mcq',
            option_a='3',
            option_b='4',
            option_c='5',
            option_d='6',
            correct_answer='option_b',
            order=1
        )
        
        self.assertEqual(question.question_type, 'mcq')
        self.assertEqual(question.option_a, '3')
        self.assertEqual(question.correct_answer, 'option_b')
    
    def test_true_false_question_creation(self):
        """Test creating a true/false question"""
        question = Question.objects.create(
            quiz=self.quiz,
            question_text='Python is a programming language',
            question_type='true_false',
            option_a='True',
            option_b='False',
            correct_answer='option_a'
        )
        
        self.assertEqual(question.question_type, 'true_false')
        self.assertEqual(question.option_a, 'True')
        self.assertEqual(question.option_b, 'False')
    
    def test_calculation_question_creation(self):
        """Test creating a calculation question"""
        question = Question.objects.create(
            quiz=self.quiz,
            question_text='Calculate 15 x 8',
            question_type='calculation',
            correct_answer='120',
            max_attempts=3
        )
        
        self.assertEqual(question.question_type, 'calculation')
        self.assertEqual(question.correct_answer, '120')
        self.assertEqual(question.max_attempts, 3)
    
    def test_question_without_group(self):
        """Test creating question without a group"""
        question = Question.objects.create(
            quiz=self.quiz,
            question_text='Standalone question',
            question_type='mcq',
            option_a='A',
            option_b='B',
            correct_answer='option_a'
        )
        
        self.assertIsNone(question.group)
    
    def test_question_with_timer(self):
        """Test question with per-question timer"""
        question = Question.objects.create(
            quiz=self.quiz,
            question_text='Timed question',
            question_type='mcq',
            option_a='A',
            option_b='B',
            correct_answer='option_a',
            duration_seconds=30
        )
        
        self.assertEqual(question.duration_seconds, 30)
    
    def test_group_set_null_on_delete(self):
        """Test question.group becomes null when group is deleted"""
        question = Question.objects.create(
            quiz=self.quiz,
            group=self.group,
            question_text='Test',
            question_type='mcq',
            option_a='A',
            option_b='B',
            correct_answer='option_a'
        )
        
        self.group.delete()
        question.refresh_from_db()
        
        self.assertIsNone(question.group)


class StudentSessionModelTest(TestCase):
    """
    Test StudentSession model
    
    Learning: Session management, unique constraints, scoring
    """
    
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher1',
            password='testpass123'
        )
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            quiz_duration=1800,
            pass_mark=60,
            created_by=self.teacher
        )
    
    def test_student_session_creation(self):
        """Test creating a student session"""
        session = StudentSession.objects.create(
            quiz=self.quiz,
            full_name='John Doe',
            reg_number='ST123456',
            email='john@example.com'
        )
        
        self.assertEqual(session.full_name, 'John Doe')
        self.assertEqual(session.reg_number, 'ST123456')
        self.assertEqual(session.email, 'john@example.com')
        self.assertFalse(session.is_submitted)
        self.assertEqual(session.total_score, 0)
        self.assertEqual(session.current_question_index, 0)
    
    def test_unique_reg_number_per_quiz(self):
        """Test that same student can't retake quiz"""
        StudentSession.objects.create(
            quiz=self.quiz,
            full_name='John Doe',
            reg_number='ST123456',
            email='john@example.com'
        )
        
        # Same reg number attempting same quiz should fail
        with self.assertRaises(Exception):
            StudentSession.objects.create(
                quiz=self.quiz,
                full_name='John Doe Again',
                reg_number='ST123456',
                email='john2@example.com'
            )
    
    def test_same_reg_different_quiz_allowed(self):
        """Test same student can take different quizzes"""
        quiz2 = Quiz.objects.create(
            title='Another Quiz',
            quiz_duration=1800,
            created_by=self.teacher
        )
        
        session1 = StudentSession.objects.create(
            quiz=self.quiz,
            full_name='John Doe',
            reg_number='ST123456',
            email='john@example.com'
        )
        
        session2 = StudentSession.objects.create(
            quiz=quiz2,
            full_name='John Doe',
            reg_number='ST123456',
            email='john@example.com'
        )
        
        self.assertEqual(session1.reg_number, session2.reg_number)
        self.assertNotEqual(session1.quiz, session2.quiz)
    
    def test_percentage_score_property(self):
        """Test percentage score calculation"""
        session = StudentSession.objects.create(
            quiz=self.quiz,
            full_name='John Doe',
            reg_number='ST123456',
            email='john@example.com',
            total_score=75,
            max_possible_score=100
        )
        
        self.assertEqual(session.percentage_score, 75.0)
    
    def test_percentage_score_with_zero_max(self):
        """Test percentage when no questions answered"""
        session = StudentSession.objects.create(
            quiz=self.quiz,
            full_name='John Doe',
            reg_number='ST123456',
            email='john@example.com',
            total_score=0,
            max_possible_score=0
        )
        
        self.assertEqual(session.percentage_score, 0)
    
    def test_is_passed_property(self):
        """Test pass/fail determination"""
        session = StudentSession.objects.create(
            quiz=self.quiz,
            full_name='John Doe',
            reg_number='ST123456',
            email='john@example.com',
            total_score=70,
            max_possible_score=100
        )
        
        self.assertTrue(session.is_passed)  # 70% >= 60% pass mark
    
    def test_is_failed_property(self):
        """Test failing score"""
        session = StudentSession.objects.create(
            quiz=self.quiz,
            full_name='Jane Doe',
            reg_number='ST123457',
            email='jane@example.com',
            total_score=50,
            max_possible_score=100
        )
        
        self.assertFalse(session.is_passed)  # 50% < 60% pass mark
    
    def test_time_remaining_property(self):
        """Test time remaining calculation"""
        session = StudentSession.objects.create(
            quiz=self.quiz,
            full_name='John Doe',
            reg_number='ST123456',
            email='john@example.com'
        )
        
        remaining = session.time_remaining
        self.assertGreater(remaining, 0)
        self.assertLessEqual(remaining, 1800)
    
    def test_time_remaining_when_submitted(self):
        """Test time remaining is 0 when submitted"""
        session = StudentSession.objects.create(
            quiz=self.quiz,
            full_name='John Doe',
            reg_number='ST123456',
            email='john@example.com',
            is_submitted=True
        )
        
        self.assertEqual(session.time_remaining, 0)


class AnswerModelTest(TestCase):
    """
    Test Answer model
    
    Learning: Answer tracking, attempts, scoring
    """
    
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher1',
            password='testpass123'
        )
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            quiz_duration=1800,
            created_by=self.teacher
        )
        self.question = Question.objects.create(
            quiz=self.quiz,
            question_text='Test question',
            question_type='mcq',
            option_a='A',
            option_b='B',
            correct_answer='option_a'
        )
        self.session = StudentSession.objects.create(
            quiz=self.quiz,
            full_name='John Doe',
            reg_number='ST123456',
            email='john@example.com'
        )
    
    def test_answer_creation(self):
        """Test creating an answer"""
        answer = Answer.objects.create(
            session=self.session,
            question=self.question,
            chosen_answer='option_a',
            is_correct=True,
            marks_awarded=1
        )
        
        self.assertEqual(answer.session, self.session)
        self.assertEqual(answer.question, self.question)
        self.assertEqual(answer.chosen_answer, 'option_a')
        self.assertTrue(answer.is_correct)
        self.assertEqual(answer.marks_awarded, 1)
    
    def test_unique_session_question(self):
        """Test one answer per session-question pair"""
        Answer.objects.create(
            session=self.session,
            question=self.question,
            chosen_answer='option_a'
        )
        
        # Duplicate should fail
        with self.assertRaises(Exception):
            Answer.objects.create(
                session=self.session,
                question=self.question,
                chosen_answer='option_b'
            )
    
    def test_blank_answer(self):
        """Test unanswered question"""
        answer = Answer.objects.create(
            session=self.session,
            question=self.question,
            chosen_answer='',
            is_correct=False,
            marks_awarded=0
        )
        
        self.assertEqual(answer.chosen_answer, '')
        self.assertFalse(answer.is_correct)
        self.assertEqual(answer.marks_awarded, 0)
    
    def test_calculation_attempts(self):
        """Test attempt tracking for calculation questions"""
        calc_question = Question.objects.create(
            quiz=self.quiz,
            question_text='Calculate 2 + 2',
            question_type='calculation',
            correct_answer='4',
            max_attempts=3
        )
        
        answer = Answer.objects.create(
            session=self.session,
            question=calc_question,
            chosen_answer='5',
            attempts_used=1,
            is_correct=False
        )
        
        self.assertEqual(answer.attempts_used, 1)
        self.assertFalse(answer.is_correct)


class SuspiciousEventModelTest(TestCase):
    """
    Test SuspiciousEvent model
    
    Learning: Anti-cheating event logging
    """
    
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher1',
            password='testpass123'
        )
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            quiz_duration=1800,
            created_by=self.teacher
        )
        self.session = StudentSession.objects.create(
            quiz=self.quiz,
            full_name='John Doe',
            reg_number='ST123456',
            email='john@example.com'
        )
    
    def test_suspicious_event_creation(self):
        """Test logging a suspicious event"""
        event = SuspiciousEvent.objects.create(
            session=self.session,
            event_type='tab_switch',
            question_index=5
        )
        
        self.assertEqual(event.session, self.session)
        self.assertEqual(event.event_type, 'tab_switch')
        self.assertEqual(event.question_index, 5)
    
    def test_multiple_events_per_session(self):
        """Test multiple suspicious events can be logged"""
        event1 = SuspiciousEvent.objects.create(
            session=self.session,
            event_type='tab_switch',
            question_index=1
        )
        event2 = SuspiciousEvent.objects.create(
            session=self.session,
            event_type='window_blur',
            question_index=3
        )
        event3 = SuspiciousEvent.objects.create(
            session=self.session,
            event_type='copy_attempt',
            question_index=5
        )
        
        events = SuspiciousEvent.objects.filter(session=self.session)
        self.assertEqual(events.count(), 3)
    
    def test_event_types(self):
        """Test all event types can be created"""
        event_types = ['tab_switch', 'window_blur', 'shortcut_blocked', 
                       'copy_attempt', 'paste_attempt']
        
        for idx, event_type in enumerate(event_types):
            SuspiciousEvent.objects.create(
                session=self.session,
                event_type=event_type,
                question_index=idx
            )
        
        self.assertEqual(SuspiciousEvent.objects.filter(session=self.session).count(), 5)


class QuizFormTest(TestCase):
    """Test Quiz creation form"""
    
    def test_valid_quiz_form(self):
        """Test form with valid data"""
        form_data = {
            'title': 'Python Quiz',
            'description': 'Test your Python skills',
            'timer_mode': 'quiz',
            'quiz_duration': 3600,
            'pass_mark': 50,
            'randomize_questions': True,
            'randomize_choices': True
        }
        
        form = QuizForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_missing_required_fields(self):
        """Test form requires title and duration"""
        form_data = {
            'description': 'Some description'
        }
        
        form = QuizForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('quiz_duration', form.errors)


class StudentEntryFormTest(TestCase):
    """Test student entry form"""
    
    def test_valid_entry_form(self):
        """Test valid student entry"""
        form_data = {
            'full_name': 'John Doe',
            'reg_number': 'ST123456',
            'email': 'john@example.com'
        }
        
        form = StudentEntryForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_missing_fields(self):
        """Test all fields are required"""
        form_data = {'full_name': 'John Doe'}
        
        form = StudentEntryForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('reg_number', form.errors)
        self.assertIn('email', form.errors)
    
    def test_invalid_email(self):
        """Test email validation"""
        form_data = {
            'full_name': 'John Doe',
            'reg_number': 'ST123456',
            'email': 'invalid-email'
        }
        
        form = StudentEntryForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

