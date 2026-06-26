import csv
from django.http import HttpResponse


def export_quiz_results(quiz):
    """Export quiz results to CSV"""
    sessions = quiz.sessions.filter(is_submitted=True)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{quiz.quiz_code}_results.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Registration Number', 'Full Name', 'Email', 'Total Score', 
                     'Max Score', 'Percentage', 'Pass/Fail', 'Submitted At', 'Submission Type'])
    
    for session in sessions:
        writer.writerow([
            session.reg_number,
            session.full_name,
            session.email,
            session.total_score,
            session.max_possible_score,
            f"{session.percentage_score}%",
            'Pass' if session.is_passed else 'Fail',
            session.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if session.submitted_at else '',
            session.get_submitted_via_display() if session.submitted_via else ''
        ])
    
    return response
