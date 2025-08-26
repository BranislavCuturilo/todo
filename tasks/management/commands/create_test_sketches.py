from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tasks.models import Sketch, Project, Task

class Command(BaseCommand):
    help = 'Create test sketches'

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
            defaults={'description': 'Test project for sketches'}
        )
        if created:
            self.stdout.write("Created test project")
        
        # Get or create a task
        task, created = Task.objects.get_or_create(
            title='Test Task',
            defaults={
                'description': 'Test task for sketches',
                'user': user,
                'project': project,
                'status': 'todo'
            }
        )
        if created:
            self.stdout.write("Created test task")
        
        # Create test sketches
        sketches_data = [
            {
                'title': 'UI Wireframe',
                'description': 'Basic layout for login page',
                'project': project,
                'task': task,
                'image_data': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
            },
            {
                'title': 'Database Schema',
                'description': 'ER diagram for user management',
                'project': project,
                'task': None,
                'image_data': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
            },
            {
                'title': 'Workflow Diagram',
                'description': 'User registration flow',
                'project': None,
                'task': task,
                'image_data': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
            }
        ]
        
        for sketch_data in sketches_data:
            sketch = Sketch.objects.create(
                title=sketch_data['title'],
                description=sketch_data['description'],
                project=sketch_data['project'],
                task=sketch_data['task'],
                image_data=sketch_data['image_data'],
                user=user
            )
            self.stdout.write(f"Created sketch: {sketch.title}")
        
        self.stdout.write("Test sketches created successfully!")






