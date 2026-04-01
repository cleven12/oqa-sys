from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.db import IntegrityError
from .models import Quiz, Question, QuestionGroup, StudentSession, Answer, SuspiciousEvent
from .forms import StudentEntryForm


def landing(request):
    return render(request, 'quiz/landing.html')


def quiz_entry(request, quiz_code):
    """Display quiz entry form with quiz details"""
    quiz = get_object_or_404(Quiz, quiz_code=quiz_code.upper(), is_active=True)
    
    # calculate quiz stats
    quiz.total_questions = quiz.questions.count()
    quiz.total_marks = sum(q.marks for q in quiz.questions.all())
    quiz.passing_percentage = quiz.pass_mark
    
    return render(request, 'quiz/student/entry.html', {'quiz': quiz})


def start_quiz(request, quiz_code):
    """Create student session and start quiz"""
    if request.method != 'POST':
        return redirect('quiz:quiz_entry', quiz_code=quiz_code)
    
    quiz = get_object_or_404(Quiz, quiz_code=quiz_code.upper(), is_active=True)
    
    # get form data
    full_name = request.POST.get('full_name', '').strip()
    reg_number = request.POST.get('reg_number', '').strip()
    email = request.POST.get('email', '').strip()
    accept_rules = request.POST.get('accept_rules')
    
    # validate
    if not all([full_name, reg_number, email, accept_rules]):
        messages.error(request, 'All fields are required and you must accept the rules')
        return redirect('quiz:quiz_entry', quiz_code=quiz_code)
    
    try:
        # calculate max posible score
        max_score = sum(q.marks for q in quiz.questions.all())
        
        # create student sesion
        session = StudentSession.objects.create(
            quiz=quiz,
            full_name=full_name,
            reg_number=reg_number,
            email=email,
            max_possible_score=max_score,
            current_question_index=0
        )
        
        return redirect('quiz:quiz_attempt', session_id=session.id)
        
    except IntegrityError:
        # student already took this quiz
        messages.error(request, f'Registration number {reg_number} has already taken this quiz. You cannot retake it.')
        return redirect('quiz:quiz_entry', quiz_code=quiz_code)
    except Exception as e:
        messages.error(request, f'Error starting quiz: {str(e)}')
        return redirect('quiz:quiz_entry', quiz_code=quiz_code)


def quiz_attempt(request, session_id):
    """Quiz attempt page - main quiz interface"""
    session = get_object_or_404(StudentSession, id=session_id)
    
    # check if already submited
    if session.is_submitted:
        return redirect('quiz:quiz_result', session_id=session_id)
    
    # check if time expired
    from .utils.timer import is_time_expired
    if is_time_expired(session):
        # auto-submit
        session.is_submitted = True
        session.submitted_at = timezone.now()
        session.submitted_via = 'auto_quiz'
        session.save()
        return redirect('quiz:quiz_result', session_id=session_id)
    
    return render(request, 'quiz/student/attempt.html', {'session': session})


def submit_quiz(request, session_id):
    """Manual quiz submission"""
    if request.method != 'POST':
        return redirect('quiz:quiz_attempt', session_id=session_id)
    
    session = get_object_or_404(StudentSession, id=session_id)
    
    if not session.is_submitted:
        session.is_submitted = True
        session.submitted_at = timezone.now()
        session.submitted_via = 'manual'
        session.save()
    
    return redirect('quiz:quiz_result', session_id=session_id)


def quiz_result(request, session_id):
    """Quiz result page"""
    session = get_object_or_404(StudentSession, id=session_id)
    
    # must be submited to see results
    if not session.is_submitted:
        return redirect('quiz:quiz_attempt', session_id=session_id)
    
    return render(request, 'quiz/student/result.html', {'session': session})


@login_required
def teacher_dashboard(request):
    quizzes = Quiz.objects.filter(created_by=request.user)
    return render(request, 'quiz/teacher/dashboard.html', {'quizzes': quizzes})


@login_required
def quiz_create(request):
    return render(request, 'quiz/teacher/quiz_form.html')


@login_required
def quiz_edit(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    return render(request, 'quiz/teacher/quiz_form.html', {'quiz': quiz})


@login_required
def quiz_delete(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    quiz.delete()
    return redirect('quiz:teacher_dashboard')


@login_required
def toggle_quiz_active(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    quiz.is_active = not quiz.is_active
    quiz.save()
    return redirect('quiz:teacher_dashboard')


@login_required
def manage_groups(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    groups = quiz.groups.all()
    return render(request, 'quiz/teacher/group_form.html', {'quiz': quiz, 'groups': groups})


@login_required
def group_create(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    return render(request, 'quiz/teacher/group_form.html', {'quiz': quiz})


@login_required
def group_edit(request, group_id):
    group = get_object_or_404(QuestionGroup, id=group_id)
    return render(request, 'quiz/teacher/group_form.html', {'group': group})


@login_required
def group_delete(request, group_id):
    group = get_object_or_404(QuestionGroup, id=group_id)
    quiz_id = group.quiz.id
    group.delete()
    return redirect('quiz:manage_groups', quiz_id=quiz_id)


@login_required
def manage_questions(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    questions = quiz.questions.all()
    return render(request, 'quiz/teacher/questions.html', {'quiz': quiz, 'questions': questions})


@login_required
def question_create(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    return render(request, 'quiz/teacher/questions.html', {'quiz': quiz})


@login_required
def question_edit(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    return render(request, 'quiz/teacher/questions.html', {'question': question})


@login_required
def question_delete(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    quiz_id = question.quiz.id
    question.delete()
    return redirect('quiz:manage_questions', quiz_id=quiz_id)


@login_required
def import_questions(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    return render(request, 'quiz/teacher/import.html', {'quiz': quiz})


@login_required
def export_template(request, quiz_id):
    return HttpResponse('Excel template')


@login_required
def export_results(request, quiz_id):
    return HttpResponse('CSV results')


@login_required
def live_monitor(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    return render(request, 'quiz/teacher/monitor.html', {'quiz': quiz})


@login_required
def quiz_results(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    sessions = quiz.sessions.filter(is_submitted=True)
    return render(request, 'quiz/teacher/results.html', {'quiz': quiz, 'sessions': sessions})

