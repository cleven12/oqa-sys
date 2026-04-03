from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.db import IntegrityError
from .models import Quiz, Question, QuestionGroup, StudentSession, Answer, SuspiciousEvent
from .forms import StudentEntryForm, QuizForm, QuestionGroupForm, QuestionForm


def landing(request):
    return render(request, 'quiz/landing.html')


def quiz_entry(request, quiz_code):
    """Display quiz entry form with quiz details"""
    quiz = get_object_or_404(Quiz, quiz_code=quiz_code.upper(), is_active=True)
    
    # Quiz now has total_questions, total_marks, passing_percentage as properties
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
        # calculate max possible score
        max_score = sum(q.marks for q in quiz.questions.all())
        
        # create student session
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
    
    # check if already submitted
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
    
    # must be submitted to see results
    if not session.is_submitted:
        return redirect('quiz:quiz_attempt', session_id=session_id)
    
    # Only show answer breakdown for auto-submitted quizzes
    answers_breakdown = None
    if session.submitted_via == 'auto_quiz':
        answers_breakdown = session.answers.select_related('question').all()
    
    return render(request, 'quiz/student/result.html', {
        'session': session,
        'answers_breakdown': answers_breakdown
    })


@login_required
def teacher_dashboard(request):
    quizzes = Quiz.objects.filter(created_by=request.user).prefetch_related('sessions')
    
    # Add computed fields for each quiz
    for quiz in quizzes:
        quiz.student_count = quiz.sessions.filter(is_submitted=True).count()
        quiz.active_count = quiz.sessions.filter(is_submitted=False).count()
    
    return render(request, 'quiz/teacher/dashboard.html', {'quizzes': quizzes})


@login_required
def quiz_create(request):
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.created_by = request.user
            # quiz_duration is already in seconds (converted by form)
            quiz.save()
            messages.success(request, f'Quiz "{quiz.title}" created successfully! Code: {quiz.quiz_code}')
            return redirect('quiz:manage_groups', quiz_id=quiz.id)
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = QuizForm()
    
    return render(request, 'quiz/teacher/quiz_form.html', {'form': form})


@login_required
def quiz_edit(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            quiz = form.save(commit=False)
            # quiz_duration is already in seconds (converted by form)
            quiz.save()
            messages.success(request, f'Quiz "{quiz.title}" updated successfully!')
            return redirect('quiz:teacher_dashboard')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        # Need to initialize form with minutes for display
        initial_data = {
            'title': quiz.title,
            'description': quiz.description,
            'timer_mode': quiz.timer_mode,
            'quiz_duration': quiz.quiz_duration // 60,  # Convert seconds to minutes
            'pass_mark': quiz.pass_mark,
            'randomize_questions': quiz.randomize_questions,
            'randomize_choices': quiz.randomize_choices,
        }
        form = QuizForm(initial=initial_data, instance=quiz)
    
    return render(request, 'quiz/teacher/quiz_form.html', {'form': form, 'quiz': quiz})


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
    groups = quiz.groups.all().order_by('order')
    
    if request.method == 'POST':
        form = QuestionGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.quiz = quiz
            group.save()
            messages.success(request, f'Group "{group.name}" added successfully!')
            return redirect('quiz:manage_groups', quiz_id=quiz.id)
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = QuestionGroupForm()
    
    return render(request, 'quiz/teacher/group_form.html', {
        'quiz': quiz,
        'groups': groups,
        'form': form
    })


@login_required
def group_create(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    return redirect('quiz:manage_groups', quiz_id=quiz_id)


@login_required
def group_edit(request, group_id):
    group = get_object_or_404(QuestionGroup, id=group_id, quiz__created_by=request.user)
    
    if request.method == 'POST':
        form = QuestionGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, f'Group "{group.name}" updated successfully!')
            return redirect('quiz:manage_groups', quiz_id=group.quiz.id)
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = QuestionGroupForm(instance=group)
    
    return render(request, 'quiz/teacher/group_form.html', {
        'group': group,
        'form': form,
        'quiz': group.quiz
    })


@login_required
def group_delete(request, group_id):
    group = get_object_or_404(QuestionGroup, id=group_id, quiz__created_by=request.user)
    quiz_id = group.quiz.id
    group.delete()
    return redirect('quiz:manage_groups', quiz_id=quiz_id)


@login_required
def manage_questions(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    questions = quiz.questions.select_related('group').all().order_by('order')
    
    if request.method == 'POST':
        form = QuestionForm(request.POST, quiz=quiz)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            messages.success(request, 'Question added successfully!')
            return redirect('quiz:manage_questions', quiz_id=quiz.id)
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = QuestionForm(quiz=quiz)
    
    return render(request, 'quiz/teacher/questions.html', {
        'quiz': quiz,
        'questions': questions,
        'form': form
    })


@login_required
def question_create(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    return redirect('quiz:manage_questions', quiz_id=quiz_id)


@login_required
def question_edit(request, question_id):
    question = get_object_or_404(Question, id=question_id, quiz__created_by=request.user)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question, quiz=question.quiz)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question updated successfully!')
            return redirect('quiz:manage_questions', quiz_id=question.quiz.id)
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = QuestionForm(instance=question, quiz=question.quiz)
    
    return render(request, 'quiz/teacher/questions.html', {
        'question': question,
        'form': form,
        'quiz': question.quiz
    })


@login_required
def question_delete(request, question_id):
    question = get_object_or_404(Question, id=question_id, quiz__created_by=request.user)
    quiz_id = question.quiz.id
    question.delete()
    return redirect('quiz:manage_questions', quiz_id=quiz_id)


@login_required
def import_questions(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    
    if request.method == 'POST' and request.FILES.get('excel_file'):
        try:
            from .utils.import_questions import import_questions_from_file
            excel_file = request.FILES['excel_file']
            
            result = import_questions_from_file(excel_file, quiz)
            
            if result['status'] == 'success':
                messages.success(request, f"Successfully imported {result['imported']} questions!")
                # Show warnings if any
                if result.get('errors'):
                    warnings = [e for e in result['errors'] if 'not found - question imported without group' in e]
                    if warnings:
                        messages.warning(request, f"{len(warnings)} questions imported without groups (groups don't exist)")
                return redirect('quiz:manage_questions', quiz_id=quiz.id)
            else:
                messages.error(request, f"Import failed: {result.get('message', 'Unknown error')}")
        except Exception as e:
            messages.error(request, f'Error importing file: {str(e)}')
    
    return render(request, 'quiz/teacher/import.html', {'quiz': quiz})


@login_required
def export_template(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    
    try:
        from .utils.export import generate_import_template
        response = generate_import_template()
        return response
    except Exception as e:
        messages.error(request, f'Error generating template: {str(e)}')
        return redirect('quiz:import_questions', quiz_id=quiz_id)


@login_required
def export_results(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    
    try:
        from .utils.export import export_quiz_results
        response = export_quiz_results(quiz)
        return response
    except Exception as e:
        messages.error(request, f'Error exporting results: {str(e)}')
        return redirect('quiz:quiz_results', quiz_id=quiz_id)


@login_required
def live_monitor(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    return render(request, 'quiz/teacher/monitor.html', {'quiz': quiz})


@login_required
def quiz_results(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    sessions = quiz.sessions.filter(is_submitted=True)
    return render(request, 'quiz/teacher/results.html', {'quiz': quiz, 'sessions': sessions})

