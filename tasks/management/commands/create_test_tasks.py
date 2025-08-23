from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from tasks.models import Task, Project, CalendarTask

class Command(BaseCommand):
    help = 'Create test tasks with different priorities'

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
        
        # Get or create a project
        project, created = Project.objects.get_or_create(
            name='Test Project',
            defaults={'description': 'Test project for priority colors'}
        )
        if created:
            self.stdout.write("Created test project")
        
        # Create tasks with different priorities
        tasks_data = [
            {
                'title': 'Critical Bug Fix (P1)',
                'description': 'Fix critical bug in production',
                'priority': 1,
                'estimate_minutes': 120
            },
            {
                'title': 'High Priority Feature (P2)',
                'description': 'Implement high priority feature',
                'priority': 2,
                'estimate_minutes': 180
            },
            {
                'title': 'Medium Priority Task (P3)',
                'description': 'Work on medium priority task',
                'priority': 3,
                'estimate_minutes': 90
            },
            {
                'title': 'Low Priority Enhancement (P4)',
                'description': 'Add low priority enhancement',
                'priority': 4,
                'estimate_minutes': 60
            },
            {
                'title': 'Minimal Priority Cleanup (P5)',
                'description': 'Code cleanup and documentation',
                'priority': 5,
                'estimate_minutes': 30
            }
        ]
        
        created_tasks = []
        for task_data in tasks_data:
            task = Task.objects.create(
                title=task_data['title'],
                description=task_data['description'],
                priority=task_data['priority'],
                estimate_minutes=task_data['estimate_minutes'],
                project=project,
                user=user,
                status='todo'
            )
            created_tasks.append(task)
            self.stdout.write(f"Created task: {task.title} (P{task.priority})")
        
        # Schedule tasks on calendar for today
        today = timezone.now().date()
        current_time = timezone.now().replace(hour=9, minute=0, second=0, microsecond=0)
        
        for i, task in enumerate(created_tasks):
            start_time = current_time + timedelta(hours=i*2)
            end_time = start_time + timedelta(minutes=task.estimate_minutes)
            
            calendar_task = CalendarTask.objects.create(
                task=task,
                scheduled_start=start_time,
                scheduled_end=end_time,
                calendar_date=today,
                user=user
            )
            self.stdout.write(f"Scheduled task: {task.title} at {start_time.strftime('%H:%M')}")
        
        self.stdout.write("Test tasks created and scheduled successfully!")

