from django.core.management.base import BaseCommand
from tasks.models import Project


class Command(BaseCommand):
    help = 'Set initial priorities for existing projects based on creation date'

    def handle(self, *args, **options):
        projects = Project.objects.all().order_by('created_at')
        
        for index, project in enumerate(projects):
            project.priority = index
            project.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Set priority {index} for project "{project.name}"'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully set priorities for {projects.count()} projects'
            )
        )
