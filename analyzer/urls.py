from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard & Resume
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload-resume/', views.upload_resume, name='upload_resume'),
    path('analysis/<int:pk>/', views.analysis_detail, name='analysis_detail'),
    path('resume/suggestions/', views.resume_suggestions, name='resume_suggestions'),
    path('compare-resumes/', views.compare_resumes, name='compare_resumes'),
    path('resume/<int:pk>/delete/', views.delete_resume, name='delete_resume'),

    # Resume Builder / Studio
    path('resume-studio/', views.resume_studio, name='resume_studio'),
    path('create-resume/', views.create_resume, name='create_resume'),
    path('create-resume/form/', views.create_resume_form, name='create_resume_form'),

    # Skill Tracker
    path('skills/', views.skill_tracker_list, name='skill_tracker_list'),
    path('skills/<int:skill_id>/', views.skill_tracker_detail, name='skill_tracker_detail'),
    path('skills/<int:skill_id>/test/', views.skill_test, name='skill_test'),
    path('skills/<int:skill_id>/test/submit/', views.submit_skill_test, name='submit_skill_test'),
    path('skills/<int:skill_id>/certificate/', views.generate_certificate, name='generate_certificate'),

    # Interview & Aptitude
    path('interview-prep/', views.interview_prep, name='interview_prep'),
    path('aptitude/', views.aptitude_prep, name='aptitude_prep'),
    path('aptitude/<int:topic_id>/', views.aptitude_topic, name='aptitude_topic'),

    # Mock Interview
    path('mock-interview/', views.mock_interview, name='mock_interview'),

    # Projects
    path('projects/', views.create_project, name='create_project'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),

    # Social & Community
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('achievements/', views.achievements, name='achievements'),
    path('company-questions/', views.company_questions, name='company_questions'),



    # Admin
    path('admin-analytics/', views.admin_analytics, name='admin_analytics'),
]
