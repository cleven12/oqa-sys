from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from .models import StudentSession, Answer, Question, SuspiciousEvent


@require_POST
def heartbeat(request):
    return JsonResponse({'status': 'ok'})


@require_POST
def save_answer(request, session_id):
    session = get_object_or_404(StudentSession, id=session_id)
    return JsonResponse({'status': 'saved'})


@require_POST
def log_suspicion(request, session_id):
    session = get_object_or_404(StudentSession, id=session_id)
    return JsonResponse({'status': 'logged'})


def live_sessions(request, quiz_id):
    return JsonResponse({'sessions': []})
