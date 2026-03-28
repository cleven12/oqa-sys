import csv
from io import StringIO
from django.http import HttpResponse
from openpyxl import Workbook


def export_to_csv(quiz, sessions):
    """Export quiz results to CSV"""
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


def generate_template(quiz):
    """Generate Excel template for bulk question import"""
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{quiz.quiz_code}_template.xlsx"'
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Questions"
    
    headers = ['question_text', 'type', 'option_a', 'option_b', 'option_c', 'option_d', 
               'correct_answer', 'duration_seconds', 'max_attempts', 'group_name']
    ws.append(headers)
    
    # Add sample row
    ws.append([
        'What is 2 + 2?',
        'mcq',
        '3',
        '4',
        '5',
        '6',
        'option_b',
        '30',
        '1',
        'Easy'
    ])
    
    wb.save(response)
    return response
