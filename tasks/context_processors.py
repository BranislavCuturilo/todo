from .models import Project


def projects_processor(request):
    """Add projects to all template contexts for the quick add modal"""
    if request.user.is_authenticated:
        projects = Project.objects.filter(user=request.user).order_by('priority', 'name')
    else:
        projects = []
    
    return {
        'projects': projects,
    }
