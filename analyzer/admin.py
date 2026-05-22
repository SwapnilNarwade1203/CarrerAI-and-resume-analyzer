from django.contrib import admin
from .models import (
    Skill, JobRole, UserProfile, Resume, ResumeAnalysis,
    SkillProgress, SkillTestQuestion, InterviewQuestion, CompanyQuestion,
    AptitudeTopic, AptitudeQuestion, Achievement, UserAchievement,
    MockInterviewSession, UserProject, JobMarketInsight, CommunicationTip
)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(JobRole)
class JobRoleAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']
    filter_horizontal = ['skills']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'target_job_role']
    search_fields = ['user__username']


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ['user', 'uploaded_at', 'score', 'experience_present', 'projects_present']
    list_filter = ['experience_present', 'projects_present']
    search_fields = ['user__username']


@admin.register(ResumeAnalysis)
class ResumeAnalysisAdmin(admin.ModelAdmin):
    list_display = ['resume', 'ats_score', 'skill_match_score', 'project_score', 'experience_score']


@admin.register(SkillProgress)
class SkillProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'skill', 'level', 'test_score', 'last_updated']
    list_filter = ['skill']
    search_fields = ['user__username', 'skill__name']


@admin.register(SkillTestQuestion)
class SkillTestQuestionAdmin(admin.ModelAdmin):
    list_display = ['skill', 'question', 'correct_option']
    list_filter = ['skill']
    search_fields = ['question']


@admin.register(InterviewQuestion)
class InterviewQuestionAdmin(admin.ModelAdmin):
    list_display = ['job_role', 'category', 'question']
    list_filter = ['job_role', 'category']
    search_fields = ['question']


@admin.register(CompanyQuestion)
class CompanyQuestionAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'job_role', 'category', 'submitted_by', 'created_at']
    list_filter = ['company_name', 'category']
    search_fields = ['company_name', 'question']


@admin.register(AptitudeTopic)
class AptitudeTopicAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(AptitudeQuestion)
class AptitudeQuestionAdmin(admin.ModelAdmin):
    list_display = ['topic', 'question', 'correct_option']
    list_filter = ['topic']


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['name', 'condition_type', 'condition_value', 'icon']


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ['user', 'achievement', 'earned_at']


@admin.register(MockInterviewSession)
class MockInterviewSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'job_role', 'started_at', 'ended_at', 'score']


@admin.register(UserProject)
class UserProjectAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'status', 'created_at', 'github_repo_url']
    list_filter = ['status']


@admin.register(JobMarketInsight)
class JobMarketInsightAdmin(admin.ModelAdmin):
    list_display = ['job_role', 'average_salary_min', 'average_salary_max', 'demand_score']


@admin.register(CommunicationTip)
class CommunicationTipAdmin(admin.ModelAdmin):
    list_display = ['title']
