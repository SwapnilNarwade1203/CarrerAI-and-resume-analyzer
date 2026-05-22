from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from analyzer.models import SkillProgress
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Send email reminders to users who have not practiced in 7 days'

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=7)
        # Find users who haven't updated any skill in 7 days
        inactive_users = User.objects.filter(
            skill_progress__last_updated__lt=cutoff
        ).distinct()

        sent_count = 0
        for user in inactive_users:
            if not user.email:
                continue
            try:
                send_mail(
                    subject='🎯 Time to Practice Your Skills!',
                    message=(
                        f'Hi {user.first_name or user.username},\n\n'
                        'It\'s been a week since you last practiced on CareerAI! '
                        'Regular practice is key to landing your dream job.\n\n'
                        'Log in now to:\n'
                        '• Continue your skill roadmap\n'
                        '• Take a skill test\n'
                        '• Review interview questions\n\n'
                        'Keep up the momentum!\n\n'
                        'Best regards,\nCareerAI Team'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
                sent_count += 1
                self.stdout.write(f'  Sent reminder to {user.email}')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  Failed to send to {user.email}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'\n✓ Sent {sent_count} reminder emails'))
