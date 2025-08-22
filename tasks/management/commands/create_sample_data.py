from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from tasks.models import Task, Project, Tag


class Command(BaseCommand):
    help = 'Create sample data for demonstration'

    def handle(self, *args, **options):
        # Get or create the admin user
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={'is_staff': True, 'is_superuser': True}
        )
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write('Created admin user')

        # Create sample projects
        projects = {
            'backend': Project.objects.get_or_create(
                name='Backend Development',
                slug='backend',
                defaults={'description': 'Server-side development tasks'}
            )[0],
            'frontend': Project.objects.get_or_create(
                name='Frontend Development',
                slug='frontend',
                defaults={'description': 'Client-side development tasks'}
            )[0],
            'devops': Project.objects.get_or_create(
                name='DevOps',
                slug='devops',
                defaults={'description': 'Infrastructure and deployment tasks'}
            )[0],
            'planning': Project.objects.get_or_create(
                name='Planning',
                slug='planning',
                defaults={'description': 'Project planning and research'}
            )[0]
        }

        # Create sample tags
        tags = {
            'bug': Tag.objects.get_or_create(name='bug', slug='bug', defaults={'color_hex': '#dc2626'})[0],
            'feature': Tag.objects.get_or_create(name='feature', slug='feature', defaults={'color_hex': '#16a34a'})[0],
            'urgent': Tag.objects.get_or_create(name='urgent', slug='urgent', defaults={'color_hex': '#ea580c'})[0],
            'review': Tag.objects.get_or_create(name='review', slug='review', defaults={'color_hex': '#0284c7'})[0],
            'documentation': Tag.objects.get_or_create(name='documentation', slug='documentation', defaults={'color_hex': '#7c3aed'})[0],
            'testing': Tag.objects.get_or_create(name='testing', slug='testing', defaults={'color_hex': '#059669'})[0]
        }

        # Create sample tasks
        now = timezone.now()
        
        # Overdue tasks
        Task.objects.get_or_create(
            title='Fix authentication bug in login API',
            defaults={
                'status': Task.Status.IN_PROGRESS,
                'priority': Task.Priority.P1,
                'project': projects['backend'],
                'due_at': now - timedelta(days=2),
                'estimate_minutes': 120,
                'description_md': 'Users are experiencing login failures. Need to investigate the JWT token validation issue.'
            }
        )

        Task.objects.get_or_create(
            title='Update SSL certificates',
            defaults={
                'status': Task.Status.TODO,
                'priority': Task.Priority.P1,
                'project': projects['devops'],
                'due_at': now - timedelta(days=1),
                'estimate_minutes': 60,
                'description_md': 'SSL certificates are expiring soon. Need to renew and update the configuration.'
            }
        )

        # Today's tasks
        Task.objects.get_or_create(
            title='Implement user dashboard',
            defaults={
                'status': Task.Status.IN_PROGRESS,
                'priority': Task.Priority.P2,
                'project': projects['frontend'],
                'due_at': now.replace(hour=17, minute=0, second=0, microsecond=0),
                'estimate_minutes': 240,
                'description_md': 'Create a comprehensive dashboard showing user statistics and recent activity.'
            }
        )

        Task.objects.get_or_create(
            title='Code review for payment integration',
            defaults={
                'status': Task.Status.TODO,
                'priority': Task.Priority.P2,
                'project': projects['backend'],
                'due_at': now.replace(hour=16, minute=0, second=0, microsecond=0),
                'estimate_minutes': 90,
                'description_md': 'Review the Stripe payment integration code before merging to main branch.'
            }
        )

        Task.objects.get_or_create(
            title='Write API documentation',
            defaults={
                'status': Task.Status.TODO,
                'priority': Task.Priority.P3,
                'project': projects['planning'],
                'due_at': now.replace(hour=18, minute=0, second=0, microsecond=0),
                'estimate_minutes': 120,
                'description_md': 'Document all REST API endpoints using OpenAPI/Swagger specification.'
            }
        )

        # Inbox tasks
        Task.objects.get_or_create(
            title='Research new database optimization techniques',
            defaults={
                'status': Task.Status.TODO,
                'priority': Task.Priority.P4,
                'project': projects['planning'],
                'estimate_minutes': 180,
                'description_md': 'Investigate PostgreSQL query optimization and indexing strategies for better performance.'
            }
        )

        Task.objects.get_or_create(
            title='Setup automated testing pipeline',
            defaults={
                'status': Task.Status.TODO,
                'priority': Task.Priority.P3,
                'project': projects['devops'],
                'estimate_minutes': 300,
                'description_md': 'Configure CI/CD pipeline with automated testing for both frontend and backend.'
            }
        )

        Task.objects.get_or_create(
            title='Design mobile app wireframes',
            defaults={
                'status': Task.Status.TODO,
                'priority': Task.Priority.P4,
                'project': projects['planning'],
                'estimate_minutes': 240,
                'description_md': 'Create wireframes for the mobile app version of our web application.'
            }
        )

        # Add tags to tasks
        for task in Task.objects.all():
            if 'bug' in task.title.lower():
                task.tags.add(tags['bug'])
            if 'review' in task.title.lower():
                task.tags.add(tags['review'])
            if 'documentation' in task.title.lower():
                task.tags.add(tags['documentation'])
            if 'testing' in task.title.lower():
                task.tags.add(tags['testing'])
            if task.priority == Task.Priority.P1:
                task.tags.add(tags['urgent'])

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )
        self.stdout.write(f'Created {Project.objects.count()} projects')
        self.stdout.write(f'Created {Tag.objects.count()} tags')
        self.stdout.write(f'Created {Task.objects.count()} tasks')
