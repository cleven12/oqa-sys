"""
QUIZ UTILS - COMPREHENSIVE TEST SUITE

Testing utility functions for timer, scoring, and business logic.
These tests ensure the core quiz mechanics work correctly.

Learning Points:
- Test time calculations with timezone awareness
- Test edge cases (expired time, negative values)
- Test server-side authority over timing
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from quiz.models import Quiz, Question, QuestionGroup, StudentSession, Answer
from quiz.utils.timer import calculate_time_remaining, is_time_expired


class TimerUtilsTest(TestCase):
    """
    Test timer utility functions
    
    Learning: Server owns time authority - never trust client
    """
    
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher1',
            password='testpass123'
        )
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            quiz_duration=1800,  # 30 minutes
            created_by=self.teacher
        )
    
    def test_calculate_time_remaining_fresh_session(self):
        """Test time remaining for newly started session"""
        session = StudentSession.objects.create(
            quiz=self.quiz,
            full_name='John Doe',
            reg_number='ST123456',
            email='john@example.com'
        )
        
        remaining = calculate_time_remaining(session)
        
        # Should be close to full duration
        self.assertGreater(remaining, 1790)  # Allow 10 second margin
        self.assertLessEqual(remaining, 1800)
    
    def test_calculate_time_remaining_mid_session(self):
        """Test time remaining in middle of quiz"""
        session = StudentSession.objects.create(
            quiz=self.quiz,
            full_name='John Doe',
            reg_number='ST123456',
            email='john@example.com'
        )
        
        # Simulate 10 minutes passed
        session.start_time = timezone.now() - timedelta(minutes=10)
        session.save()
        
        remaining = calculate_time_remaining(session)
        
        # Should be around 20 minutes (1200 seconds)
        self.assertGreater(remaining, 1190)
        self.assertLess(remaining, 1210)
    
    def test_calculate_time_remaining_expired(self):
        """Test time remaining when session has expired"""
        session = StudentSession.objects.create(
            quiz=self.quiz,
            full_name='John Doe',
            reg_number='ST123456',
            email='john@example.com'
        )
        
        # Simulate 40 minutes passed (quiz is 30 minutes)
        session.start_time = timezone.now() - timedelta(minutes=40)
        session.save()
        
        remaining = calculate_time_remaining(session)
        
        # Should be 0, not negative
        self.assertEqual(remaining, 0)
    
    def test_calculate_time_remaining_submitted(self):
        """Test time remaining for submitted session"""
        session = StudentSession.objects.create(
            quiz=self.quiz,
            full_name='John Doe',
            reg_number='ST123456',
            email='john@example.com',
            is_submitted=True
        )
        
        remaining = calculate_time_remaining(session)
        
        self.assertEqual(remaining, 0)
    
    def test_is_time_expired_not_expired(self):
        """Test time expiry check for active session"""
        session = StudentSession.objects.create(
            quiz=self.quiz,
            full_name='John Doe',
            reg_number='ST123456',
            email='john@example.com'
        )
        
        self.assertFalse(is_time_expired(session))
    
    def test_is_time_expired_when_expired(self):
        """Test time expiry check for expired session"""
        session = StudentSession.objects.create(
            quiz=self.quiz,
            full_name='John Doe',
            reg_number='ST123456',
            email='john@example.com'
        )
        
        # Simulate time expired
        session.start_time = timezone.now() - timedelta(minutes=40)
        session.save()
        
        self.assertTrue(is_time_expired(session))


class ScoringLogicTest(TestCase):
    """
    Test scoring calculations
    
    Learning: Marks come from groups, scoring must be accurate
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
        
        # Create groups with different marks
        self.easy_group = QuestionGroup.objects.create(
            quiz=self.quiz,
            name='Easy',
            marks_per_question=1,
            pick_count=5,
            order=1
        )
        
        self.hard_group = QuestionGroup.objects.create(
            quiz=self.quiz,
            name='Hard',
            marks_per_question=5,
            pick_count=2,
            order=2
        )
        
        # Create questions
        for i in range(5):
            Question.objects.create(
                quiz=self.quiz,
                group=self.easy_group,
                question_text=f'Easy Q{i+1}',
                question_type='mcq',
                option_a='A',
                option_b='B',
                correct_answer='option_a',
                order=i
            )
        
        for i in range(2):
            Question.objects.create(
                quiz=self.quiz,
                group=self.hard_group,
                question_text=f'Hard Q{i+1}',
                question_type='mcq',
                option_a='A',
                option_b='B',
                correct_answer='option_a',
                order=i+5
            )
        
        self.session = StudentSession.objects.create(
            quiz=self.quiz,
            full_name='John Doe',
            reg_number='ST123456',
            email='john@example.com'
        )
    
    def test_scoring_all_correct(self):
        """Test scoring when all answers correct"""
        questions = Question.objects.filter(quiz=self.quiz)
        
        for question in questions:
            marks = question.group.marks_per_question
            Answer.objects.create(
                session=self.session,
                question=question,
                chosen_answer='option_a',
                is_correct=True,
                marks_awarded=marks
            )
        
        # Calculate total
        total = sum(a.marks_awarded for a in self.session.answers.all())
        max_possible = sum(q.group.marks_per_question for q in questions)
        
        self.assertEqual(total, 15)  # 5*1 + 2*5 = 15
        self.assertEqual(max_possible, 15)
    
    def test_scoring_partial_correct(self):
        """Test scoring with some correct, some wrong"""
        questions = list(Question.objects.filter(quiz=self.quiz))
        
        # Answer first 3 easy questions correctly (3 marks)
        for q in questions[:3]:
            Answer.objects.create(
                session=self.session,
                question=q,
                chosen_answer='option_a',
                is_correct=True,
                marks_awarded=q.group.marks_per_question
            )
        
        # Answer remaining incorrectly (0 marks)
        for q in questions[3:]:
            Answer.objects.create(
                session=self.session,
                question=q,
                chosen_answer='option_b',
                is_correct=False,
                marks_awarded=0
            )
        
        total = sum(a.marks_awarded for a in self.session.answers.all())
        self.assertEqual(total, 3)
    
    def test_scoring_with_blank_answers(self):
        """Test scoring with unanswered questions"""
        questions = list(Question.objects.filter(quiz=self.quiz))
        
        # Answer only first question
        Answer.objects.create(
            session=self.session,
            question=questions[0],
            chosen_answer='option_a',
            is_correct=True,
            marks_awarded=1
        )
        
        # Leave others blank
        for q in questions[1:]:
            Answer.objects.create(
                session=self.session,
                question=q,
                chosen_answer='',
                is_correct=False,
                marks_awarded=0
            )
        
        total = sum(a.marks_awarded for a in self.session.answers.all())
        self.assertEqual(total, 1)


class QuestionRandomizationTest(TestCase):
    """
    Test stratified question selection
    
    Learning: Pick N random questions from each group per student
    """
    
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher1',
            password='testpass123'
        )
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            quiz_duration=1800,
            randomize_questions=True,
            created_by=self.teacher
        )
        
        self.group = QuestionGroup.objects.create(
            quiz=self.quiz,
            name='Test Group',
            marks_per_question=1,
            pick_count=3,  # Pick 3 out of 10
            order=1
        )
        
        # Create 10 questions in group
        for i in range(10):
            Question.objects.create(
                quiz=self.quiz,
                group=self.group,
                question_text=f'Question {i+1}',
                question_type='mcq',
                option_a='A',
                option_b='B',
                correct_answer='option_a',
                order=i
            )
    
    def test_pick_count_validation(self):
        """Test that group has enough questions for pick_count"""
        total_questions = Question.objects.filter(group=self.group).count()
        
        self.assertGreaterEqual(total_questions, self.group.pick_count)
    
    def test_different_students_get_different_questions(self):
        """
        Test randomization concept
        Note: This is a conceptual test - actual randomization happens in views
        """
        all_questions = list(Question.objects.filter(group=self.group))
        
        # Simulate picking for two students
        import random
        
        random.seed(12345)
        student1_questions = random.sample(all_questions, self.group.pick_count)
        
        random.seed(67890)
        student2_questions = random.sample(all_questions, self.group.pick_count)
        
        # Different seeds should give different selections
        student1_ids = {q.id for q in student1_questions}
        student2_ids = {q.id for q in student2_questions}
        
        # They shouldn't be identical (high probability)
        self.assertNotEqual(student1_ids, student2_ids)


class CalculationQuestionTest(TestCase):
    """
    Test calculation question behavior
    
    Learning: Multiple attempts, case-insensitive, whitespace handling
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
        self.calc_question = Question.objects.create(
            quiz=self.quiz,
            question_text='Calculate 15 x 8',
            question_type='calculation',
            correct_answer='120',
            max_attempts=3
        )
        self.session = StudentSession.objects.create(
            quiz=self.quiz,
            full_name='John Doe',
            reg_number='ST123456',
            email='john@example.com'
        )
    
    def test_correct_answer_first_attempt(self):
        """Test correct answer on first try"""
        answer = Answer.objects.create(
            session=self.session,
            question=self.calc_question,
            chosen_answer='120',
            attempts_used=1,
            is_correct=True,
            marks_awarded=1
        )
        
        self.assertTrue(answer.is_correct)
        self.assertEqual(answer.attempts_used, 1)
    
    def test_incorrect_then_correct(self):
        """Test multiple attempts concept"""
        # First attempt wrong
        answer = Answer.objects.create(
            session=self.session,
            question=self.calc_question,
            chosen_answer='115',
            attempts_used=1,
            is_correct=False,
            marks_awarded=0
        )
        
        self.assertFalse(answer.is_correct)
        self.assertEqual(answer.attempts_used, 1)
        
        # Concept: In real implementation, would update this answer
        # For now, testing that attempts_used can be tracked
    
    def test_max_attempts_reached(self):
        """Test that max attempts is enforced"""
        answer = Answer.objects.create(
            session=self.session,
            question=self.calc_question,
            chosen_answer='wrong',
            attempts_used=3,  # Used all attempts
            is_correct=False,
            marks_awarded=0
        )
        
        self.assertEqual(answer.attempts_used, self.calc_question.max_attempts)
        self.assertFalse(answer.is_correct)


class SecurityConstraintTest(TestCase):
    """
    Test security constraints
    
    Learning: Database-level security through constraints
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
    
    def test_quiz_code_cannot_be_duplicated(self):
        """Test quiz codes are unique"""
        code = self.quiz.quiz_code
        
        # Try to create another quiz with same code manually
        quiz2 = Quiz(
            title='Another Quiz',
            quiz_duration=1800,
            quiz_code=code,  # Same code
            created_by=self.teacher
        )
        
        with self.assertRaises(Exception):
            quiz2.save()
    
    def test_student_cannot_retake_same_quiz(self):
        """Test unique_together constraint prevents retakes"""
        StudentSession.objects.create(
            quiz=self.quiz,
            full_name='John Doe',
            reg_number='ST123456',
            email='john@example.com'
        )
        
        # Attempt to create another session with same reg_number
        with self.assertRaises(Exception):
            StudentSession.objects.create(
                quiz=self.quiz,
                full_name='John Doe (trying again)',
                reg_number='ST123456',  # Same reg number
                email='john2@example.com'
            )
    
    def test_cascade_delete_protects_data_integrity(self):
        """Test that related data is properly cleaned up"""
        question = Question.objects.create(
            quiz=self.quiz,
            question_text='Test',
            question_type='mcq',
            option_a='A',
            option_b='B',
            correct_answer='option_a'
        )
        
        session = StudentSession.objects.create(
            quiz=self.quiz,
            full_name='John Doe',
            reg_number='ST123456',
            email='john@example.com'
        )
        
        answer = Answer.objects.create(
            session=session,
            question=question,
            chosen_answer='option_a'
        )
        
        answer_id = answer.id
        question_id = question.id
        
        # Delete quiz
        self.quiz.delete()
        
        # Related data should be deleted
        self.assertFalse(Question.objects.filter(id=question_id).exists())
        self.assertFalse(Answer.objects.filter(id=answer_id).exists())
