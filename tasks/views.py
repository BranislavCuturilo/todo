from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Count, Case, When, IntegerField
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.text import slugify
from datetime import datetime, timedelta
import json

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic import FormView
from django.urls import reverse_lazy

from .models import Task, Project, Tag, TaskRelationship, FocusSession
from .forms import TaskForm, ProjectForm, TaskRelationshipForm
from .utils import parse_quick_add

class CustomLoginView(FormView):
    template_name = 'auth/login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('dashboard')
    
    def post(self, request, *args, **kwargs):
        print(f"POST request received: {request.POST}")
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        print(f"Form valid - Username: {username}")
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
            messages.success(self.request, f'Welcome back, {user.username}!')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'Invalid username or password.')
            return self.form_invalid(form)

@login_required
def dashboard(request):
    # Get filter parameters
    priority_filter = request.GET.get('priority')
    project_filter = request.GET.get('project')
    status_filter = request.GET.get('status')
    
    # Base querysets
    tasks_today = Task.objects.filter(user=request.user, due_at__date=timezone.now().date())
    overdue = Task.objects.filter(user=request.user, due_at__lt=timezone.now(), status__in=['todo', 'in_progress'])
    inbox = Task.objects.filter(user=request.user, project__isnull=True, status__in=['todo', 'in_progress'])
    
    # Apply filters
    if priority_filter:
        tasks_today = tasks_today.filter(priority=priority_filter)
        overdue = overdue.filter(priority=priority_filter)
        inbox = inbox.filter(priority=priority_filter)
    
    if project_filter:
        tasks_today = tasks_today.filter(project_id=project_filter)
        overdue = overdue.filter(project_id=project_filter)
        inbox = inbox.filter(project_id=project_filter)
    
    if status_filter:
        tasks_today = tasks_today.filter(status=status_filter)
        overdue = overdue.filter(status=status_filter)
        inbox = inbox.filter(status=status_filter)
    
    projects = Project.objects.all()
    
    current_filters = {
        'priority': priority_filter,
        'project': project_filter,
        'status': status_filter,
    }
    
    context = {
        'tasks_today': tasks_today,
        'overdue': overdue,
        'inbox': inbox,
        'projects': projects,
        'current_filters': current_filters,
        'now': timezone.now(),
    }
    return render(request, 'tasks/dashboard.html', context)

@login_required
def list_inbox(request):
    tasks = Task.objects.filter(user=request.user, project__isnull=True, status__in=['todo', 'in_progress'])
    return render(request, 'tasks/list.html', {'tasks': tasks, 'title': 'Inbox', 'now': timezone.now()})

@login_required
def list_today(request):
    tasks = Task.objects.filter(user=request.user, due_at__date=timezone.now().date())
    return render(request, 'tasks/list.html', {'tasks': tasks, 'title': 'Today', 'now': timezone.now()})

@login_required
def list_upcoming(request):
    tasks = Task.objects.filter(user=request.user, due_at__gt=timezone.now(), status__in=['todo', 'in_progress'])
    return render(request, 'tasks/list.html', {'tasks': tasks, 'title': 'Upcoming', 'now': timezone.now()})

@login_required
def list_done(request):
    tasks = Task.objects.filter(user=request.user, status='done')
    return render(request, 'tasks/list.html', {'tasks': tasks, 'title': 'Done', 'now': timezone.now()})

@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    relationships = TaskRelationship.objects.filter(from_task=task)
    incoming_relationships = TaskRelationship.objects.filter(to_task=task)
    
    context = {
        'task': task,
        'relationships': relationships,
        'incoming_relationships': incoming_relationships,
        'now': timezone.now(),
    }
    return render(request, 'tasks/task_detail.html', context)

@login_required
def project_list(request):
    projects = Project.objects.all()
    return render(request, 'tasks/projects.html', {'projects': projects, 'now': timezone.now()})

@login_required
def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    status_filter = request.GET.get('status', 'all')
    
    if status_filter == 'all':
        tasks = Task.objects.filter(project=project, user=request.user)
    else:
        tasks = Task.objects.filter(project=project, user=request.user, status=status_filter)
    
    context = {
        'project': project,
        'tasks': tasks,
        'status_filter': status_filter,
        'now': timezone.now(),
    }
    return render(request, 'tasks/project_detail.html', context)

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            form.save_m2m()
            messages.success(request, 'Task created successfully!')
            return redirect('task_detail', task_id=task.id)
    else:
        initial = {}
        project_id = request.GET.get('project')
        if project_id:
            initial['project'] = project_id
        form = TaskForm(initial=initial)
    
    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'Create Task'})

@login_required
def task_edit(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('task_detail', task_id=task.id)
    else:
        form = TaskForm(instance=task)
    
    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'Edit Task'})

@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.slug = slugify(project.name)
            project.save()
            messages.success(request, 'Project created successfully!')
            return redirect('project_detail', slug=project.slug)
    else:
        form = ProjectForm()
    
    return render(request, 'tasks/project_form.html', {'form': form, 'title': 'Create Project'})

@login_required
def project_edit(request, slug):
    project = get_object_or_404(Project, slug=slug)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('project_detail', slug=project.slug)
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'tasks/project_form.html', {'form': form, 'title': 'Edit Project'})

@login_required
def quick_add(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        priority = request.POST.get('priority', '3')
        estimate_minutes = request.POST.get('estimate_minutes')
        project_id = request.POST.get('project')
        due_at = request.POST.get('due_at')
        tags = request.POST.get('tags', '')
        
        if title:
            task = Task.objects.create(
                user=request.user,
                title=title,
                description=description,
                priority=int(priority),
                estimate_minutes=int(estimate_minutes) if estimate_minutes else None,
                project_id=project_id if project_id else None,
                due_at=datetime.fromisoformat(due_at.replace('Z', '+00:00')) if due_at else None,
            )
            
            # Handle tags
            if tags:
                tag_names = [tag.strip() for tag in tags.split(',') if tag.strip()]
                for tag_name in tag_names:
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    task.tags.add(tag)
            
            messages.success(request, 'Task added successfully!')
            return redirect('dashboard')
    
    return redirect('dashboard')

@login_required
def snooze_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id, user=request.user)
        minutes = int(request.POST.get('minutes', 30))
        task.due_at = timezone.now() + timedelta(minutes=minutes)
        task.save()
        messages.success(request, f'Task snoozed for {minutes} minutes!')
    
    return redirect('dashboard')

@login_required
def focus_start(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        kind = request.POST.get('kind', 'work')
        
        if task_id:
            task = get_object_or_404(Task, id=task_id, user=request.user)
            session = FocusSession.objects.create(user=request.user, task=task, kind=kind)
        else:
            session = FocusSession.objects.create(user=request.user, kind=kind)
        
        messages.success(request, f'{kind.title()} session started!')
    
    return redirect('dashboard')

@login_required
def focus_end(request):
    if request.method == 'POST':
        session = FocusSession.objects.filter(user=request.user, end_time__isnull=True).first()
        if session:
            session.end()
            messages.success(request, f'Session ended! Duration: {session.duration_minutes} minutes')
    
    return redirect('dashboard')

@login_required
def task_relationships(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    if request.method == 'POST':
        form = TaskRelationshipForm(request.POST)
        if form.is_valid():
            relationship = form.save(commit=False)
            relationship.from_task = task
            relationship.save()
            messages.success(request, 'Relationship created successfully!')
            return redirect('task_relationships', task_id=task.id)
    else:
        form = TaskRelationshipForm()
    
    # Get all tasks for the dropdown (excluding current task)
    available_tasks = Task.objects.filter(user=request.user).exclude(id=task.id)
    
    # Get existing relationships
    outgoing_relationships = TaskRelationship.objects.filter(from_task=task)
    incoming_relationships = TaskRelationship.objects.filter(to_task=task)
    
    context = {
        'task': task,
        'form': form,
        'available_tasks': available_tasks,
        'outgoing_relationships': outgoing_relationships,
        'incoming_relationships': incoming_relationships,
    }
    return render(request, 'tasks/task_relationships.html', context)

@login_required
def optimal_task_order(request):
    """Calculate optimal task order based on dependencies, priorities, and due dates"""
    
    # Get all user's tasks
    tasks = Task.objects.filter(user=request.user, status__in=['todo', 'in_progress'])
    
    # Calculate task scores for ordering
    for task in tasks:
        # Base score starts with priority (lower number = higher priority)
        score = task.priority
        
        # Add urgency based on due date
        if task.due_at:
            days_until_due = (task.due_at - timezone.now()).days
            if days_until_due < 0:  # Overdue
                score -= 10
            elif days_until_due <= 1:  # Due today/tomorrow
                score -= 5
            elif days_until_due <= 3:  # Due this week
                score -= 2
        
        # Add dependency penalty (tasks that block others get higher priority)
        blocking_count = TaskRelationship.objects.filter(
            from_task=task, 
            relationship_type='blocks'
        ).count()
        score -= blocking_count * 2
        
        # Add dependency requirement penalty (tasks that depend on others get lower priority)
        dependency_count = TaskRelationship.objects.filter(
            to_task=task, 
            relationship_type='depends_on'
        ).count()
        score += dependency_count * 2
        
        task.optimal_score = score
    
    # Sort tasks by optimal score
    optimal_tasks = sorted(tasks, key=lambda x: x.optimal_score)
    
    # Group tasks by project for better organization
    tasks_by_project = {}
    for task in optimal_tasks:
        project_name = task.project.name if task.project else 'No Project'
        if project_name not in tasks_by_project:
            tasks_by_project[project_name] = []
        tasks_by_project[project_name].append(task)
    
    context = {
        'optimal_tasks': optimal_tasks,
        'tasks_by_project': tasks_by_project,
        'now': timezone.now(),
    }
    return render(request, 'tasks/optimal_order.html', context)

@login_required
def create_project_from_tasks(request):
    """Create a new project from selected tasks"""
    if request.method == 'POST':
        project_name = request.POST.get('project_name')
        task_ids = request.POST.getlist('task_ids')
        
        if project_name and task_ids:
            # Create the project
            project = Project.objects.create(
                name=project_name,
                slug=slugify(project_name)
            )
            
            # Assign tasks to the project
            tasks = Task.objects.filter(id__in=task_ids, user=request.user)
            for task in tasks:
                task.project = project
                task.save()
            
            messages.success(request, f'Project "{project_name}" created with {len(tasks)} tasks!')
            return redirect('project_detail', slug=project.slug)
    
    # Get tasks without projects
    unassigned_tasks = Task.objects.filter(user=request.user, project__isnull=True, status__in=['todo', 'in_progress'])
    
    context = {
        'unassigned_tasks': unassigned_tasks,
    }
    return render(request, 'tasks/create_project_from_tasks.html', context)

@login_required
def task_mind_map(request):
    """Show task relationships as a mind map"""
    tasks = Task.objects.filter(user=request.user, status__in=['todo', 'in_progress'])
    
    # Build relationship graph
    task_graph = {}
    for task in tasks:
        task_graph[task.id] = {
            'task': task,
            'outgoing': [],
            'incoming': [],
        }
    
    # Add relationships
    relationships = TaskRelationship.objects.filter(
        from_task__in=tasks,
        to_task__in=tasks
    )
    
    for rel in relationships:
        if rel.from_task.id in task_graph:
            task_graph[rel.from_task.id]['outgoing'].append({
                'type': rel.relationship_type,
                'task': rel.to_task,
                'description': rel.description,
            })
        if rel.to_task.id in task_graph:
            task_graph[rel.to_task.id]['incoming'].append({
                'type': rel.relationship_type,
                'task': rel.from_task,
                'description': rel.description,
            })
    
    context = {
        'task_graph': task_graph,
        'tasks': tasks,
    }
    return render(request, 'tasks/task_mind_map.html', context)
