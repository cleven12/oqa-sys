from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from .models import Quiz, Question, QuestionGroup, StudentSession, Answer, SuspiciousEvent


def landing(request):
    return render(request, 'quiz/landing.html')


def quiz_entry(request, quiz_code):
    quiz = get_object_or_404(Quiz, quiz_code=quiz_code, is_active=True)
    return render(request, 'quiz/student/entry.html', {'quiz': quiz})


def start_quiz(request, quiz_code):
    return redirect('quiz:landing')


def quiz_attempt(request, session_id):
    session = get_object_or_404(StudentSession, id=session_id)
    return render(request, 'quiz/student/attempt.html', {'session': session})


def submit_quiz(request, session_id):
    return redirect('quiz:quiz_result', session_id=session_id)


def quiz_result(request, session_id):
    session = get_object_or_404(StudentSession, id=session_id)
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

