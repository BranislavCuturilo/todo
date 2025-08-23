from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from tasks.models import Event

class Command(BaseCommand):
    help = 'Create test recurring events'

    def handle(self, *args, **options):
        # Get or create a user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write("Created test user")
        
        # Create a daily event
        daily_event = Event.objects.create(
            title="Daily Standup",
            description="Daily team standup meeting",
            start_time=timezone.make_aware(datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)),
            end_time=timezone.make_aware(datetime.now().replace(hour=9, minute=30, second=0, microsecond=0)),
            user=user,
            is_recurring=True,
            recurrence_type='daily',
            recurrence_interval=1,
            max_occurrences=5  # Only 5 occurrences
        )
        self.stdout.write(f"Created daily event: {daily_event.title}")
        
        # Create a weekly event
        weekly_event = Event.objects.create(
            title="Weekly Team Meeting",
            description="Weekly team meeting",
            start_time=timezone.make_aware(datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)),
            end_time=timezone.make_aware(datetime.now().replace(hour=15, minute=0, second=0, microsecond=0)),
            user=user,
            is_recurring=True,
            recurrence_type='weekly',
            recurrence_interval=1,
            weekdays=[0, 2],  # Monday and Wednesday
            max_occurrences=3  # Only 3 occurrences
        )
        self.stdout.write(f"Created weekly event: {weekly_event.title}")
        
        # Create a monthly event
        monthly_event = Event.objects.create(
            title="Monthly Review",
            description="Monthly project review",
            start_time=timezone.make_aware(datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)),
            end_time=timezone.make_aware(datetime.now().replace(hour=11, minute=0, second=0, microsecond=0)),
            user=user,
            is_recurring=True,
            recurrence_type='monthly',
            recurrence_interval=1,
            end_date=timezone.now().date() + timedelta(days=90)  # End in 3 months
        )
        self.stdout.write(f"Created monthly event: {monthly_event.title}")
        
        self.stdout.write("Test events created successfully!")
