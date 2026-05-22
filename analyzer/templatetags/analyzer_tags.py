from django import template

register = template.Library()


@register.filter(name='zip_feedback')
def zip_feedback(analysis):
    """
    Takes a ResumeAnalysis object and returns a list of (label, score, feedback) tuples
    for use in the analysis detail template accordion.
    """
    if not analysis:
        return []
    return [
        ('Skills Match',   analysis.skill_match_score,   analysis.skill_feedback),
        ('ATS Score',      analysis.ats_score,            analysis.general_feedback),
        ('Experience',     analysis.experience_score,     analysis.experience_feedback),
        ('Projects',       analysis.project_score,        analysis.project_feedback),
        ('Education',      analysis.education_score,      analysis.education_feedback),
        ('Certifications', analysis.certification_score,  analysis.certification_feedback),
    ]


@register.filter(name='zip_options')
def zip_options(question):
    """
    Not actually used in a meaningful way – skill_test.html was refactored
    to inline options. This stub prevents template errors if called elsewhere.
    """
    return []


@register.filter(name='get_item')
def get_item(dictionary, key):
    """Allow dict[key] lookup in templates: {{ mydict|get_item:key }}"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None


@register.filter(name='selectattr')
def selectattr(iterable, attr):
    """
    Filter iterable by truthy attribute value.
    Usage: {{ my_list|selectattr:'done' }}
    """
    try:
        result = []
        for item in iterable:
            if isinstance(item, dict):
                if item.get(attr):
                    result.append(item)
            else:
                if getattr(item, attr, False):
                    result.append(item)
        return result
    except Exception:
        return []


@register.filter(name='subtract')
def subtract(value, arg):
    """Subtract arg from value: {{ value|subtract:arg }}"""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0


@register.simple_tag
def score_color(score):
    """Return a CSS class based on score value."""
    try:
        score = float(score)
        if score >= 70:
            return 'success'
        elif score >= 40:
            return 'warning'
        return 'danger'
    except (ValueError, TypeError):
        return 'secondary'
