import re
import io
from django.conf import settings


def extract_text_from_file(file_obj):
    """Extract plain text from PDF or DOCX file."""
    filename = file_obj.name.lower()
    text = ''

    try:
        if filename.endswith('.pdf'):
            import pdfplumber
            with pdfplumber.open(file_obj) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ''
        elif filename.endswith('.docx'):
            from docx import Document
            doc = Document(file_obj)
            for para in doc.paragraphs:
                text += para.text + '\n'
    except Exception as e:
        text = ''

    return text


def clean_text(text):
    """Lowercase and remove excess whitespace/punctuation."""
    text = text.lower()
    text = re.sub(r'[^\w\s\+\#\.]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_skills(text, skill_queryset):
    """Match skills from text using keyword matching."""
    cleaned = clean_text(text)
    found = []
    for skill in skill_queryset:
        name = skill.name.lower()
        # word-boundary-aware search
        pattern = r'\b' + re.escape(name) + r'\b'
        if re.search(pattern, cleaned):
            found.append(skill.name)
    return found


def detect_sections(text):
    """Detect if experience and projects sections are present using strict header line patterns."""
    lower_text = text.lower()
    
    # 1. Experience detection: Look for standard headers on their own line or at the start of a line
    experience_headers = [
        r'(?:^|\n)\s*work\s+experience\s*(?:\n|\r|:|-|\b)',
        r'(?:^|\n)\s*professional\s+experience\s*(?:\n|\r|:|-|\b)',
        r'(?:^|\n)\s*experience\s*(?:\n|\r|:|-|\b)',
        r'(?:^|\n)\s*work\s+history\s*(?:\n|\r|:|-|\b)',
        r'(?:^|\n)\s*employment\s+history\s*(?:\n|\r|:|-|\b)',
        r'(?:^|\n)\s*employment\s*(?:\n|\r|:|-|\b)',
        r'(?:^|\n)\s*job\s+history\s*(?:\n|\r|:|-|\b)',
        r'(?:^|\n)\s*experience\s+history\s*(?:\n|\r|:|-|\b)'
    ]
    
    experience_present = False
    for pat in experience_headers:
        if re.search(pat, lower_text):
            # Avoid single mentions of "user experience" or "customer experience"
            ux_count = lower_text.count('user experience') + lower_text.count('customer experience')
            exp_count = lower_text.count('experience')
            if exp_count > ux_count:
                experience_present = True
                break

    # 2. Projects detection: Look for standard headers on their own line or at the start of a line
    project_headers = [
        r'(?:^|\n)\s*projects\s*(?:\n|\r|:|-|\b)',
        r'(?:^|\n)\s*academic\s+projects\s*(?:\n|\r|:|-|\b)',
        r'(?:^|\n)\s*personal\s+projects\s*(?:\n|\r|:|-|\b)',
        r'(?:^|\n)\s*key\s+projects\s*(?:\n|\r|:|-|\b)',
        r'(?:^|\n)\s*project\s+details\s*(?:\n|\r|:|-|\b)',
        r'(?:^|\n)\s*portfolio\s*(?:\n|\r|:|-|\b)'
    ]
    projects_present = False
    for pat in project_headers:
        if re.search(pat, lower_text):
            projects_present = True
            break
            
    return experience_present, projects_present


def calculate_resume_score(extracted_skills, job_role, experience_present, projects_present):
    """
    Score = 50% skill match + 25% projects + 25% experience
    """
    skill_match_score = 0.0
    if job_role:
        required_skills = list(job_role.skills.values_list('name', flat=True))
        if required_skills:
            matched = [s for s in extracted_skills if s in required_skills]
            skill_match_score = len(matched) / len(required_skills) * 100
    else:
        skill_match_score = min(len(extracted_skills) * 5, 100)

    experience_score = 100.0 if experience_present else 0.0
    project_score = 100.0 if projects_present else 0.0

    total = (skill_match_score * 0.5) + (experience_score * 0.25) + (project_score * 0.25)
    return round(total, 1), round(skill_match_score, 1)


def get_skill_gap(extracted_skills, job_role):
    """Return missing skills for the target job role."""
    if not job_role:
        return []
    required = list(job_role.skills.values_list('name', flat=True))
    missing = [s for s in required if s not in extracted_skills]
    return missing


CERTIFICATION_MAP = {
    'python': [{'name': 'PCAP - Certified Associate in Python', 'provider': 'Python Institute', 'url': 'https://pythoninstitute.org/pcap'}],
    'aws': [{'name': 'AWS Certified Solutions Architect', 'provider': 'Amazon', 'url': 'https://aws.amazon.com/certification/'}],
    'azure': [{'name': 'AZ-900 Microsoft Azure Fundamentals', 'provider': 'Microsoft', 'url': 'https://learn.microsoft.com/en-us/certifications/'}],
    'machine learning': [{'name': 'TensorFlow Developer Certificate', 'provider': 'Google', 'url': 'https://www.tensorflow.org/certificate'}],
    'data science': [{'name': 'IBM Data Science Professional Certificate', 'provider': 'Coursera', 'url': 'https://www.coursera.org/professional-certificates/ibm-data-science'}],
    'javascript': [{'name': 'JavaScript Algorithms & Data Structures', 'provider': 'freeCodeCamp', 'url': 'https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/'}],
    'react': [{'name': 'Meta Front-End Developer Certificate', 'provider': 'Coursera', 'url': 'https://www.coursera.org/professional-certificates/meta-front-end-developer'}],
    'sql': [{'name': 'Oracle Database SQL Certified Associate', 'provider': 'Oracle', 'url': 'https://education.oracle.com/'}],
    'docker': [{'name': 'Docker Certified Associate', 'provider': 'Docker', 'url': 'https://training.docker.com/certification'}],
    'kubernetes': [{'name': 'Certified Kubernetes Administrator (CKA)', 'provider': 'CNCF', 'url': 'https://www.cncf.io/certification/cka/'}],
    'django': [{'name': 'Python Web Frameworks–Django', 'provider': 'Coursera', 'url': 'https://www.coursera.org/learn/django-web-framework'}],
    'tensorflow': [{'name': 'TensorFlow Developer Certificate', 'provider': 'Google', 'url': 'https://www.tensorflow.org/certificate'}],
    'tableau': [{'name': 'Tableau Desktop Specialist', 'provider': 'Tableau', 'url': 'https://www.tableau.com/learn/certification'}],
    'power bi': [{'name': 'Microsoft Certified: Power BI Data Analyst', 'provider': 'Microsoft', 'url': 'https://learn.microsoft.com/en-us/certifications/'}],
    'java': [{'name': 'Oracle Certified Professional Java SE', 'provider': 'Oracle', 'url': 'https://education.oracle.com/'}],
}

PROJECT_MAP = {
    'python': ['Build a Web Scraper', 'Create a CLI Task Manager', 'Develop a Data Pipeline Script'],
    'django': ['Build a Blog with User Auth', 'Create a REST API', 'Develop an E-commerce Site'],
    'machine learning': ['Sentiment Analysis Model', 'Image Classification CNN', 'House Price Predictor'],
    'data science': ['Exploratory Data Analysis Project', 'Movie Recommendation System', 'COVID-19 Data Dashboard'],
    'javascript': ['Build a Todo App', 'Create a Weather Widget', 'Develop a Browser Game'],
    'react': ['Build a Personal Portfolio', 'Create a Real-time Chat UI', 'Develop a Dashboard App'],
    'sql': ['Design an Inventory Database', 'Build a Report Generator', 'Create a Student Management DB'],
    'docker': ['Containerize a Web App', 'Multi-container App with Docker Compose', 'CI/CD Pipeline with Docker'],
    'kubernetes': ['Deploy App on Minikube', 'K8s Rolling Update Strategy', 'Helm Chart for Web Service'],
    'aws': ['Host Static Site on S3', 'Lambda Serverless Function', 'Auto-scaling EC2 Web App'],
    'tensorflow': ['MNIST Digit Recognition', 'Neural Style Transfer App', 'NLP Text Classifier'],
    'node.js': ['REST API with Express', 'Real-time App with Socket.io', 'CLI Tool with Commander.js'],
    'flutter': ['Mobile To-Do App', 'Weather App with API', 'E-commerce Mobile UI'],
    'java': ['Spring Boot REST API', 'Android Calculator App', 'Inventory Management System'],
    'c++': ['Data Structures Library', 'Simple Game Engine', 'File Compression Tool'],
    'default': ['Build a Portfolio Website', 'Create a Personal Blog', 'Develop a Calculator App'],
}

COURSE_MAP = {
    'python': [
        {'name': 'Python for Everybody', 'platform': 'Coursera', 'url': 'https://www.coursera.org/specializations/python'},
        {'name': 'Complete Python Bootcamp', 'platform': 'Udemy', 'url': 'https://www.udemy.com/course/complete-python-bootcamp/'},
    ],
    'django': [
        {'name': 'Django for Beginners', 'platform': 'YouTube', 'url': 'https://www.youtube.com/results?search_query=django+for+beginners'},
        {'name': 'Django Full Course', 'platform': 'Udemy', 'url': 'https://www.udemy.com/course/python-django-the-practical-guide/'},
    ],
    'machine learning': [
        {'name': 'Machine Learning Specialization', 'platform': 'Coursera', 'url': 'https://www.coursera.org/specializations/machine-learning-introduction'},
        {'name': 'ML with Python', 'platform': 'YouTube', 'url': 'https://www.youtube.com/results?search_query=machine+learning+python+course'},
    ],
    'javascript': [
        {'name': 'The Complete JavaScript Course', 'platform': 'Udemy', 'url': 'https://www.udemy.com/course/the-complete-javascript-course/'},
        {'name': 'JavaScript Full Course', 'platform': 'YouTube', 'url': 'https://www.youtube.com/results?search_query=javascript+full+course'},
    ],
    'react': [
        {'name': 'React - The Complete Guide', 'platform': 'Udemy', 'url': 'https://www.udemy.com/course/react-the-complete-guide-incl-redux/'},
        {'name': 'React Tutorial', 'platform': 'YouTube', 'url': 'https://www.youtube.com/results?search_query=react+js+tutorial+2024'},
    ],
    'sql': [
        {'name': 'SQL for Data Science', 'platform': 'Coursera', 'url': 'https://www.coursera.org/learn/sql-for-data-science'},
        {'name': 'Complete SQL Bootcamp', 'platform': 'Udemy', 'url': 'https://www.udemy.com/course/the-complete-sql-bootcamp/'},
    ],
    'aws': [
        {'name': 'AWS Certified Solutions Architect', 'platform': 'Udemy', 'url': 'https://www.udemy.com/course/aws-certified-solutions-architect-associate-saa-c03/'},
        {'name': 'AWS Free Training', 'platform': 'AWS', 'url': 'https://aws.amazon.com/training/'},
    ],
    'default': [
        {'name': 'Search on YouTube', 'platform': 'YouTube', 'url': 'https://www.youtube.com/results?search_query='},
        {'name': 'Search on Coursera', 'platform': 'Coursera', 'url': 'https://www.coursera.org/search?query='},
    ],
}


def get_recommendations(missing_skills):
    """Return projects, courses, and certifications for missing skills."""
    if not missing_skills:
        return [], [], []

    # Try AI recommendation first
    try:
        client, model_name = get_ai_client_and_model()
        if client:
            import json
            skills_to_use = missing_skills[:6] # cap at 6 to keep it fast
            system_prompt = (
                "You are an expert career adviser and tech mentor.\n"
                "Your task is to recommend projects, courses, and certifications to help a candidate bridge their missing skills.\n"
                "You must return a JSON object with the exact keys: 'projects', 'courses', 'certifications'.\n\n"
                "Format requirements:\n"
                "- 'projects': list of objects, each with 'skill' (the exact skill name) and 'project' (a brief project title/idea).\n"
                "- 'courses': list of objects, each with 'skill' (the exact skill name), 'name' (course name), 'platform' (e.g. Coursera, Udemy, YouTube, edX), and 'url' (a clean, valid URL to search or view the course, e.g. 'https://www.coursera.org/search?query=python').\n"
                "- 'certifications': list of objects, each with 'skill' (the exact skill name), 'name' (certification name), 'provider' (e.g. AWS, Microsoft, Python Institute, CNCF), and 'url' (valid URL to the certification page).\n\n"
                "Ensure all URLs are clean, valid, and secure (HTTPS). Do not return any other text, markdown formatting, or preamble."
            )
            
            user_content = f"Missing Skills: {', '.join(skills_to_use)}"
            
            resp = client.chat.completions.create(
                model=model_name,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_content}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            data = json.loads(resp.choices[0].message.content.strip())
            projects = data.get('projects', [])
            courses = data.get('courses', [])
            certifications = data.get('certifications', [])
            
            # Make sure keys are present and types are correct
            valid_projects = []
            for p in projects:
                if isinstance(p, dict) and 'skill' in p and 'project' in p:
                    valid_projects.append(p)
                    
            valid_courses = []
            for c in courses:
                if isinstance(c, dict) and 'skill' in c and 'name' in c and 'platform' in c and 'url' in c:
                    valid_courses.append(c)
                    
            valid_certs = []
            for cert in certifications:
                if isinstance(cert, dict) and 'skill' in cert and 'name' in cert and 'provider' in cert and 'url' in cert:
                    valid_certs.append(cert)
                    
            if valid_projects or valid_courses or valid_certs:
                return valid_projects, valid_courses, valid_certs
    except Exception as e:
        # Fall back to manual recommendations on exception
        pass

    # Manual Fallback
    projects = []
    courses = []
    certifications = []

    for skill_name in missing_skills[:8]:  # cap at 8
        skill_key = skill_name.lower()

        # Projects
        proj_list = PROJECT_MAP.get(skill_key, PROJECT_MAP['default'])
        for p in proj_list[:2]:
            projects.append({'skill': skill_name, 'project': p})

        # Courses
        course_list = COURSE_MAP.get(skill_key, None)
        if course_list:
            for c in course_list[:2]:
                courses.append({'skill': skill_name, **c})
        else:
            courses.append({
                'skill': skill_name,
                'name': f'Learn {skill_name}',
                'platform': 'YouTube',
                'url': f'https://www.youtube.com/results?search_query={skill_name.replace(" ", "+")}+tutorial'
            })

        # Certifications
        cert_list = CERTIFICATION_MAP.get(skill_key, [])
        for cert in cert_list[:1]:
            certifications.append({'skill': skill_name, **cert})

    return projects, courses, certifications


def create_github_repo(repo_name, description, token):
    """Create a GitHub repository using PyGithub."""
    try:
        from github import Github
        g = Github(token)
        user = g.get_user()
        repo = user.create_repo(
            name=repo_name,
            description=description,
            private=False,
            auto_init=True
        )
        return repo.html_url
    except Exception as e:
        return None


def generate_ats_resume_text(data):
    """Generate ATS-friendly plain-text resume from form data."""
    lines = []
    lines.append(data.get('full_name', '').upper())
    lines.append(f"Email: {data.get('email','')} | Phone: {data.get('phone','')}")
    if data.get('linkedin'):
        lines.append(f"LinkedIn: {data.get('linkedin','')}")
    if data.get('github'):
        lines.append(f"GitHub: {data.get('github','')}")
    lines.append('')
    lines.append('PROFESSIONAL SUMMARY')
    lines.append('-' * 40)
    lines.append(data.get('summary', ''))
    lines.append('')
    lines.append('SKILLS')
    lines.append('-' * 40)
    lines.append(data.get('skills', ''))
    lines.append('')
    lines.append('PROFESSIONAL EXPERIENCE')
    lines.append('-' * 40)
    lines.append(data.get('experience', ''))
    lines.append('')
    lines.append('EDUCATION')
    lines.append('-' * 40)
    lines.append(data.get('education', ''))
    if data.get('projects'):
        lines.append('')
        lines.append('PROJECTS')
        lines.append('-' * 40)
        lines.append(data.get('projects', ''))
    if data.get('certifications'):
        lines.append('')
        lines.append('CERTIFICATIONS')
        lines.append('-' * 40)
        lines.append(data.get('certifications', ''))
    return '\n'.join(lines)


_ai_client_cache = {}  # module-level cache: avoids re-instantiating on every request


def get_ai_client_and_model():
    """
    Returns (client, model_name) based on the configured OPENAI_API_KEY.
    The client object is cached at module level to avoid re-initializing on every request.
    """
    from openai import OpenAI
    api_key = getattr(settings, 'OPENAI_API_KEY', '')
    if not api_key:
        return None, None

    if api_key in _ai_client_cache:
        return _ai_client_cache[api_key]

    if api_key.startswith('AIzaSy'):
        client = OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        result = client, "gemini-2.5-flash"
    else:
        client = OpenAI(api_key=api_key)
        result = client, "gpt-3.5-turbo"

    _ai_client_cache[api_key] = result
    return result


def analyze_resume_with_ai(resume_text, target_job_role_title):
    """
    Analyzes resume text against a target job role using OpenAI or Gemini.
    Returns a dict containing scores, feedback, and skill lists.
    """
    client, model_name = get_ai_client_and_model()
    if not client:
        raise ValueError("AI API Key is not set.")

    system_prompt = (
        "You are an expert ATS (Applicant Tracking System) and professional resume reviewer.\n"
        "Your task is to analyze the provided resume text against the target job role: '{role}'.\n"
        "You MUST return a JSON object with the exact keys described below. Do not return any other text, markdown formatting, or preamble.\n\n"
        "CRITICAL RULES FOR SCORING:\n"
        "- If a section is completely missing or has no content (e.g., the candidate has no work experience/employment section, no projects, or no certifications), you MUST assign a score of 0 for that specific score (e.g., experience_score, project_score, or certification_score).\n"
        "- Do not make up or assume any details not present in the resume.\n"
        "- Be highly critical and objective. A perfect score of 100 should only be given if the candidate perfectly matches the job role requirements and has outstanding qualifications.\n\n"
        "Expected JSON format:\n"
        "{{\n"
        "  \"ats_score\": <float between 0 and 100>,\n"
        "  \"education_score\": <float between 0 and 100>,\n"
        "  \"project_score\": <float between 0 and 100>,\n"
        "  \"experience_score\": <float between 0 and 100>,\n"
        "  \"certification_score\": <float between 0 and 100>,\n"
        "  \"skill_match_score\": <float between 0 and 100>,\n"
        "  \"education_feedback\": \"<string>\",\n"
        "  \"project_feedback\": \"<string>\",\n"
        "  \"experience_feedback\": \"<string>\",\n"
        "  \"certification_feedback\": \"<string>\",\n"
        "  \"skill_feedback\": \"<string>\",\n"
        "  \"general_feedback\": \"<string>\",\n"
        "  \"extracted_skills\": [\"<skill1>\", \"<skill2>\", ...],\n"
        "  \"missing_skills\": [\"<skill1>\", \"<skill2>\", ...]\n"
        "}}\n"
    ).format(role=target_job_role_title or "General Resume Evaluation")

    resp = client.chat.completions.create(
        model=model_name,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': f"Resume Text:\n{resume_text}"}
        ],
        temperature=0.2,
        response_format={"type": "json_object"}
    )

    import json
    result = json.loads(resp.choices[0].message.content.strip())
    return result
