from django.core.management.base import BaseCommand
from analyzer.models import (
    Skill, JobRole, InterviewQuestion, CommunicationTip, AptitudeTopic,
    Achievement, JobMarketInsight
)


SKILLS = [
    'Python', 'Django', 'JavaScript', 'React', 'Node.js', 'HTML', 'CSS',
    'Bootstrap', 'SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis',
    'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Scikit-learn',
    'Data Science', 'Data Analysis', 'Pandas', 'NumPy', 'Matplotlib', 'Seaborn',
    'R', 'Tableau', 'Power BI', 'Excel',
    'Java', 'Spring Boot', 'C++', 'C#', '.NET', 'PHP', 'Laravel',
    'Go', 'Rust', 'Kotlin', 'Swift', 'Flutter', 'React Native',
    'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'CI/CD',
    'Git', 'GitHub', 'Linux', 'Bash',
    'REST API', 'GraphQL', 'Microservices', 'System Design', 'Agile', 'Scrum',
    'TypeScript', 'Vue.js', 'Angular', 'FastAPI', 'Flask',
    'OpenCV', 'NLP', 'Computer Vision', 'Blockchain', 'Cybersecurity',
    'Figma', 'UI/UX Design', 'Communication', 'Leadership', 'Problem Solving',
]

JOB_ROLES = {
    'Web Developer': {
        'description': 'Build and maintain websites and web applications.',
        'skills': ['HTML', 'CSS', 'JavaScript', 'React', 'Node.js', 'SQL', 'Git', 'Bootstrap', 'REST API', 'TypeScript'],
        'salary_min': 50000, 'salary_max': 120000, 'demand': 85,
        'employers': ['Google', 'Amazon', 'Microsoft', 'Meta', 'Shopify'],
    },
    'Data Analyst': {
        'description': 'Analyze data to help organizations make better decisions.',
        'skills': ['Python', 'SQL', 'Pandas', 'NumPy', 'Matplotlib', 'Tableau', 'Excel', 'Power BI', 'Data Analysis', 'Statistics'],
        'salary_min': 55000, 'salary_max': 110000, 'demand': 90,
        'employers': ['Deloitte', 'McKinsey', 'JPMorgan', 'Netflix', 'Spotify'],
    },
    'Machine Learning Engineer': {
        'description': 'Design and implement ML models for production systems.',
        'skills': ['Python', 'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Scikit-learn', 'SQL', 'Docker', 'AWS', 'Git'],
        'salary_min': 90000, 'salary_max': 180000, 'demand': 95,
        'employers': ['OpenAI', 'Google DeepMind', 'Meta AI', 'Tesla', 'Nvidia'],
    },
    'Data Scientist': {
        'description': 'Extract insights from large datasets using statistical and ML methods.',
        'skills': ['Python', 'R', 'Machine Learning', 'Data Science', 'SQL', 'Pandas', 'NumPy', 'NLP', 'Matplotlib', 'Scikit-learn'],
        'salary_min': 80000, 'salary_max': 160000, 'demand': 92,
        'employers': ['Amazon', 'Apple', 'LinkedIn', 'Uber', 'Airbnb'],
    },
    'Backend Developer': {
        'description': 'Build server-side logic, APIs, and databases.',
        'skills': ['Python', 'Django', 'REST API', 'SQL', 'PostgreSQL', 'Docker', 'Redis', 'AWS', 'Git', 'Microservices'],
        'salary_min': 65000, 'salary_max': 130000, 'demand': 88,
        'employers': ['Stripe', 'Twilio', 'GitHub', 'Dropbox', 'Slack'],
    },
    'Full Stack Developer': {
        'description': 'Work across the entire web application stack — front to back.',
        'skills': ['JavaScript', 'React', 'Node.js', 'Python', 'Django', 'SQL', 'MongoDB', 'Docker', 'AWS', 'Git'],
        'salary_min': 75000, 'salary_max': 150000, 'demand': 90,
        'employers': ['Atlassian', 'HubSpot', 'Salesforce', 'Oracle', 'SAP'],
    },
    'DevOps Engineer': {
        'description': 'Automate and streamline software delivery and infrastructure operations.',
        'skills': ['Docker', 'Kubernetes', 'AWS', 'CI/CD', 'Linux', 'Bash', 'Git', 'Python', 'Ansible', 'Terraform'],
        'salary_min': 85000, 'salary_max': 160000, 'demand': 87,
        'employers': ['Red Hat', 'HashiCorp', 'Datadog', 'PagerDuty', 'Cloudflare'],
    },
    'Android Developer': {
        'description': 'Build native Android mobile applications.',
        'skills': ['Kotlin', 'Java', 'Android SDK', 'Git', 'REST API', 'SQL', 'Agile', 'Flutter'],
        'salary_min': 70000, 'salary_max': 140000, 'demand': 82,
        'employers': ['Samsung', 'Google', 'Spotify', 'Uber', 'DoorDash'],
    },
    'UI/UX Designer': {
        'description': 'Design intuitive and visually appealing user interfaces.',
        'skills': ['Figma', 'UI/UX Design', 'HTML', 'CSS', 'JavaScript', 'Communication', 'Agile'],
        'salary_min': 55000, 'salary_max': 120000, 'demand': 80,
        'employers': ['Apple', 'Adobe', 'Figma', 'InVision', 'IDEO'],
    },
    'Cybersecurity Analyst': {
        'description': 'Protect systems, networks, and programs from digital attacks.',
        'skills': ['Cybersecurity', 'Linux', 'Python', 'Networking', 'Bash', 'System Design', 'Problem Solving'],
        'salary_min': 75000, 'salary_max': 145000, 'demand': 93,
        'employers': ['CrowdStrike', 'Palo Alto Networks', 'FireEye', 'Booz Allen', 'CISA'],
    },
}

INTERVIEW_QUESTIONS = {
    'Web Developer': [
        ('What is the difference between HTML, CSS, and JavaScript?', 'HTML structures, CSS styles, JS adds behaviour.', 'technical'),
        ('Explain the box model in CSS.', 'Content + padding + border + margin.', 'technical'),
        ('What is responsive web design?', 'Flexible layouts that adapt to screen sizes using media queries.', 'technical'),
        ('What is the difference between GET and POST requests?', 'GET retrieves data; POST submits data. GET params are in URL; POST in body.', 'technical'),
        ('Explain event bubbling in JavaScript.', 'Events propagate from child to parent elements.', 'technical'),
        ('What is CORS and how do you handle it?', 'Cross-Origin Resource Sharing; handled via headers on the server.', 'technical'),
        ('Describe RESTful APIs.', 'Stateless client-server architecture using HTTP methods.', 'technical'),
        ('What is the difference between == and === in JavaScript?', '== does type coercion; === is strict equality.', 'technical'),
        ('How do you optimize web performance?', 'Minification, lazy loading, CDN, caching, image optimization.', 'technical'),
        ('Explain async/await in JavaScript.', 'Syntactic sugar over Promises for asynchronous code.', 'technical'),
        ('Tell me about a challenging web project you built.', 'STAR method: Situation, Task, Action, Result.', 'behavioral'),
        ('How do you handle cross-browser compatibility?', 'Use CSS resets, feature detection, polyfills, and testing on multiple browsers.', 'behavioral'),
        ('Describe your workflow when starting a new project.', 'Requirements gathering, design, tech selection, iterative development.', 'situational'),
        ('What is a Single Page Application?', 'An app that dynamically rewrites a single HTML page instead of loading new pages.', 'technical'),
        ('How do you ensure your code is maintainable?', 'Clean code, documentation, tests, code reviews.', 'technical'),
    ],
    'Data Analyst': [
        ('What is the difference between INNER JOIN and LEFT JOIN?', 'INNER: only matching rows; LEFT: all rows from left + matching from right.', 'technical'),
        ('Explain the process of data cleaning.', 'Handle nulls, remove duplicates, fix data types, normalize formats.', 'technical'),
        ('What is a pivot table?', 'A tool to summarize and aggregate data in a cross-tabulated format.', 'technical'),
        ('How do you handle missing data?', 'Drop, impute with mean/median/mode, or use ML-based imputation.', 'technical'),
        ('Explain A/B testing.', 'Comparing two variants to determine which performs better statistically.', 'technical'),
        ('What is the difference between mean, median, and mode?', 'Mean: average; Median: middle value; Mode: most frequent.', 'technical'),
        ('Describe a time you turned data into actionable insights.', 'Use STAR method with specific metrics.', 'behavioral'),
        ('What visualization tools have you used?', 'Tableau, Power BI, Matplotlib, Seaborn, Plotly.', 'technical'),
        ('What is standard deviation?', 'Measure of data spread/dispersion from the mean.', 'technical'),
        ('How do you prioritize multiple analysis requests?', 'By business impact, urgency, and data availability.', 'situational'),
        ('What is a p-value?', 'Probability of observing results as extreme as the data if the null hypothesis is true.', 'technical'),
        ('Explain regression analysis.', 'Statistical method to model the relationship between a dependent variable and independent variables.', 'technical'),
        ('What is ETL?', 'Extract, Transform, Load - a data pipeline process.', 'technical'),
        ('How do you communicate findings to non-technical stakeholders?', 'Use clear visuals, avoid jargon, focus on business impact.', 'behavioral'),
        ('What is data normalization?', 'Organizing data to reduce redundancy and improve integrity.', 'technical'),
    ],
    'Machine Learning Engineer': [
        ('What is the difference between supervised and unsupervised learning?', 'Supervised uses labeled data; unsupervised finds patterns without labels.', 'technical'),
        ('Explain overfitting and underfitting.', 'Overfitting: model memorizes training data; Underfitting: model too simple.', 'technical'),
        ('What is gradient descent?', 'Optimization algorithm that minimizes loss by iteratively updating parameters.', 'technical'),
        ('Explain the bias-variance tradeoff.', 'High bias = underfitting; High variance = overfitting; need balance.', 'technical'),
        ('What is cross-validation?', 'Technique to evaluate model generalization by splitting data into folds.', 'technical'),
        ('How do you handle class imbalance?', 'Oversampling (SMOTE), undersampling, class weights, ensemble methods.', 'technical'),
        ('What is regularization?', 'Technique to prevent overfitting by penalizing model complexity (L1/L2).', 'technical'),
        ('Explain precision, recall, and F1 score.', 'Precision: TP/(TP+FP); Recall: TP/(TP+FN); F1: harmonic mean.', 'technical'),
        ('What is transfer learning?', 'Reusing a pre-trained model on a new but related task.', 'technical'),
        ('How do you deploy ML models to production?', 'REST APIs (Flask/FastAPI), Docker containers, cloud platforms (AWS SageMaker).', 'technical'),
        ('Describe a machine learning project from end to end.', 'Data collection → EDA → preprocessing → model → evaluation → deployment.', 'behavioral'),
        ('What is feature engineering?', 'Creating new features from existing data to improve model performance.', 'technical'),
        ('How do you monitor ML models in production?', 'Track data drift, model drift, performance metrics over time.', 'technical'),
        ('What is the difference between bagging and boosting?', 'Bagging: parallel, reduces variance (Random Forest); Boosting: sequential, reduces bias (XGBoost).', 'technical'),
        ('Explain attention mechanisms in transformers.', 'Allows model to focus on relevant parts of input. Self-attention computes Q, K, V matrices.', 'technical'),
    ],
}


COMMUNICATION_TIPS = [
    {
        'title': 'The STAR Method for Behavioral Questions',
        'content': 'Use Situation, Task, Action, Result to structure your answers to behavioral interview questions. This keeps your response focused and demonstrates impact.',
        'video_url': 'https://www.youtube.com/results?search_query=STAR+method+interview',
    },
    {
        'title': 'Body Language in Interviews',
        'content': 'Maintain eye contact, sit up straight, avoid fidgeting, and smile genuinely. Non-verbal communication can be as important as what you say.',
        'video_url': 'https://www.youtube.com/results?search_query=body+language+tips+job+interview',
    },
    {
        'title': 'How to Research a Company Before Interview',
        'content': 'Research the company\'s mission, products, recent news, culture, and the specific team. Tailor your answers to align with their values.',
        'video_url': '',
    },
    {
        'title': 'Answering "Tell Me About Yourself"',
        'content': 'Use a 2-minute pitch: Present (current role/situation) → Past (relevant experience) → Future (why this role excites you).',
        'video_url': 'https://www.youtube.com/results?search_query=tell+me+about+yourself+answer',
    },
    {
        'title': 'Asking Great Questions at the End',
        'content': 'Ask about team culture, biggest challenges, growth opportunities, and what success looks like in the role. Never say "I have no questions".',
        'video_url': '',
    },
]


class Command(BaseCommand):
    help = 'Populate initial data: skills, job roles, interview questions, tips, aptitude topics'

    def handle(self, *args, **options):
        self.stdout.write('Creating skills...')
        skill_objects = {}
        for skill_name in SKILLS:
            obj, created = Skill.objects.get_or_create(name=skill_name)
            skill_objects[skill_name] = obj
            if created:
                self.stdout.write(f'  Created skill: {skill_name}')

        self.stdout.write('\nCreating job roles...')
        for role_title, role_data in JOB_ROLES.items():
            role, created = JobRole.objects.get_or_create(
                title=role_title,
                defaults={'description': role_data['description']}
            )
            if not created:
                role.description = role_data['description']
                role.save()

            # Assign skills
            role.skills.clear()
            for skill_name in role_data['skills']:
                skill_obj = skill_objects.get(skill_name)
                if not skill_obj:
                    skill_obj, _ = Skill.objects.get_or_create(name=skill_name)
                role.skills.add(skill_obj)

            # Market insight
            JobMarketInsight.objects.update_or_create(
                job_role=role,
                defaults={
                    'average_salary_min': role_data['salary_min'],
                    'average_salary_max': role_data['salary_max'],
                    'demand_score': role_data['demand'],
                    'top_employers': role_data['employers'],
                }
            )
            self.stdout.write(f'  Created/updated role: {role_title}')

        self.stdout.write('\nCreating interview questions...')
        for role_title, questions in INTERVIEW_QUESTIONS.items():
            try:
                role = JobRole.objects.get(title=role_title)
            except JobRole.DoesNotExist:
                continue
            for q_text, hint, category in questions:
                InterviewQuestion.objects.get_or_create(
                    job_role=role,
                    question=q_text,
                    defaults={'answer_hints': hint, 'category': category}
                )

        # Add generic questions for all other roles
        generic_questions = [
            ('Why do you want this role?', 'Align your answer with the company mission and your career goals.', 'behavioral'),
            ('What are your biggest strengths?', 'Choose 2-3 strengths relevant to the role with examples.', 'behavioral'),
            ('What is your greatest weakness?', 'Pick real weakness, show self-awareness, describe how you are improving.', 'behavioral'),
            ('Where do you see yourself in 5 years?', 'Show ambition aligned with the company growth path.', 'behavioral'),
            ('Describe a conflict with a teammate. How did you resolve it?', 'Focus on resolution and learnings.', 'situational'),
            ('How do you handle pressure and tight deadlines?', 'Give a specific example with positive outcome.', 'situational'),
            ('Tell me about a time you failed.', 'Be honest, focus on learnings and what you changed.', 'behavioral'),
            ('What motivates you?', 'Be genuine: impact, learning, problem-solving, etc.', 'behavioral'),
        ]
        for role in JobRole.objects.all():
            for q_text, hint, category in generic_questions:
                InterviewQuestion.objects.get_or_create(
                    job_role=role,
                    question=q_text,
                    defaults={'answer_hints': hint, 'category': category}
                )

        self.stdout.write('\nCreating communication tips...')
        for tip_data in COMMUNICATION_TIPS:
            CommunicationTip.objects.get_or_create(
                title=tip_data['title'],
                defaults={'content': tip_data['content'], 'video_url': tip_data['video_url']}
            )

        self.stdout.write('\nCreating achievements...')
        achievements_data = [
            ('First Upload', 'Upload your first resume!', 'fa-file-upload', 'resume_count', 1),
            ('Skill Starter', 'Start tracking your first skill!', 'fa-seedling', 'skill_count', 1),
            ('Fast Learner', 'Track 5 or more skills!', 'fa-bolt', 'skill_count', 5),
            ('Dedicated Learner', 'Track 10 or more skills!', 'fa-star', 'skill_count', 10),
            ('Skill Master', 'Reach 100% in any skill!', 'fa-trophy', 'skill_level', 100),
            ('High Scorer', 'Score 80%+ on a skill test!', 'fa-medal', 'test_score', 80),
            ('Perfect Score', 'Score 100% on a skill test!', 'fa-crown', 'test_score', 100),
            ('Interview Ready', 'Complete your first mock interview!', 'fa-microphone', 'interview_count', 1),
            ('Project Builder', 'Create your first project!', 'fa-hammer', 'project_count', 1),
        ]
        for name, desc, icon, cond_type, cond_val in achievements_data:
            Achievement.objects.get_or_create(
                name=name,
                defaults={'description': desc, 'icon': icon, 'condition_type': cond_type, 'condition_value': cond_val}
            )

        self.stdout.write(self.style.SUCCESS('\n✓ Initial data populated successfully!'))
        self.stdout.write(f'  Skills: {Skill.objects.count()}')
        self.stdout.write(f'  Job Roles: {JobRole.objects.count()}')
        self.stdout.write(f'  Interview Questions: {InterviewQuestion.objects.count()}')
        self.stdout.write(f'  Communication Tips: {CommunicationTip.objects.count()}')
        self.stdout.write(f'  Achievements: {Achievement.objects.count()}')
