from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, CompanyQuestion, UserProject, JobRole


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control auth-input',
            'placeholder': 'your@email.com',
            'autocomplete': 'new-password',   # tricks browsers/extensions into ignoring field
            'data-lpignore': 'true',           # disables LastPass overlay
            'data-form-type': 'other',         # defeats TempMail / 1Password detection
            'data-1p-ignore': '',              # disables 1Password
            'spellcheck': 'false',
        })
    )
    first_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove all help_text (causes white unstyled boxes in the UI)
        for field in self.fields.values():
            field.help_text = ''
            field.error_messages = {k: v for k, v in field.error_messages.items()}


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['target_job_role', 'career_goals']
        widgets = {
            'career_goals': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Describe your career goals...'}),
            'target_job_role': forms.Select(attrs={'class': 'form-select'}),
        }


class ResumeUploadForm(forms.Form):
    resume_file = forms.FileField(
        label='Upload Resume (PDF or DOCX)',
        widget=forms.FileInput(attrs={
            'accept': '.pdf,.docx',
            'class': 'form-control',
        })
    )
    target_job_role = forms.ModelChoiceField(
        queryset=JobRole.objects.all(),
        required=False,
        label='Target Job Role',
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label='Select a job role...'
    )


class CompanyQuestionForm(forms.ModelForm):
    class Meta:
        model = CompanyQuestion
        fields = ['company_name', 'job_role', 'question', 'answer_hints', 'category']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Google, Microsoft'}),
            'job_role': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Software Engineer'}),
            'question': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'answer_hints': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select'},
                                     choices=[('technical','Technical'),('behavioral','Behavioral'),('hr','HR'),('system_design','System Design')]),
        }


class ATSResumeForm(forms.Form):
    full_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Full Name'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'your@email.com', 'autocomplete': 'off'}))
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 234 567 8900'}))
    linkedin = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/in/...'}))
    github = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/...'}))
    summary = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Professional summary...'}))
    skills = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Python, Django, JavaScript, ...'}))
    experience = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Job Title | Company | Duration\n- Achievement 1\n- Achievement 2'}))
    education = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Degree | Institution | Year'}))
    certifications = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Certification | Issuer | Year'}))
    projects = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Project Name | Description | Tech Stack'}))


class ProjectForm(forms.ModelForm):
    skill_names = forms.CharField(
        required=False,
        label='Skills Used (comma separated)',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Python, Django, ML...'})
    )

    class Meta:
        model = UserProject
        fields = ['title', 'description', 'github_repo_url', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'github_repo_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/...'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class ResumeBuilderForm(forms.Form):
    template_choice = forms.ChoiceField(
        choices=[('minimal', 'Minimal'), ('professional', 'Professional'), ('creative', 'Creative')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    full_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'your@email.com', 'autocomplete': 'off'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 98765 43210'}))
    linkedin = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/in/...'}))
    github = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/...'}))
    summary = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Professional summary in 2-3 lines...'}))
    skills = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Python, Django, JavaScript, React, SQL...'}))
    experience = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Job Title | Company | Duration\n- Achievement 1\n- Achievement 2'}))
    education = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Degree | Institution | Year'}))
    projects = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Project Name | Tech Stack | Description'}))
    certifications = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Certification | Issuer | Year'}))


# Alias kept for any legacy imports
ResumeStudioForm = ResumeBuilderForm
