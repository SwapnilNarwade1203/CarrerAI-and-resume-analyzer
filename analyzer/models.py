from django.db import models
from django.contrib.auth.models import User


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class JobRole(models.Model):
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    skills = models.ManyToManyField(Skill, related_name='job_roles', blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    target_job_role = models.ForeignKey(JobRole, null=True, blank=True, on_delete=models.SET_NULL)
    career_goals = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    file = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    extracted_text = models.TextField(blank=True)
    extracted_skills = models.JSONField(default=list)
    experience_present = models.BooleanField(default=False)
    projects_present = models.BooleanField(default=False)
    score = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.user.username} - {self.uploaded_at.strftime('%Y-%m-%d')}"

    class Meta:
        ordering = ['-uploaded_at']


class ResumeAnalysis(models.Model):
    resume = models.OneToOneField(Resume, on_delete=models.CASCADE, related_name='analysis')
    ats_score = models.FloatField(default=0.0)
    education_score = models.FloatField(default=0.0)
    project_score = models.FloatField(default=0.0)
    experience_score = models.FloatField(default=0.0)
    certification_score = models.FloatField(default=0.0)
    skill_match_score = models.FloatField(default=0.0)
    education_feedback = models.TextField(blank=True)
    project_feedback = models.TextField(blank=True)
    experience_feedback = models.TextField(blank=True)
    certification_feedback = models.TextField(blank=True)
    skill_feedback = models.TextField(blank=True)
    general_feedback = models.TextField(blank=True)

    def __str__(self):
        return f"Analysis for {self.resume}"


class AptitudeTopic(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class AptitudeQuestion(models.Model):
    topic = models.ForeignKey(AptitudeTopic, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_option = models.CharField(max_length=1, choices=[('A','A'),('B','B'),('C','C'),('D','D')])
    explanation = models.TextField(blank=True)

    def __str__(self):
        return self.question[:80]


class SkillProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skill_progress')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='progress')
    level = models.IntegerField(default=0)  # 0-100
    last_updated = models.DateTimeField(auto_now=True)
    roadmap = models.JSONField(default=list)
    daily_questions = models.JSONField(default=list)
    test_score = models.FloatField(default=0.0)
    priority = models.IntegerField(default=0)
    completed_steps = models.JSONField(default=list)

    class Meta:
        unique_together = ('user', 'skill')
        ordering = ['-level']

    def __str__(self):
        return f"{self.user.username} - {self.skill.name}: {self.level}%"


class SkillTestQuestion(models.Model):
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='test_questions')
    question = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_option = models.CharField(max_length=1, choices=[('A','A'),('B','B'),('C','C'),('D','D')])
    explanation = models.TextField(blank=True)

    def __str__(self):
        return f"[{self.skill.name}] {self.question[:60]}"


class InterviewQuestion(models.Model):
    CATEGORY_CHOICES = [
        ('technical', 'Technical'),
        ('behavioral', 'Behavioral'),
        ('situational', 'Situational'),
    ]
    job_role = models.ForeignKey(JobRole, on_delete=models.CASCADE, related_name='interview_questions')
    question = models.TextField()
    answer_hints = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='technical')

    def __str__(self):
        return f"[{self.job_role.title}] {self.question[:60]}"


class CompanyQuestion(models.Model):
    company_name = models.CharField(max_length=200)
    job_role = models.CharField(max_length=200)
    question = models.TextField()
    answer_hints = models.TextField(blank=True)
    category = models.CharField(max_length=50, default='technical')
    submitted_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.company_name}] {self.question[:60]}"

    class Meta:
        ordering = ['-created_at']


class Achievement(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=100, default='fa-trophy')
    condition_type = models.CharField(max_length=50, default='skill_level')
    condition_value = models.IntegerField(default=100)

    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'achievement')

    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"


class MockInterviewSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mock_sessions')
    job_role = models.ForeignKey(JobRole, null=True, blank=True, on_delete=models.SET_NULL)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    transcript = models.JSONField(default=list)
    score = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.user.username} - Mock Interview {self.started_at.strftime('%Y-%m-%d')}"

    class Meta:
        ordering = ['-started_at']


class UserProject(models.Model):
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=300)
    description = models.TextField()
    github_repo_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    roadmap = models.JSONField(default=list)
    skills_used = models.ManyToManyField(Skill, related_name='projects', blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    class Meta:
        ordering = ['-created_at']


class JobMarketInsight(models.Model):
    job_role = models.OneToOneField(JobRole, on_delete=models.CASCADE, related_name='market_insight')
    average_salary_min = models.IntegerField(default=0)
    average_salary_max = models.IntegerField(default=0)
    demand_score = models.IntegerField(default=50)  # 0-100
    top_employers = models.JSONField(default=list)
    last_updated = models.DateField(auto_now=True)

    def __str__(self):
        return f"Market Insight - {self.job_role.title}"


class CommunicationTip(models.Model):
    title = models.CharField(max_length=300)
    content = models.TextField()
    video_url = models.URLField(blank=True)

    def __str__(self):
        return self.title
