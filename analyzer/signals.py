from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile, SkillProgress, Achievement, UserAchievement


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create UserProfile when a User is created."""
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Ensure UserProfile is saved with the User."""
    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(post_save, sender=SkillProgress)
def check_achievements(sender, instance, **kwargs):
    """Award achievements based on skill progress."""
    user = instance.user

    # Skill Master: reach level 100 in any skill
    if instance.level >= 100:
        achievement, _ = Achievement.objects.get_or_create(
            name='Skill Master',
            defaults={
                'description': 'Reached 100% proficiency in a skill!',
                'icon': 'fa-trophy',
                'condition_type': 'skill_level',
                'condition_value': 100,
            }
        )
        UserAchievement.objects.get_or_create(user=user, achievement=achievement)

    # Fast Learner: track 5+ skills
    tracked_count = SkillProgress.objects.filter(user=user).count()
    if tracked_count >= 5:
        achievement, _ = Achievement.objects.get_or_create(
            name='Fast Learner',
            defaults={
                'description': 'Started tracking 5 or more skills!',
                'icon': 'fa-bolt',
                'condition_type': 'skill_count',
                'condition_value': 5,
            }
        )
        UserAchievement.objects.get_or_create(user=user, achievement=achievement)

    # Dedicated: track 10+ skills
    if tracked_count >= 10:
        achievement, _ = Achievement.objects.get_or_create(
            name='Dedicated Learner',
            defaults={
                'description': 'Started tracking 10 or more skills!',
                'icon': 'fa-star',
                'condition_type': 'skill_count',
                'condition_value': 10,
            }
        )
        UserAchievement.objects.get_or_create(user=user, achievement=achievement)

    # Skill Scorer: score 80+ on any test
    if instance.test_score >= 80:
        achievement, _ = Achievement.objects.get_or_create(
            name='High Scorer',
            defaults={
                'description': 'Scored 80% or higher on a skill test!',
                'icon': 'fa-medal',
                'condition_type': 'test_score',
                'condition_value': 80,
            }
        )
        UserAchievement.objects.get_or_create(user=user, achievement=achievement)
