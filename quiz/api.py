from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db import models
import json
from .models import StudentSession, Answer, Question, SuspiciousEvent, Quiz
from .utils.timer import calculate_time_remaining, is_time_expired


@require_POST
@csrf_exempt
def heartbeat(request):
    """
    Heartbeat endpoint - called every 10 seconds from client
    Returns time remaining and auto-submits if expired
    """
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        
        if not session_id:
            return JsonResponse({'error': 'session_id required'}, status=400)
        
        session = get_object_or_404(StudentSession, id=session_id)
        
        # check if already submitted
        if session.is_submitted:
            return JsonResponse({
                'status': 'submitted',
                'time_remaining': 0,
                'is_expired': True,
                'message': 'Quiz already submitted'
            })
        
        # calculate time remaining
        time_remaining = calculate_time_remaining(session)
        is_expired = time_remaining <= 0
        
        # auto-submit if time expired
        if is_expired and not session.is_submitted:
            session.is_submitted = True
            session.submitted_at = timezone.now()
            session.submitted_via = 'auto_quiz'
            session.save()
            
            return JsonResponse({
                'status': 'auto_submitted',
                'time_remaining': 0,
                'is_expired': True,
                'message': 'Time expired - quiz auto-submitted'
            })
        
        return JsonResponse({
            'status': 'ok',
            'time_remaining': time_remaining,
            'is_expired': is_expired,
            'current_question': session.current_question_index
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_POST
@csrf_exempt
def save_answer(request, session_id):
    """
    Save or update student answer
    Checks correctness and awards marks
    """
    try:
        session = get_object_or_404(StudentSession, id=session_id)
        
        # can't save if already submitted
        if session.is_submitted:
            return JsonResponse({'error': 'Quiz already submitted'}, status=400)
        
        # check time not expired
        if is_time_expired(session):
            return JsonResponse({'error': 'Time expired'}, status=400)
        
        data = json.loads(request.body)
        question_id = data.get('question_id')
        chosen_answer = data.get('chosen_answer')
        time_taken = data.get('time_taken', 0)
        
        if not question_id or not chosen_answer:
            return JsonResponse({'error': 'question_id and chosen_answer required'}, status=400)
        
        question = get_object_or_404(Question, id=question_id, quiz=session.quiz)
        
        # check if answer correct
        is_correct = (chosen_answer == question.correct_answer)
        marks_awarded = question.marks if is_correct else 0
        
        # create or update answer
        answer, created = Answer.objects.update_or_create(
            session=session,
            question=question,
            defaults={
                'chosen_answer': chosen_answer,
                'time_taken_seconds': time_taken,
                'is_correct': is_correct,
                'marks_awarded': marks_awarded
            }
        )
        
        # recalculate total score
        session.total_score = session.answers.aggregate(
            total=models.Sum('marks_awarded')
        )['total'] or 0
        session.save()
        
        return JsonResponse({
            'status': 'saved',
            'is_correct': is_correct,
            'marks_awarded': marks_awarded,
            'created': created,
            'total_score': session.total_score
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_POST
@csrf_exempt
def log_suspicion(request, session_id):
    """
    Log suspicious activity (anti-cheat)
    """
    try:
        session = get_object_or_404(StudentSession, id=session_id)
        
        data = json.loads(request.body)
        event_type = data.get('event_type')
        question_index = data.get('question_index', session.current_question_index)
        details = data.get('details', '')
        
        if not event_type:
            return JsonResponse({'error': 'event_type required'}, status=400)
        
        # create suspicious event record
        event = SuspiciousEvent.objects.create(
            session=session,
            event_type=event_type,
            question_index=question_index,
            details=details
        )
        
        # count total suspicious events for this session
        total_events = session.suspicious_events.count()
        
        return JsonResponse({
            'status': 'logged',
            'event_id': event.id,
            'total_suspicions': total_events,
            'timestamp': event.timestamp.isoformat()
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def live_sessions(request, quiz_id):
    """
    Get all active (not submitted) sessions for a quiz
    Used for teacher live monitoring
    """
    try:
        quiz = get_object_or_404(Quiz, id=quiz_id)
        
        # get active sessions
        sessions = StudentSession.objects.filter(
            quiz=quiz,
            is_submitted=False
        ).select_related('quiz')
        
        sessions_data = []
        for session in sessions:
            # calculate progress
            total_questions = session.quiz.questions.count()
            answered_questions = session.answers.count()
            progress = (answered_questions / total_questions * 100) if total_questions > 0 else 0
            
            # get suspicion count
            suspicion_count = session.suspicious_events.count()
            
            sessions_data.append({
                'session_id': session.id,
                'student_name': session.full_name,
                'reg_number': session.reg_number,
                'email': session.email,
                'start_time': session.start_time.isoformat(),
                'time_remaining': calculate_time_remaining(session),
                'progress': round(progress, 1),
                'answered': answered_questions,
                'total_questions': total_questions,
                'current_score': session.total_score,
                'suspicion_count': suspicion_count,
                'current_question_index': session.current_question_index
            })
        
        return JsonResponse({
            'status': 'ok',
            'quiz_code': quiz.quiz_code,
            'quiz_title': quiz.title,
            'active_sessions': len(sessions_data),
            'sessions': sessions_data
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_questions(request, session_id):
    """
    Load all questions for a quiz session
    Returns questions WITHOUT correct answers (security)
    """
    try:
        session = get_object_or_404(StudentSession, id=session_id)
        
        # check if already submitted
        if session.is_submitted:
            return JsonResponse({'error': 'Quiz already submitted'}, status=400)
        
        import random as _random

        # use randomized order stored at quiz start
        order_key = f'q_order_{session.id}'
        question_ids = request.session.get(order_key)

        if question_ids:
            questions_map = {q.id: q for q in session.quiz.questions.filter(id__in=question_ids)}
            questions = [questions_map[qid] for qid in question_ids if qid in questions_map]
        else:
            questions = list(session.quiz.questions.order_by('order'))

        def get_options(question):
            if question.question_type == 'true_false':
                return [
                    {'key': 'option_a', 'label': 'A)', 'text': question.option_a or 'True'},
                    {'key': 'option_b', 'label': 'B)', 'text': question.option_b or 'False'},
                ]
            choices = [(k, getattr(question, k)) for k in ['option_a','option_b','option_c','option_d']
                       if getattr(question, k)]
            if question.quiz.randomize_choices:
                _random.seed(f"{session.id}{question.id}")
                _random.shuffle(choices)
                _random.seed()
            return [{'key': k, 'label': chr(65+i)+')', 'text': v} for i,(k,v) in enumerate(choices)]

        # prefetch existing answers
        existing = {a.question_id: a.chosen_answer for a in session.answers.all()}

        questions_data = []
        for idx, question in enumerate(questions):
            questions_data.append({
                'id': question.id,
                'index': idx,
                'text': question.question_text,
                'type': question.question_type,
                'marks': question.marks,
                'options': get_options(question),
                'chosen_answer': existing.get(question.id)
            })
        
        return JsonResponse({
            'status': 'ok',
            'session_id': session.id,
            'quiz_title': session.quiz.title,
            'time_remaining': calculate_time_remaining(session),
            'questions': questions_data,
            'total_questions': len(questions_data)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)