from django.utils import timezone


def calculate_time_remaining(session):
    """
    Calculate remaining time for a quiz session.
    Server owns time authority - client timer is display only.
    """
    if session.is_submitted:
        return 0
    
    elapsed = (timezone.now() - session.start_time).total_seconds()
    remaining = session.quiz.quiz_duration - elapsed
    return max(0, int(remaining))


def is_time_expired(session):
    """Check if quiz time has expired"""
    return calculate_time_remaining(session) <= 0
