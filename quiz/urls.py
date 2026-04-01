from django.urls import path
from . import views, api

app_name = 'quiz'

urlpatterns = [
    # Landing and student quiz access
    path('', views.landing, name='landing'),
    path('<str:quiz_code>/', views.quiz_entry, name='quiz_entry'),
    path('<str:quiz_code>/start/', views.start_quiz, name='start_quiz'),
    path('session/<int:session_id>/attempt/', views.quiz_attempt, name='quiz_attempt'),
    path('session/<int:session_id>/submit/', views.submit_quiz, name='submit_quiz'),
    path('session/<int:session_id>/result/', views.quiz_result, name='quiz_result'),
    
    # Teacher dashboard and quiz management
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/quiz/create/', views.quiz_create, name='quiz_create'),
    path('teacher/quiz/<int:quiz_id>/edit/', views.quiz_edit, name='quiz_edit'),
    path('teacher/quiz/<int:quiz_id>/delete/', views.quiz_delete, name='quiz_delete'),
    path('teacher/quiz/<int:quiz_id>/toggle-active/', views.toggle_quiz_active, name='toggle_quiz_active'),
    
    # Question group management
    path('teacher/quiz/<int:quiz_id>/groups/', views.manage_groups, name='manage_groups'),
    path('teacher/quiz/<int:quiz_id>/group/create/', views.group_create, name='group_create'),
    path('teacher/group/<int:group_id>/edit/', views.group_edit, name='group_edit'),
    path('teacher/group/<int:group_id>/delete/', views.group_delete, name='group_delete'),
    
    # Question management
    path('teacher/quiz/<int:quiz_id>/questions/', views.manage_questions, name='manage_questions'),
    path('teacher/quiz/<int:quiz_id>/question/create/', views.question_create, name='question_create'),
    path('teacher/question/<int:question_id>/edit/', views.question_edit, name='question_edit'),
    path('teacher/question/<int:question_id>/delete/', views.question_delete, name='question_delete'),
    
    # Excel import/export
    path('teacher/quiz/<int:quiz_id>/import/', views.import_questions, name='import_questions'),
    path('teacher/quiz/<int:quiz_id>/export-template/', views.export_template, name='export_template'),
    path('teacher/quiz/<int:quiz_id>/export-results/', views.export_results, name='export_results'),
    
    # Live monitoring
    path('teacher/quiz/<int:quiz_id>/monitor/', views.live_monitor, name='live_monitor'),
    path('teacher/quiz/<int:quiz_id>/results/', views.quiz_results, name='quiz_results'),
    
    # AJAX API endpoints
    path('api/heartbeat/', api.heartbeat, name='api_heartbeat'),
    path('api/session/<int:session_id>/save-answer/', api.save_answer, name='api_save_answer'),
    path('api/session/<int:session_id>/log-suspicion/', api.log_suspicion, name='api_log_suspicion'),
    path('api/session/<int:session_id>/questions/', api.get_questions, name='api_get_questions'),
    path('api/quiz/<int:quiz_id>/live-sessions/', api.live_sessions, name='api_live_sessions'),
]
