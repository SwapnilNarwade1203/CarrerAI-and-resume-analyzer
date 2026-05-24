import json
import random
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Avg, Count
from django.utils import timezone
from django.conf import settings

from .models import (
    Skill, JobRole, UserProfile, Resume, ResumeAnalysis,
    SkillProgress, SkillTestQuestion, InterviewQuestion, CompanyQuestion,
    AptitudeTopic, AptitudeQuestion, Achievement, UserAchievement,
    MockInterviewSession, UserProject, JobMarketInsight, CommunicationTip
)
from .forms import (
    UserRegistrationForm, UserProfileForm, ResumeUploadForm,
    CompanyQuestionForm, ProjectForm, ResumeBuilderForm
)
from .utils import (
    extract_text_from_file, extract_skills, detect_sections,
    calculate_resume_score, get_skill_gap, get_recommendations,
    create_github_repo, analyze_resume_with_ai, get_ai_client_and_model,
    PROJECT_MAP, COURSE_MAP, CERTIFICATION_MAP,
)
from .youtube_api import get_youtube_videos


def _fast_recommendations(missing_skills):
    """
    Instant static recommendations — zero network calls.
    Used on Dashboard and Analysis Detail so those pages never block on AI.
    Full AI recommendations are still available via the /resume/suggestions/ AJAX endpoint.
    """
    if not missing_skills:
        return [], [], []
    projects, courses, certifications = [], [], []
    for skill_name in missing_skills[:8]:
        key = skill_name.lower()
        for p in PROJECT_MAP.get(key, PROJECT_MAP['default'])[:2]:
            projects.append({'skill': skill_name, 'project': p})
        course_list = COURSE_MAP.get(key)
        if course_list:
            for c in course_list[:2]:
                courses.append({'skill': skill_name, **c})
        else:
            courses.append({
                'skill': skill_name,
                'name': f'Learn {skill_name}',
                'platform': 'YouTube',
                'url': f'https://www.youtube.com/results?search_query={skill_name.replace(" ", "+")}+tutorial',
            })
        for cert in CERTIFICATION_MAP.get(key, [])[:1]:
            certifications.append({'skill': skill_name, **cert})
    return projects, courses, certifications



# ─── AUTH VIEWS ───────────────────────────────────────────────────────────────

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    job_roles = JobRole.objects.all()[:6]
    total_skills = Skill.objects.count()
    total_users = Resume.objects.values('user').distinct().count()
    return render(request, 'home.html', {
        'job_roles': job_roles,
        'total_skills': total_skills,
        'total_users': total_users,
    })


def _style_auth_form(form):
    """Inject auth-input class + placeholder into all text/password widgets."""
    placeholders = {
        'username': 'Choose a username',
        'email': 'your@email.com',
        'password': 'Enter password',
        'password1': 'Create a password',
        'password2': 'Repeat password',
    }
    for name, field in form.fields.items():
        attrs = {
            'class': 'form-control auth-input',
            'autocomplete': 'off',
            'autocorrect': 'off',
            'spellcheck': 'false',
        }
        if name in placeholders:
            attrs['placeholder'] = placeholders[name]
        field.widget.attrs.update(attrs)
    return form


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}! Your account has been created.')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': _style_auth_form(form)})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': _style_auth_form(form)})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


# ─── DASHBOARD ────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    resumes = Resume.objects.filter(user=user)
    latest_resume = resumes.first()
    job_roles = JobRole.objects.all()

    # Profile form
    profile_form = UserProfileForm(instance=profile)
    if request.method == 'POST' and 'update_profile' in request.POST:
        profile_form = UserProfileForm(request.POST, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Profile updated!')
            return redirect('dashboard')

    # Skill gap for latest resume vs target role
    missing_skills = []
    matching_skills = []
    projects_rec = []
    courses_rec = []
    certs_rec = []
    skill_history = []
    radar_labels = []
    radar_scores = []

    if latest_resume and profile.target_job_role:
        role = profile.target_job_role
        extracted = latest_resume.extracted_skills or []
        required = list(role.skills.values_list('name', flat=True))
        matching_skills = [s for s in extracted if s in required]
        missing_skills = [s for s in required if s not in extracted]
        projects_rec, courses_rec, certs_rec = _fast_recommendations(missing_skills)

        # Radar chart data
        radar_labels = ['Skills', 'Experience', 'Projects', 'ATS Score', 'Completeness']
        skill_pct = (len(matching_skills) / len(required) * 100) if required else 0
        exp_pct = 100 if latest_resume.experience_present else 20
        proj_pct = 100 if latest_resume.projects_present else 20
        ats_pct = latest_resume.score
        complete_pct = min((len(extracted) / max(len(required), 1)) * 100, 100)
        radar_scores = [round(skill_pct), exp_pct, proj_pct, round(ats_pct), round(complete_pct)]

    # Skill history for chart
    sp_list = SkillProgress.objects.filter(user=user).order_by('-level')[:6]

    # Learning plan: top 5 missing skills
    learning_plan = missing_skills[:5]

    # User's tracked skill progress
    tracked_skills = SkillProgress.objects.filter(user=user)

    # Resume upload form
    upload_form = ResumeUploadForm(initial={'target_job_role': profile.target_job_role})

    # Insights
    market_insight = None
    if profile.target_job_role:
        market_insight = JobMarketInsight.objects.filter(job_role=profile.target_job_role).first()

    return render(request, 'dashboard.html', {
        'profile': profile,
        'profile_form': profile_form,
        'resumes': resumes,
        'latest_resume': latest_resume,
        'job_roles': job_roles,
        'matching_skills': matching_skills,
        'missing_skills': missing_skills,
        'projects_rec': projects_rec[:4],
        'courses_rec': courses_rec[:4],
        'certs_rec': certs_rec[:4],
        'learning_plan': learning_plan,
        'tracked_skills': tracked_skills,
        'radar_labels': json.dumps(radar_labels),
        'radar_scores': json.dumps(radar_scores),
        'upload_form': upload_form,
        'market_insight': market_insight,
        'sp_list': sp_list,
    })


# ─── RESUME UPLOAD ────────────────────────────────────────────────────────────

@login_required
def upload_resume(request):
    if request.method != 'POST':
        return redirect('dashboard')

    form = ResumeUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        messages.error(request, 'Please upload a valid PDF or DOCX file.')
        return redirect('dashboard')

    uploaded_file = request.FILES['resume_file']
    target_role_id = form.cleaned_data.get('target_job_role')

    # Extract text
    text = extract_text_from_file(uploaded_file)
    uploaded_file.seek(0)

    # Determine job role
    job_role = target_role_id
    if not job_role:
        profile = UserProfile.objects.filter(user=request.user).first()
        if profile:
            job_role = profile.target_job_role

    role_title = job_role.title if job_role else ""

    # Try AI analysis if API Key is configured
    api_key = getattr(settings, 'OPENAI_API_KEY', '')
    ai_result = None
    if api_key:
        try:
            ai_result = analyze_resume_with_ai(text, role_title)
        except Exception:
            # Fall back to rule-based analysis
            pass

    if ai_result:
        extracted_raw = ai_result.get('extracted_skills', [])
        found_skills = []
        # Match case-insensitively with Skill objects in db to keep original casing
        db_skills = {s.name.lower(): s.name for s in Skill.objects.all()}
        for s in extracted_raw:
            s_low = s.lower()
            if s_low in db_skills:
                found_skills.append(db_skills[s_low])
            else:
                found_skills.append(s)

        score = ai_result.get('ats_score', 0.0)
        resume = Resume.objects.create(
            user=request.user,
            file=uploaded_file,
            extracted_text=text,
            extracted_skills=found_skills,
            experience_present=ai_result.get('experience_score', 0.0) >= 50.0,
            projects_present=ai_result.get('project_score', 0.0) >= 50.0,
            score=score,
        )

        ResumeAnalysis.objects.create(
            resume=resume,
            ats_score=ai_result.get('ats_score', 0.0),
            education_score=ai_result.get('education_score', 0.0),
            project_score=ai_result.get('project_score', 0.0),
            experience_score=ai_result.get('experience_score', 0.0),
            certification_score=ai_result.get('certification_score', 0.0),
            skill_match_score=ai_result.get('skill_match_score', 0.0),
            education_feedback=ai_result.get('education_feedback', ''),
            project_feedback=ai_result.get('project_feedback', ''),
            experience_feedback=ai_result.get('experience_feedback', ''),
            certification_feedback=ai_result.get('certification_feedback', ''),
            skill_feedback=ai_result.get('skill_feedback', ''),
            general_feedback=ai_result.get('general_feedback', ''),
        )
    else:
        # Fall back to local rule-based analysis
        all_skills = Skill.objects.all()
        found_skills = extract_skills(text, all_skills)
        experience_present, projects_present = detect_sections(text)
        score, skill_match_score = calculate_resume_score(found_skills, job_role, experience_present, projects_present)

        resume = Resume.objects.create(
            user=request.user,
            file=uploaded_file,
            extracted_text=text,
            extracted_skills=found_skills,
            experience_present=experience_present,
            projects_present=projects_present,
            score=score,
        )

        edu_kws = ['education', 'degree', 'bachelor', 'master', 'university', 'college']
        cert_kws = ['certification', 'certified', 'certificate', 'aws', 'coursera', 'udemy']
        edu_score = 100 if any(kw in text.lower() for kw in edu_kws) else 30
        cert_score = 100 if any(kw in text.lower() for kw in cert_kws) else 20
        exp_score = 100 if experience_present else 20
        proj_score = 100 if projects_present else 20
        ats_score = round((skill_match_score + edu_score + exp_score + proj_score + cert_score) / 5, 1)

        ResumeAnalysis.objects.create(
            resume=resume,
            ats_score=ats_score,
            education_score=edu_score,
            project_score=proj_score,
            experience_score=exp_score,
            certification_score=cert_score,
            skill_match_score=skill_match_score,
            education_feedback='Good education section detected.' if edu_score == 100 else 'Add your education details (degree, institution, year).',
            project_feedback='Projects section found.' if proj_score == 100 else 'Add a projects section to showcase your work.',
            experience_feedback='Experience section detected.' if exp_score == 100 else 'Add work experience or internship details.',
            certification_feedback='Certifications mentioned.' if cert_score == 100 else 'Consider adding relevant certifications.',
            skill_feedback=f'Matched {len(found_skills)} skills from your resume.',
            general_feedback=f'Your resume scored {score}/100. Focus on the missing skills to boost your score.',
        )

    # Update user profile job role if provided
    if job_role:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.target_job_role = job_role
        profile.save()

    messages.success(request, f'Resume analyzed! Your score: {score}/100')
    return redirect('analysis_detail', pk=resume.pk)


@login_required
def analysis_detail(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    analysis = getattr(resume, 'analysis', None)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    job_role = profile.target_job_role
    missing_skills = get_skill_gap(resume.extracted_skills, job_role)
    matching_skills = [s for s in resume.extracted_skills if job_role and s in list(job_role.skills.values_list('name', flat=True))]
    projects_rec, courses_rec, certs_rec = _fast_recommendations(missing_skills)

    improvement_tips = []
    if not resume.experience_present:
        improvement_tips.append('Add a detailed work experience / internship section.')
    if not resume.projects_present:
        improvement_tips.append('Include a projects section with GitHub links.')
    if len(missing_skills) > 3:
        improvement_tips.append(f'Learn missing skills: {", ".join(missing_skills[:3])}...')
    if analysis and analysis.education_score < 50:
        improvement_tips.append('Strengthen your education section with degree, institution, and graduation year.')
    if analysis and analysis.certification_score < 50:
        improvement_tips.append('Add relevant certifications to stand out.')

    return render(request, 'analysis_detail.html', {
        'resume': resume,
        'analysis': analysis,
        'matching_skills': matching_skills,
        'missing_skills': missing_skills,
        'projects_rec': projects_rec[:6],
        'courses_rec': courses_rec[:6],
        'certs_rec': certs_rec[:6],
        'improvement_tips': improvement_tips,
        'profile': profile,
    })


# ─── INTERVIEW PREP ──────────────────────────────────────────────────────────

@login_required
def interview_prep(request):
    job_roles = JobRole.objects.all()
    selected_role = None
    questions = []
    company_questions = []
    tips = CommunicationTip.objects.all()

    role_id = request.GET.get('role')
    category = request.GET.get('category', '')

    if role_id:
        selected_role = get_object_or_404(JobRole, pk=role_id)
        questions = InterviewQuestion.objects.filter(job_role=selected_role)
        if category:
            questions = questions.filter(category=category)

        # Company questions: match by role title (CharField), case-insensitive
        cq_qs = CompanyQuestion.objects.filter(job_role__icontains=selected_role.title)
        if category:
            cq_qs = cq_qs.filter(category=category)
        company_questions = list(cq_qs.order_by('company_name', 'category'))

    all_categories = [
        ('technical',     'Technical',     'fa-code',          '#6c63ff'),
        ('behavioral',    'Behavioral',    'fa-comments',      '#10b981'),
        ('situational',   'Situational',   'fa-lightbulb',     '#f59e0b'),
        ('hr',            'HR',            'fa-user-tie',      '#ec4899'),
        ('system_design', 'System Design', 'fa-network-wired', '#ef4444'),
    ]

    return render(request, 'interview_prep.html', {
        'job_roles': job_roles,
        'selected_role': selected_role,
        'questions': questions,
        'company_questions': company_questions,
        'tips': tips,
        'all_categories': all_categories,
        'categories': [('technical', 'Technical'), ('behavioral', 'Behavioral'), ('situational', 'Situational')],
        'selected_category': category,
    })


# ─── SKILL TRACKER ───────────────────────────────────────────────────────────

@login_required
def skill_tracker_list(request):
    all_skills = Skill.objects.all()
    tracked = SkillProgress.objects.filter(user=request.user)
    tracked_ids = set(tracked.values_list('skill_id', flat=True))

    if request.method == 'POST':
        skill_id = request.POST.get('skill_id')
        action = request.POST.get('action')
        if action == 'track' and skill_id:
            skill = get_object_or_404(Skill, pk=skill_id)
            sp, created = SkillProgress.objects.get_or_create(
                user=request.user,
                skill=skill,
                defaults={'level': 0, 'priority': 0}
            )
            if created:
                # Load roadmap from JSON
                try:
                    import os
                    roadmap_path = os.path.join(settings.BASE_DIR, 'roadmaps.json')
                    with open(roadmap_path) as f:
                        roadmaps = json.load(f)
                    steps = roadmaps.get(skill.name, roadmaps.get('default', []))
                    sp.roadmap = steps
                    sp.save()
                except Exception:
                    pass
                messages.success(request, f'Now tracking {skill.name}!')
            return redirect('skill_tracker_list')
        elif action == 'untrack' and skill_id:
            SkillProgress.objects.filter(user=request.user, skill_id=skill_id).delete()
            messages.info(request, 'Skill removed from tracker.')
            return redirect('skill_tracker_list')

    return render(request, 'skill_tracker_list.html', {
        'all_skills': all_skills,
        'tracked': tracked,
        'tracked_ids': tracked_ids,
    })


@login_required
def skill_tracker_detail(request, skill_id):
    skill = get_object_or_404(Skill, pk=skill_id)
    sp, created = SkillProgress.objects.get_or_create(
        user=request.user, skill=skill,
        defaults={'level': 0}
    )

    if request.method == 'POST':
        step_index = request.POST.get('step_index')
        if step_index is not None:
            step_index = int(step_index)
            completed = sp.completed_steps or []
            if step_index not in completed:
                completed.append(step_index)
                sp.completed_steps = completed
                # Update level based on roadmap completion
                total_steps = len(sp.roadmap) if sp.roadmap else 1
                sp.level = min(int(len(completed) / total_steps * 100), 100)
                sp.save()
                messages.success(request, 'Step marked as completed!')
            return redirect('skill_tracker_detail', skill_id=skill_id)

    videos = get_youtube_videos(f'{skill.name} tutorial')
    questions_count = SkillTestQuestion.objects.filter(skill=skill).count()

    return render(request, 'skill_tracker_detail.html', {
        'skill': skill,
        'sp': sp,
        'videos': videos,
        'questions_count': questions_count,
        'practice_links': [
            {'name': 'LeetCode', 'url': f'https://leetcode.com/problemset/?search={skill.name}', 'icon': 'fa-code'},
            {'name': 'HackerRank', 'url': f'https://www.hackerrank.com/domains/{skill.name.lower()}', 'icon': 'fa-terminal'},
            {'name': 'GeeksforGeeks', 'url': f'https://www.geeksforgeeks.org/{skill.name.lower()}/', 'icon': 'fa-book'},
            {'name': 'freeCodeCamp', 'url': f'https://www.freecodecamp.org/learn', 'icon': 'fa-graduation-cap'},
        ],
    })


@login_required
def skill_test(request, skill_id):
    skill = get_object_or_404(Skill, pk=skill_id)
    questions = list(SkillTestQuestion.objects.filter(skill=skill))
    if len(questions) > 10:
        questions = random.sample(questions, 10)

    if not questions:
        messages.warning(request, f'No test questions available for {skill.name} yet.')
        return redirect('skill_tracker_detail', skill_id=skill_id)

    return render(request, 'skill_test.html', {
        'skill': skill,
        'questions': questions,
    })


@login_required
@require_POST
def submit_skill_test(request, skill_id):
    skill = get_object_or_404(Skill, pk=skill_id)
    questions = SkillTestQuestion.objects.filter(skill=skill)

    correct = 0
    total = 0
    results = []

    for q in questions:
        answer = request.POST.get(f'q_{q.pk}')
        if answer:
            total += 1
            is_correct = answer.upper() == q.correct_option.upper()
            if is_correct:
                correct += 1
            results.append({
                'question': q.question,
                'your_answer': answer.upper(),
                'correct_answer': q.correct_option.upper(),
                'is_correct': is_correct,
                'explanation': q.explanation,
                'options': {'A': q.option_a, 'B': q.option_b, 'C': q.option_c, 'D': q.option_d},
            })

    score = round((correct / total * 100) if total > 0 else 0, 1)

    # Update SkillProgress
    sp, _ = SkillProgress.objects.get_or_create(user=request.user, skill=skill)
    if score > sp.test_score:
        sp.test_score = score
    sp.level = max(sp.level, int(score * 0.7))  # test contributes 70% to level
    sp.save()

    return render(request, 'skill_test.html', {
        'skill': skill,
        'questions': SkillTestQuestion.objects.filter(skill=skill),
        'results': results,
        'score': score,
        'correct': correct,
        'total': total,
        'submitted': True,
        'passed': score >= 80,
    })


# ─── APTITUDE ────────────────────────────────────────────────────────────────

@login_required
def aptitude_prep(request):
    topics = AptitudeTopic.objects.annotate(q_count=Count('questions'))
    return render(request, 'aptitude_prep.html', {'topics': topics})


@login_required
def aptitude_topic(request, topic_id):
    topic = get_object_or_404(AptitudeTopic, pk=topic_id)
    questions = list(topic.questions.all())
    if len(questions) > 15:
        questions = random.sample(questions, 15)

    results = None
    score = None
    if request.method == 'POST':
        correct = 0
        total = 0
        results = []
        for q in topic.questions.all():
            answer = request.POST.get(f'q_{q.pk}')
            if answer:
                total += 1
                is_correct = answer.upper() == q.correct_option.upper()
                if is_correct:
                    correct += 1
                results.append({
                    'question': q.question,
                    'your_answer': answer.upper(),
                    'correct_answer': q.correct_option.upper(),
                    'is_correct': is_correct,
                    'explanation': q.explanation,
                })
        score = round((correct / total * 100) if total else 0, 1)

    return render(request, 'aptitude_topic.html', {
        'topic': topic,
        'questions': questions,
        'results': results,
        'score': score,
    })


# ─── MOCK INTERVIEW ──────────────────────────────────────────────────────────

# Generic technical fallback (used only when OpenAI fails)
TECHNICAL_FALLBACK_QUESTIONS = [
    "Explain the difference between a stack and a queue with a real-world use case.",
    "What is the time complexity of QuickSort in the worst case, and how would you avoid it?",
    "Describe how you would design a URL shortener service (system design).",
    "What are SOLID principles? Give an example of the Single Responsibility Principle.",
    "Explain the difference between REST and GraphQL APIs. When would you use each?",
    "How does garbage collection work in a language you know well?",
    "Describe a situation where you had to debug a production issue. What was your process?",
    "What is the CAP theorem and how does it affect distributed database design?",
    "Explain how you would optimize a slow SQL query.",
    "What is the difference between horizontal and vertical scaling?",
]

# Generic HR / behavioral fallback (used only when OpenAI fails)
HR_FALLBACK_QUESTIONS = [
    "Tell me about a time you had a conflict with a team member and how you resolved it.",
    "Describe a situation where you had to meet a very tight deadline. What did you do?",
    "Give me an example of a time you showed leadership without having a formal title.",
    "Tell me about a project that failed. What did you learn from it?",
    "How do you prioritize your work when you have multiple competing deadlines?",
    "Describe a time you received critical feedback. How did you respond?",
    "Tell me about a time you went above and beyond what was expected of you.",
    "How do you handle working with a difficult stakeholder or client?",
    "Describe a time you had to quickly learn a new technology or skill. How did you approach it?",
    "Where do you see yourself in 5 years, and how does this role fit into that plan?",
]


def _get_fallback_questions(interview_type):
    """Return the appropriate hardcoded fallback list based on interview type."""
    if interview_type == 'hr':
        return HR_FALLBACK_QUESTIONS
    return TECHNICAL_FALLBACK_QUESTIONS


def _build_start_prompt(interview_type, role_title):
    """Return (system_prompt, user_content) for generating the first question."""
    if interview_type == 'hr':
        system_prompt = (
            f"You are a senior HR manager conducting a behavioral interview for the role of '{role_title}'. "
            f"Your task is to ask the FIRST behavioral interview question. "
            f"Focus on soft skills: teamwork, communication, conflict resolution, adaptability, or leadership. "
            f"Do NOT ask technical questions. Keep it concise (1-2 sentences)."
        )
    else:
        system_prompt = (
            f"You are an expert technical interviewer conducting a technical interview for the role of '{role_title}'. "
            f"Your task is to ask the FIRST technical interview question. "
            f"Ask a specific, domain-relevant technical or conceptual question that tests core competency in this field. "
            f"Do NOT ask generic HR/behavioral questions (e.g., 'tell me about yourself'). Keep it concise (1-2 sentences)."
        )
    user_content = f"Job Role: {role_title}. Ask the first question."
    return system_prompt, user_content


def _build_followup_prompt(interview_type, role_title, formatted_history):
    """Return (system_prompt, user_content) for generating a follow-up question."""
    if interview_type == 'hr':
        system_prompt = (
            f"You are a senior HR manager conducting a behavioral interview for the role of '{role_title}'. "
            f"Based on the interview so far, ask a concise follow-up behavioral question that explores the candidate's "
            f"soft skills, emotional intelligence, conflict resolution, or professional attitude. "
            f"Do NOT ask technical questions. Keep it to 1-2 sentences."
        )
    else:
        system_prompt = (
            f"You are an expert technical interviewer for the role of '{role_title}'. "
            f"Based on the interview so far, ask a concise follow-up technical question that digs deeper into the "
            f"candidate's knowledge. It should be domain-specific, test practical understanding, and vary from previous questions. "
            f"Do NOT ask behavioral or HR questions. Keep it to 1-2 sentences."
        )
    return system_prompt, f"Interview History:\n{formatted_history}"


def _build_eval_prompt(interview_type, role_title):
    """Return the system prompt for AI-based evaluation at the end."""
    track = "behavioral/HR" if interview_type == 'hr' else "technical"
    return (
        f"You are an expert senior hiring manager evaluating a candidate for the role of '{role_title}'.\n"
        f"This was a {track} interview. Critically evaluate the transcript below.\n\n"
        f"Scoring Rules:\n"
        f"- For technical interviews: assess accuracy, depth, clarity, and problem-solving approach.\n"
        f"- For HR interviews: assess communication, self-awareness, professionalism, and use of STAR method.\n"
        f"- Be objective and critical. Deduct points for vague, generic, or incomplete answers.\n"
        f"- A score of 90+ is rare; reserve it for truly exceptional answers.\n\n"
        f"Return ONLY a raw JSON object (no markdown) with exactly two keys:\n"
        f"  'score': integer 0-100 representing overall interview readiness\n"
        f"  'feedback': detailed paragraph explaining strengths, weaknesses, and specific improvement suggestions"
    )


@login_required
def mock_interview(request):
    job_roles = JobRole.objects.all()
    session = None
    current_question = None
    transcript = []

    session_id = request.GET.get('session')
    if session_id:
        session = get_object_or_404(MockInterviewSession, pk=session_id, user=request.user)
        transcript = session.transcript or []

    # Get OpenAI client
    client, model_name = get_ai_client_and_model()

    # ── POST ──────────────────────────────────────────────────────────────────
    if request.method == 'POST':
        action = request.POST.get('action')

        # ── START ─────────────────────────────────────────────────────────────
        if action == 'start':
            role_id = request.POST.get('role_id')
            interview_type = request.POST.get('interview_type', 'technical')
            role = get_object_or_404(JobRole, pk=role_id) if role_id else None
            role_title = role.title if role else 'General Professional'
            request.session['interview_type'] = interview_type

            first_question = None
            if client:
                try:
                    sys_prompt, usr_content = _build_start_prompt(interview_type, role_title)
                    resp = client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {'role': 'system', 'content': sys_prompt},
                            {'role': 'user', 'content': usr_content},
                        ]
                    )
                    first_question = resp.choices[0].message.content.strip()
                except Exception:
                    pass

            # Fallback: use domain-appropriate hardcoded question
            if not first_question:
                fallbacks = _get_fallback_questions(interview_type)
                if role:
                    qs = list(InterviewQuestion.objects.filter(
                        job_role=role,
                        category='behavioral' if interview_type == 'hr' else 'technical'
                    ))
                    first_question = qs[0].question if qs else fallbacks[0]
                else:
                    first_question = fallbacks[0]

            session = MockInterviewSession.objects.create(user=request.user, job_role=role, transcript=[])
            request.session['current_interview_question'] = first_question
            return redirect(f'/mock-interview/?session={session.pk}')

        # ── ANSWER ────────────────────────────────────────────────────────────
        elif action == 'answer' and session:
            answer = request.POST.get('answer', '').strip()
            interview_type = request.session.get('interview_type', 'technical')
            role_title = session.job_role.title if session.job_role else 'General Professional'

            question_text = request.session.get('current_interview_question')
            if not question_text:
                # Emergency fallback if session expired
                q_index = len(transcript)
                fallbacks = _get_fallback_questions(interview_type)
                question_text = fallbacks[q_index % len(fallbacks)]

            transcript.append({'question': question_text, 'answer': answer})
            session.transcript = transcript

            # ── 5-question threshold → evaluate and end ──
            if len(transcript) >= 5:
                session.ended_at = timezone.now()
                if client:
                    try:
                        formatted_transcript = ''.join(
                            f"Q{i+1}: {e['question']}\nA{i+1}: {e['answer']}\n\n"
                            for i, e in enumerate(transcript)
                        )
                        resp = client.chat.completions.create(
                            model=model_name,
                            messages=[
                                {'role': 'system', 'content': _build_eval_prompt(interview_type, role_title)},
                                {'role': 'user', 'content': f'Transcript:\n{formatted_transcript}'},
                            ],
                            response_format={'type': 'json_object'}
                        )
                        eval_data = json.loads(resp.choices[0].message.content.strip())
                        session.score = float(eval_data.get('score', 60.0))
                        feedback = eval_data.get('feedback', 'Thank you for completing the interview.')
                        transcript.append({'question': '📊 AI Feedback & Score Breakdown', 'answer': feedback})
                        session.transcript = transcript
                    except Exception:
                        session.score = min(len(transcript) * 18, 90)
                else:
                    session.score = min(len(transcript) * 18, 90)

                session.save()
                request.session.pop('current_interview_question', None)
                return redirect(f'/mock-interview/?session={session.pk}')

            # ── Generate next question ──
            next_question = None
            if client:
                try:
                    formatted_history = ''.join(
                        f"Q{i+1}: {e['question']}\nA{i+1}: {e['answer']}\n\n"
                        for i, e in enumerate(transcript)
                    )
                    sys_prompt, usr_content = _build_followup_prompt(interview_type, role_title, formatted_history)
                    resp = client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {'role': 'system', 'content': sys_prompt},
                            {'role': 'user', 'content': usr_content},
                        ]
                    )
                    next_question = resp.choices[0].message.content.strip()
                except Exception:
                    pass

            if not next_question:
                q_index = len(transcript)
                fallbacks = _get_fallback_questions(interview_type)
                if session.job_role:
                    qs = list(InterviewQuestion.objects.filter(
                        job_role=session.job_role,
                        category='behavioral' if interview_type == 'hr' else 'technical'
                    ))
                    next_question = qs[q_index].question if q_index < len(qs) else fallbacks[q_index % len(fallbacks)]
                else:
                    next_question = fallbacks[q_index % len(fallbacks)]

            session.save()
            request.session['current_interview_question'] = next_question
            return redirect(f'/mock-interview/?session={session.pk}')

        # ── END (early exit) ──────────────────────────────────────────────────
        elif action == 'end' and session:
            interview_type = request.session.get('interview_type', 'technical')
            role_title = session.job_role.title if session.job_role else 'General Professional'
            session.ended_at = timezone.now()

            if len(transcript) > 0 and client:
                try:
                    formatted_transcript = ''.join(
                        f"Q{i+1}: {e['question']}\nA{i+1}: {e['answer']}\n\n"
                        for i, e in enumerate(transcript)
                    )
                    resp = client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {'role': 'system', 'content': _build_eval_prompt(interview_type, role_title)},
                            {'role': 'user', 'content': f'Transcript:\n{formatted_transcript}'},
                        ],
                        response_format={'type': 'json_object'}
                    )
                    eval_data = json.loads(resp.choices[0].message.content.strip())
                    session.score = float(eval_data.get('score', 60.0))
                    feedback = eval_data.get('feedback', 'Interview ended early.')
                    transcript.append({'question': '📊 AI Feedback & Score Breakdown', 'answer': feedback})
                    session.transcript = transcript
                except Exception:
                    session.score = max(len(transcript) * 15, 10)
            else:
                session.score = 0.0

            session.save()
            request.session.pop('current_interview_question', None)
            return redirect(f'/mock-interview/?session={session.pk}')

    # ── GET ────────────────────────────────────────────────────────────────────
    interview_type = request.session.get('interview_type', 'technical')

    if session and not session.ended_at:
        current_question = request.session.get('current_interview_question')
        if not current_question:
            # Session state lost (e.g. browser refresh after server restart) → regenerate
            q_index = len(transcript)
            role_title = session.job_role.title if session.job_role else 'General Professional'

            if client:
                try:
                    if q_index == 0:
                        sys_prompt, usr_content = _build_start_prompt(interview_type, role_title)
                    else:
                        formatted_history = ''.join(
                            f"Q{i+1}: {e['question']}\nA{i+1}: {e['answer']}\n\n"
                            for i, e in enumerate(transcript)
                        )
                        sys_prompt, usr_content = _build_followup_prompt(interview_type, role_title, formatted_history)
                    resp = client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {'role': 'system', 'content': sys_prompt},
                            {'role': 'user', 'content': usr_content},
                        ]
                    )
                    current_question = resp.choices[0].message.content.strip()
                except Exception:
                    pass

            if not current_question:
                fallbacks = _get_fallback_questions(interview_type)
                if session.job_role:
                    qs = list(InterviewQuestion.objects.filter(
                        job_role=session.job_role,
                        category='behavioral' if interview_type == 'hr' else 'technical'
                    ))
                    current_question = qs[q_index].question if q_index < len(qs) else fallbacks[q_index % len(fallbacks)]
                else:
                    current_question = fallbacks[q_index % len(fallbacks)]

            request.session['current_interview_question'] = current_question

    return render(request, 'mock_interview.html', {
        'job_roles': job_roles,
        'session': session,
        'transcript': transcript,
        'current_question': current_question,
        'q_number': len(transcript) + 1,
        'interview_type': interview_type,
    })




# ─── PROJECT BUILDER ─────────────────────────────────────────────────────────

@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            # Generate roadmap
            skills_raw = form.cleaned_data.get('skill_names', '')
            skill_list = [s.strip() for s in skills_raw.split(',') if s.strip()]
            roadmap = []
            for i, skill in enumerate(skill_list, 1):
                roadmap.append({'step': i, 'title': f'Learn {skill}', 'description': f'Study {skill} fundamentals and best practices.', 'done': False})
            roadmap.append({'step': len(skill_list)+1, 'title': 'Build Core Features', 'description': 'Implement the main project functionality.', 'done': False})
            roadmap.append({'step': len(skill_list)+2, 'title': 'Write Tests', 'description': 'Add unit and integration tests.', 'done': False})
            roadmap.append({'step': len(skill_list)+3, 'title': 'Deploy & Document', 'description': 'Deploy the project and write a README.', 'done': False})
            project.roadmap = roadmap
            project.save()

            # Attach skills
            for skill_name in skill_list:
                skill_obj, _ = Skill.objects.get_or_create(name=skill_name)
                project.skills_used.add(skill_obj)

            # Try to create GitHub repo
            github_token = getattr(settings, 'GITHUB_TOKEN', '')
            if github_token:
                repo_url = create_github_repo(
                    repo_name=project.title.lower().replace(' ', '-'),
                    description=project.description[:250],
                    token=github_token
                )
                if repo_url:
                    project.github_repo_url = repo_url
                    project.save()
                    messages.success(request, f'Project created! GitHub repository: {repo_url}')
                else:
                    messages.success(request, 'Project created! (GitHub repo creation failed — check your token)')
            else:
                messages.success(request, 'Project created! Add GITHUB_TOKEN to auto-create a repo.')

            return redirect('project_detail', pk=project.pk)
    else:
        # Pre-fill from missing skills
        profile = UserProfile.objects.filter(user=request.user).first()
        initial_skills = ''
        if profile and profile.target_job_role:
            latest_resume = Resume.objects.filter(user=request.user).first()
            if latest_resume:
                missing = get_skill_gap(latest_resume.extracted_skills, profile.target_job_role)
                initial_skills = ', '.join(missing[:4])
        form = ProjectForm(initial={'skill_names': initial_skills})

    user_projects = UserProject.objects.filter(user=request.user)
    return render(request, 'create_project.html', {'form': form, 'user_projects': user_projects})


@login_required
def project_detail(request, pk):
    project = get_object_or_404(UserProject, pk=pk, user=request.user)
    if request.method == 'POST':
        step_index = int(request.POST.get('step_index', -1))
        if step_index >= 0 and project.roadmap:
            roadmap = project.roadmap
            if step_index < len(roadmap):
                roadmap[step_index]['done'] = not roadmap[step_index].get('done', False)
                project.roadmap = roadmap
                completed = sum(1 for s in roadmap if s.get('done'))
                if completed == len(roadmap):
                    project.status = 'completed'
                elif completed > 0:
                    project.status = 'in_progress'
                project.save()
        return redirect('project_detail', pk=pk)

    return render(request, 'project_detail.html', {'project': project})


# ─── LEADERBOARD ─────────────────────────────────────────────────────────────

@login_required
def leaderboard(request):
    from django.contrib.auth.models import User
    skill_id = request.GET.get('skill')
    selected_skill = None

    if skill_id:
        selected_skill = get_object_or_404(Skill, pk=skill_id)
        rankings = SkillProgress.objects.filter(skill=selected_skill).select_related('user').order_by('-level')[:20]
    else:
        # Overall: average level across all skills per user
        from django.db.models import Avg
        rankings = (
            SkillProgress.objects
            .values('user__username', 'user__first_name', 'user__last_name')
            .annotate(avg_level=Avg('level'), skill_count=Count('skill'))
            .order_by('-avg_level')[:20]
        )

    all_skills = Skill.objects.all()
    user_rank = None
    if not skill_id:
        user_data = SkillProgress.objects.filter(user=request.user).aggregate(avg=Avg('level'))
        user_avg = user_data['avg'] or 0
        user_rank = sum(1 for r in rankings if r.get('avg_level', 0) > user_avg) + 1

    return render(request, 'leaderboard.html', {
        'rankings': rankings,
        'all_skills': all_skills,
        'selected_skill': selected_skill,
        'user_rank': user_rank,
        'is_overall': not skill_id,
    })


# ─── ACHIEVEMENTS ────────────────────────────────────────────────────────────

@login_required
def achievements(request):
    user_achievements = UserAchievement.objects.filter(user=request.user).select_related('achievement')
    all_achievements = Achievement.objects.all()
    earned_ids = set(ua.achievement_id for ua in user_achievements)
    return render(request, 'achievements.html', {
        'user_achievements': user_achievements,
        'all_achievements': all_achievements,
        'earned_ids': earned_ids,
    })


# ─── COMPANY QUESTIONS ───────────────────────────────────────────────────────

@login_required
def company_questions(request):
    company_filter = request.GET.get('company', '')
    questions = CompanyQuestion.objects.all()
    if company_filter:
        questions = questions.filter(company_name__icontains=company_filter)
    companies = CompanyQuestion.objects.order_by('company_name').values_list('company_name', flat=True).distinct()

    submit_form = CompanyQuestionForm()
    if request.method == 'POST':
        submit_form = CompanyQuestionForm(request.POST)
        if submit_form.is_valid():
            cq = submit_form.save(commit=False)
            cq.submitted_by = request.user
            cq.save()
            messages.success(request, 'Question submitted! Thank you for contributing.')
            return redirect('company_questions')

    return render(request, 'company_questions.html', {
        'questions': questions,
        'companies': companies,
        'company_filter': company_filter,
        'submit_form': submit_form,
    })


# ─── ATS RESUME FORMATTER ────────────────────────────────────────────────────


# ─── RESUME STUDIO (merged Resume Builder + ATS Formatter) ───────────────────

@login_required
def resume_studio(request):
    """
    Unified Resume Studio: one form → two outputs:
      1. Visual resume (3 templates with live mini-preview cards)
      2. ATS-safe plain text (copy / print)
    """
    data = None
    ats_text = None

    if request.method == 'POST':
        form = ResumeBuilderForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            data = d

            # ── Build ATS plain text ────────────────────────────────────────
            lines = []
            lines.append(d['full_name'].upper())
            contact_parts = [d['email'], d.get('phone', '')]
            if d.get('linkedin'):
                contact_parts.append(d['linkedin'])
            if d.get('github'):
                contact_parts.append(d['github'])
            lines.append(' | '.join(p for p in contact_parts if p))
            lines.append('')
            lines.append('PROFESSIONAL SUMMARY')
            lines.append('-' * 40)
            lines.append(d['summary'])
            lines.append('')
            lines.append('SKILLS')
            lines.append('-' * 40)
            lines.append(d['skills'])
            lines.append('')
            lines.append('EXPERIENCE')
            lines.append('-' * 40)
            lines.append(d['experience'])
            lines.append('')
            lines.append('EDUCATION')
            lines.append('-' * 40)
            lines.append(d['education'])
            if d.get('projects'):
                lines.append('')
                lines.append('PROJECTS')
                lines.append('-' * 40)
                lines.append(d['projects'])
            if d.get('certifications'):
                lines.append('')
                lines.append('CERTIFICATIONS')
                lines.append('-' * 40)
                lines.append(d['certifications'])
            ats_text = '\n'.join(lines)
    else:
        form = ResumeBuilderForm()

    return render(request, 'resume_studio.html', {
        'form': form,
        'data': data,
        'ats_text': ats_text,
    })


@login_required
def create_resume_form(request):
    return redirect('resume_studio')


@login_required
def create_resume(request):
    return redirect('resume_studio')


# ─── RESUME COMPARISON ───────────────────────────────────────────────────────

@login_required
def compare_resumes(request):
    user_resumes = Resume.objects.filter(user=request.user)
    resume1 = resume2 = comparison = None

    r1_id = request.GET.get('r1')
    r2_id = request.GET.get('r2')

    if r1_id and r2_id:
        resume1 = get_object_or_404(Resume, pk=r1_id, user=request.user)
        resume2 = get_object_or_404(Resume, pk=r2_id, user=request.user)
        skills1 = set(resume1.extracted_skills)
        skills2 = set(resume2.extracted_skills)
        comparison = {
            'only_in_r1': list(skills1 - skills2),
            'only_in_r2': list(skills2 - skills1),
            'common': list(skills1 & skills2),
            'score_diff': round(resume1.score - resume2.score, 1),
        }

    return render(request, 'compare_resumes.html', {
        'user_resumes': user_resumes,
        'resume1': resume1,
        'resume2': resume2,
        'comparison': comparison,
        'r1_id': r1_id,
        'r2_id': r2_id,
    })


# ─── CERTIFICATE ─────────────────────────────────────────────────────────────

@login_required
def generate_certificate(request, skill_id):
    skill = get_object_or_404(Skill, pk=skill_id)
    sp = get_object_or_404(SkillProgress, user=request.user, skill=skill)
    if sp.test_score < 80:
        messages.warning(request, f'You need a test score of 80% or higher to earn a certificate. Your score: {sp.test_score}%')
        return redirect('skill_tracker_detail', skill_id=skill_id)
    return render(request, 'certificate.html', {
        'user': request.user,
        'skill': skill,
        'score': sp.test_score,
        'date': timezone.now().date(),
    })


# ─── ADMIN ANALYTICS ─────────────────────────────────────────────────────────

@staff_member_required
def admin_analytics(request):
    from django.contrib.auth.models import User
    total_users = User.objects.count()
    total_resumes = Resume.objects.count()
    avg_skill_level = SkillProgress.objects.aggregate(avg=Avg('level'))['avg'] or 0
    most_tracked = (
        SkillProgress.objects
        .values('skill__name')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    recent_resumes = Resume.objects.select_related('user').order_by('-uploaded_at')[:10]
    top_roles = JobRole.objects.annotate(resume_count=Count('userprofile')).order_by('-resume_count')[:5]

    return render(request, 'admin_analytics.html', {
        'total_users': total_users,
        'total_resumes': total_resumes,
        'avg_skill_level': round(avg_skill_level, 1),
        'most_tracked': most_tracked,
        'recent_resumes': recent_resumes,
        'top_roles': top_roles,
    })


# ─── AI RESUME SUGGESTIONS ───────────────────────────────────────────────────

@login_required
@require_POST
def resume_suggestions(request):
    section = request.POST.get('section', '')
    text = request.POST.get('text', '')

    client, model_name = get_ai_client_and_model()

    if not client:
        fallback = {
            'improved_text': text or "Please paste your current text to see an improved version.",
            'key_changes': [
                f"Use strong action verbs (e.g., 'Spearheaded', 'Engineered', 'Optimized') to describe your {section}.",
                "Add quantifiable metrics and results where possible (e.g., 'reduced latency by 40%').",
                "Ensure correct formatting, grammar, and professional tone."
            ],
            'pro_tips': [
                "Keep descriptions to 3-4 bullet points maximum.",
                "Align keywords with your target job role's required skills."
            ]
        }
        return JsonResponse(fallback)

    try:
        system_prompt = (
            "You are an expert resume writer and ATS specialist.\n"
            "Your task is to analyze and improve the user's resume section (e.g., summary, experience, skills, projects).\n"
            "You MUST return a JSON object with the exact keys: 'improved_text', 'key_changes', 'pro_tips'. Do not return any other text, markdown formatting, or preamble.\n\n"
            "Format requirements:\n"
            "- 'improved_text': The complete, improved, and polished version of the user's input text. Keep it professional, impactful, and ATS-friendly.\n"
            "- 'key_changes': A list of strings (2-4 items) explaining exactly what you changed and why (e.g. 'Replaced passive verbs with active ones', 'Restructured for readability').\n"
            "- 'pro_tips': A list of strings (1-2 items) offering additional advice for this section."
        )
        
        user_content = f"Section Type: {section}\nUser Text:\n{text}"
        
        resp = client.chat.completions.create(
            model=model_name,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_content}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        import json
        data = json.loads(resp.choices[0].message.content.strip())
        return JsonResponse({
            'improved_text': data.get('improved_text', ''),
            'key_changes': data.get('key_changes', []),
            'pro_tips': data.get('pro_tips', [])
        })
    except Exception as e:
        fallback = {
            'improved_text': text or "Please paste your current text to see an improved version.",
            'key_changes': [
                f"Use strong action verbs (e.g., 'Spearheaded', 'Engineered', 'Optimized') to describe your {section}.",
                "Add quantifiable metrics and results where possible (e.g., 'reduced latency by 40%').",
                "Ensure correct formatting, grammar, and professional tone."
            ],
            'pro_tips': [
                "Keep descriptions to 3-4 bullet points maximum.",
                "Align keywords with your target job role's required skills.",
                "Note: AI suggestion is temporarily offline (Rate Limit / Quota reached)."
            ]
        }
        return JsonResponse(fallback)


@login_required
@require_POST
def delete_resume(request, pk):
    import os
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    if resume.file:
        try:
            if os.path.exists(resume.file.path):
                os.remove(resume.file.path)
        except Exception:
            pass
    resume.delete()
    messages.success(request, 'Resume deleted successfully!')
    return redirect('dashboard')
