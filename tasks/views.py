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
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.views.generic import FormView
from django.urls import reverse_lazy

from .models import Task, Project, Tag, TaskRelationship, FocusSession, Event, TimeSlot, CalendarTask, UserPreferences, Sketch
from .forms import TaskForm, ProjectForm, TaskRelationshipForm, EventForm, TimeSlotForm, UserPreferencesForm, SketchForm
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

def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to TODO, {user.username}! Your account has been created successfully.')
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    
    return render(request, 'auth/register.html', {'form': form})

@login_required
def cache_test(request):
    """Cache test page to help debug cache issues"""
    return render(request, 'cache_test.html')

@login_required
def dashboard(request):
    # Get filter parameters
    priority_filter = request.GET.get('priority')
    project_filter = request.GET.get('project')
    status_filter = request.GET.get('status')
    
    # Base querysets
    overdue = Task.objects.filter(
        user=request.user, 
        due_at__lt=timezone.now(), 
        status__in=['todo', 'in_progress']
    )
    
    scheduled = Task.objects.filter(
        user=request.user,
        due_at__isnull=False,
        due_at__gte=timezone.now(),
        status__in=['todo', 'in_progress']
    )
    
    not_scheduled = Task.objects.filter(
        user=request.user,
        due_at__isnull=True,
        status__in=['todo', 'in_progress']
    )
    
    # Apply filters
    if priority_filter:
        overdue = overdue.filter(priority=priority_filter)
        scheduled = scheduled.filter(priority=priority_filter)
        not_scheduled = not_scheduled.filter(priority=priority_filter)
    
    if project_filter:
        overdue = overdue.filter(project_id=project_filter)
        scheduled = scheduled.filter(project_id=project_filter)
        not_scheduled = not_scheduled.filter(project_id=project_filter)
    
    if status_filter:
        overdue = overdue.filter(status=status_filter)
        scheduled = scheduled.filter(status=status_filter)
        not_scheduled = not_scheduled.filter(status=status_filter)
    
    # Sort overdue by priority and due date
    overdue = overdue.order_by('priority', 'due_at')
    
    # Sort scheduled by date, then priority, then time (optimized for 4 hours daily)
    scheduled = scheduled.order_by('due_at__date', 'priority', 'due_at__time')
    
    # Calculate scores for not scheduled tasks
    for task in not_scheduled:
        # Base score starts with priority (lower number = higher priority)
        score = task.priority * 10
        
        # Add project priority (lower number = higher priority)
        if task.project:
            score += task.project.priority * 100
        else:
            score += 1000  # No project gets lowest priority
        
        # Add duration factor (shorter tasks get higher priority)
        if task.estimate_minutes:
            score += min(task.estimate_minutes // 30, 10)  # Max 10 points for duration
        else:
            score += 5  # Default duration score
        
        task.optimization_score = score
    
    # Sort not scheduled by optimization score
    not_scheduled = sorted(not_scheduled, key=lambda x: x.optimization_score)
    
    # Optimize scheduled tasks for 4 hours daily (240 minutes)
    optimized_scheduled = []
    daily_minutes = 240
    current_date = None
    current_daily_minutes = 0
    
    for task in scheduled:
        task_date = task.due_at.date()
        
        # Reset daily minutes for new date
        if current_date != task_date:
            current_date = task_date
            current_daily_minutes = 0
        
        # Check if task fits in daily schedule
        task_minutes = task.estimate_minutes or 60  # Default 1 hour if not estimated
        
        if current_daily_minutes + task_minutes <= daily_minutes:
            optimized_scheduled.append(task)
            current_daily_minutes += task_minutes
        else:
            # Task doesn't fit, add to not scheduled
            task.due_at = None
            not_scheduled.append(task)
    
    # Re-sort not scheduled after adding overflow tasks
    for task in not_scheduled:
        if not hasattr(task, 'optimization_score'):
            score = task.priority * 10
            if task.project:
                score += task.project.priority * 100
            else:
                score += 1000
            if task.estimate_minutes:
                score += min(task.estimate_minutes // 30, 10)
            else:
                score += 5
            task.optimization_score = score
    
    not_scheduled = sorted(not_scheduled, key=lambda x: x.optimization_score)
    
    projects = Project.objects.filter(user=request.user).order_by('priority', 'name')
    
    current_filters = {
        'priority': priority_filter,
        'project': project_filter,
        'status': status_filter,
    }
    
    context = {
        'overdue': overdue,
        'scheduled': optimized_scheduled,
        'not_scheduled': not_scheduled,
        'projects': projects,
        'current_filters': current_filters,
        'now': timezone.now(),
    }
    return render(request, 'tasks/dashboard.html', context)

@login_required
def all_tasks(request):
    """View all tasks grouped by projects with filters"""
    # Get filter parameters
    priority_filter = request.GET.get('priority')
    project_filter = request.GET.get('project')
    status_filter = request.GET.get('status')
    
    # Base queryset
    tasks = Task.objects.filter(user=request.user)
    
    # Apply filters
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    if project_filter:
        tasks = tasks.filter(project_id=project_filter)
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    # Group tasks by project
    projects = Project.objects.filter(user=request.user).order_by('priority', 'name')
    tasks_by_project = {}
    
    for project in projects:
        project_tasks = tasks.filter(project=project).order_by('priority', 'due_at', 'created_at')
        if project_tasks.exists():
            tasks_by_project[project] = project_tasks
    
    # Handle tasks without project
    no_project_tasks = tasks.filter(project__isnull=True).order_by('priority', 'due_at', 'created_at')
    if no_project_tasks.exists():
        tasks_by_project[None] = no_project_tasks
    
    current_filters = {
        'priority': priority_filter,
        'project': project_filter,
        'status': status_filter,
    }
    
    context = {
        'tasks_by_project': tasks_by_project,
        'projects': projects,
        'current_filters': current_filters,
        'now': timezone.now(),
    }
    return render(request, 'tasks/all_tasks.html', context)

@login_required
def calendar_view(request):
    """Calendar view with events and scheduled tasks"""
    # Get week navigation parameters
    week_offset = request.GET.get('week', 0)
    try:
        week_offset = int(week_offset)
    except ValueError:
        week_offset = 0
    
    # Get current week with offset
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    end_of_week = start_of_week + timedelta(days=6)
    
    # Pre-calculate week dates
    week_dates = []
    for i in range(7):
        week_dates.append(start_of_week + timedelta(days=i))
    
    # Pre-calculate all 24 hours
    hours = list(range(24))  # 0:00 to 23:00
    
    # Get user preferences
    user_preferences = UserPreferences.get_or_create_for_user(request.user)
    
    # Get all events for the week (including recurring events)
    all_events = []
    
    # Get regular events
    regular_events = Event.objects.filter(
        user=request.user,
        start_time__date__gte=start_of_week,
        start_time__date__lte=end_of_week
    ).order_by('start_time')
    
    for event in regular_events:
        all_events.append({
            'title': event.title,
            'description': event.description,
            'start_time': event.start_time,
            'end_time': event.end_time,
            'is_recurring_instance': False,
            'original_event': event,
        })
    
    # Get recurring events and generate instances
    recurring_events = Event.objects.filter(
        user=request.user,
        is_recurring=True
    ).order_by('start_time')
    
    for event in recurring_events:
        recurring_instances = event.get_recurring_events(start_of_week, end_of_week)
        all_events.extend(recurring_instances)
    
    # Ensure all events have timezone-aware datetimes before sorting
    for event in all_events:
        if timezone.is_naive(event['start_time']):
            event['start_time'] = timezone.make_aware(event['start_time'])
        if timezone.is_naive(event['end_time']):
            event['end_time'] = timezone.make_aware(event['end_time'])
    
    # Sort all events by start time
    all_events.sort(key=lambda x: x['start_time'])
    
    # Get time slots
    time_slots = TimeSlot.objects.filter(user=request.user, is_active=True)
    
    # Get scheduled tasks
    calendar_tasks = CalendarTask.objects.filter(
        user=request.user,
        calendar_date__gte=start_of_week,
        calendar_date__lte=end_of_week
    ).order_by('scheduled_start')
    
    # Get all available tasks for scheduling
    available_tasks = Task.objects.filter(
        user=request.user,
        status__in=['todo', 'in_progress']
    ).order_by('priority', 'due_at')
    
    context = {
        'events': all_events,
        'time_slots': time_slots,
        'calendar_tasks': calendar_tasks,
        'available_tasks': available_tasks,
        'start_of_week': start_of_week,
        'end_of_week': end_of_week,
        'today': today,
        'week_dates': week_dates,
        'hours': hours,
        'user_preferences': user_preferences,
        'projects': Project.objects.filter(user=request.user).order_by('priority', 'name'),
        'week_offset': week_offset,
    }
    return render(request, 'tasks/calendar.html', context)

@login_required
def regenerate_calendar(request):
    """Regenerate calendar schedule for tasks"""
    if request.method == 'POST':
        # Clear existing calendar tasks
        CalendarTask.objects.filter(user=request.user).delete()
        
        # Get user preferences
        user_preferences = UserPreferences.get_or_create_for_user(request.user)
        work_start = user_preferences.work_start_time
        work_end = user_preferences.work_end_time
        daily_hours = user_preferences.daily_work_hours
        
        # Get all tasks that need scheduling (ignore due dates, use only priority)
        tasks = Task.objects.filter(
            user=request.user,
            status__in=['todo', 'in_progress']
        ).order_by('priority')  # Only by priority, not by due_at
        
        # Get time slots when user is not available
        time_slots = TimeSlot.objects.filter(user=request.user, is_active=True)
        
        # Get events
        events = Event.objects.filter(user=request.user)
        
        # Start scheduling from today
        current_date = timezone.now().date()
        current_time = work_start
        
        for task in tasks:
            # Calculate task duration
            task_duration = task.estimate_minutes or 60  # Default 1 hour
            
            # Find available time slot
            scheduled = False
            attempts = 0
            
            while not scheduled and attempts < 30:  # Try for 30 days
                # Check if current time is within working hours
                if current_time >= work_start and current_time < work_end:
                    # Check if time conflicts with events
                    conflicts_with_events = events.filter(
                        start_time__date=current_date,
                        start_time__time__lte=current_time,
                        end_time__time__gt=current_time
                    ).exists()
                    
                    # Check if time conflicts with time slots (fixed for SQLite)
                    current_weekday = current_date.weekday()
                    conflicts_with_slots = False
                    for time_slot in time_slots:
                        if (current_weekday in time_slot.days_of_week and 
                            time_slot.start_time <= current_time and 
                            time_slot.end_time > current_time):
                            conflicts_with_slots = True
                            break
                    
                    if not conflicts_with_events and not conflicts_with_slots:
                        # Schedule the task
                        end_time = datetime.combine(current_date, current_time) + timedelta(minutes=task_duration)
                        
                        CalendarTask.objects.create(
                            task=task,
                            scheduled_start=datetime.combine(current_date, current_time),
                            scheduled_end=end_time,
                            calendar_date=current_date,
                            user=request.user
                        )
                        
                        # Move to next time slot
                        current_time = end_time.time()
                        if current_time >= work_end:
                            current_date += timedelta(days=1)
                            current_time = work_start
                        
                        scheduled = True
                        break
                
                # Move to next time slot
                current_time = (datetime.combine(current_date, current_time) + timedelta(minutes=30)).time()
                if current_time >= work_end:
                    current_date += timedelta(days=1)
                    current_time = work_start
                
                attempts += 1
            
            if not scheduled:
                # If couldn't schedule, add to end of day
                CalendarTask.objects.create(
                    task=task,
                    scheduled_start=datetime.combine(current_date, work_end) - timedelta(hours=1),
                    scheduled_end=datetime.combine(current_date, work_end),
                    calendar_date=current_date,
                    user=request.user
                )
        
        messages.success(request, 'Calendar regenerated successfully!')
        return redirect('calendar')
    
    return redirect('calendar')

@login_required
def event_create(request):
    """Create a new event"""
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            
            # Handle recurring event fields
            if form.cleaned_data.get('is_recurring'):
                # Convert weekdays to integers if provided
                weekdays = form.cleaned_data.get('weekdays', [])
                if weekdays:
                    event.weekdays = [int(day) for day in weekdays]
                else:
                    event.weekdays = []
            else:
                # Reset recurring fields if not recurring
                event.recurrence_type = 'none'
                event.recurrence_interval = 1
                event.weekdays = []
                event.end_date = None
                event.max_occurrences = None
            
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('calendar')
    else:
        form = EventForm()
    
    return render(request, 'tasks/event_form.html', {
        'form': form,
        'title': 'Create Event',
        'projects': Project.objects.filter(user=request.user).order_by('priority', 'name')
    })

@login_required
def event_edit(request, event_id):
    """Edit an existing event"""
    event = get_object_or_404(Event, id=event_id, user=request.user)
    
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            event = form.save(commit=False)
            
            # Handle recurring event fields
            if form.cleaned_data.get('is_recurring'):
                # Convert weekdays to integers if provided
                weekdays = form.cleaned_data.get('weekdays', [])
                if weekdays:
                    event.weekdays = [int(day) for day in weekdays]
                else:
                    event.weekdays = []
            else:
                # Reset recurring fields if not recurring
                event.recurrence_type = 'none'
                event.recurrence_interval = 1
                event.weekdays = []
                event.end_date = None
                event.max_occurrences = None
            
            event.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('calendar')
    else:
        form = EventForm(instance=event)
    
    return render(request, 'tasks/event_form.html', {
        'form': form,
        'title': 'Edit Event',
        'event': event,
        'projects': Project.objects.filter(user=request.user).order_by('priority', 'name')
    })

@login_required
def time_slot_create(request):
    """Create a new time slot"""
    if request.method == 'POST':
        form = TimeSlotForm(request.POST)
        if form.is_valid():
            time_slot = form.save(commit=False)
            time_slot.user = request.user
            # Convert string values to integers for days_of_week
            days_of_week = form.cleaned_data.get('days_of_week', [])
            time_slot.days_of_week = [int(day) for day in days_of_week]
            time_slot.save()
            messages.success(request, 'Time slot created successfully!')
            return redirect('calendar')
    else:
        form = TimeSlotForm()
    
    return render(request, 'tasks/time_slot_form.html', {'form': form})

@login_required
def user_preferences_edit(request):
    """Edit user preferences including working hours"""
    user_preferences = UserPreferences.get_or_create_for_user(request.user)
    
    if request.method == 'POST':
        form = UserPreferencesForm(request.POST, instance=user_preferences)
        if form.is_valid():
            form.save()
            messages.success(request, 'Preferences updated successfully!')
            return redirect('calendar')
    else:
        form = UserPreferencesForm(instance=user_preferences)
    
    return render(request, 'tasks/user_preferences_form.html', {'form': form})

@login_required
def list_inbox(request):
    tasks = Task.objects.filter(user=request.user, project__isnull=True, status__in=['todo', 'in_progress'])
    return render(request, 'tasks/list.html', {
        'tasks': tasks, 
        'title': 'Inbox', 
        'projects': Project.objects.filter(user=request.user).order_by('priority', 'name'),
        'now': timezone.now()
    })

@login_required
def list_today(request):
    tasks = Task.objects.filter(user=request.user, due_at__date=timezone.now().date())
    return render(request, 'tasks/list.html', {
        'tasks': tasks, 
        'title': 'Today', 
        'projects': Project.objects.filter(user=request.user).order_by('priority', 'name'),
        'now': timezone.now()
    })

@login_required
def list_upcoming(request):
    tasks = Task.objects.filter(user=request.user, due_at__gt=timezone.now(), status__in=['todo', 'in_progress'])
    return render(request, 'tasks/list.html', {
        'tasks': tasks, 
        'title': 'Upcoming', 
        'projects': Project.objects.filter(user=request.user).order_by('priority', 'name'),
        'now': timezone.now()
    })

@login_required
def list_done(request):
    tasks = Task.objects.filter(user=request.user, status='done')
    return render(request, 'tasks/list.html', {
        'tasks': tasks, 
        'title': 'Done', 
        'projects': Project.objects.filter(user=request.user).order_by('priority', 'name'),
        'now': timezone.now()
    })

@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    # Handle POST actions
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'done':
            task.status = 'done'
            task.save()
            messages.success(request, f'Task "{task.title}" marked as done!')
            return redirect('task_detail', task_id=task.id)
        elif action == 'undo_done':
            task.status = 'todo'
            task.save()
            messages.success(request, f'Task "{task.title}" marked as todo!')
            return redirect('task_detail', task_id=task.id)
    
    relationships = TaskRelationship.objects.filter(from_task=task)
    incoming_relationships = TaskRelationship.objects.filter(to_task=task)
    
    context = {
        'task': task,
        'relationships': relationships,
        'incoming_relationships': incoming_relationships,
        'projects': Project.objects.filter(user=request.user).order_by('priority', 'name'),
        'now': timezone.now(),
    }
    return render(request, 'tasks/task_detail.html', context)

@login_required
def project_list(request):
    projects = Project.objects.filter(user=request.user).order_by('priority', 'name')
    return render(request, 'tasks/projects.html', {'projects': projects, 'now': timezone.now()})

@login_required
def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug, user=request.user)
    status_filter = request.GET.get('status', 'all')
    
    if status_filter == 'all':
        tasks = Task.objects.filter(project=project, user=request.user)
    else:
        tasks = Task.objects.filter(project=project, user=request.user, status=status_filter)
    
    context = {
        'project': project,
        'tasks': tasks,
        'status_filter': status_filter,
        'projects': Project.objects.filter(user=request.user).order_by('priority', 'name'),
        'now': timezone.now(),
    }
    return render(request, 'tasks/project_detail.html', context)

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
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
        form = TaskForm(initial=initial, user=request.user)
    
    return render(request, 'tasks/task_form.html', {
        'form': form, 
        'title': 'Create Task',
        'projects': Project.objects.filter(user=request.user).order_by('priority', 'name')
    })

@login_required
def task_edit(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('task_detail', task_id=task.id)
    else:
        form = TaskForm(instance=task, user=request.user)
    
    return render(request, 'tasks/task_form.html', {
        'form': form, 
        'title': 'Edit Task',
        'projects': Project.objects.filter(user=request.user).order_by('priority', 'name')
    })

@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.slug = slugify(project.name)
            project.save()
            messages.success(request, 'Project created successfully!')
            return redirect('project_detail', slug=project.slug)
    else:
        form = ProjectForm()
    
    return render(request, 'tasks/project_form.html', {
        'form': form, 
        'title': 'Create Project',
        'projects': Project.objects.filter(user=request.user).order_by('priority', 'name')
    })

@login_required
def project_edit(request, slug):
    project = get_object_or_404(Project, slug=slug, user=request.user)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('project_detail', slug=project.slug)
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'tasks/project_form.html', {
        'form': form, 
        'title': 'Edit Project',
        'projects': Project.objects.filter(user=request.user).order_by('priority', 'name')
    })

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
        'projects': Project.objects.filter(user=request.user).order_by('priority', 'name'),
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
        'projects': Project.objects.filter(user=request.user).order_by('priority', 'name'),
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
        'projects': Project.objects.filter(user=request.user).order_by('priority', 'name'),
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
    
    # Store actual relationship instances so templates can use display helpers
    for rel in relationships:
        if rel.from_task.id in task_graph:
            task_graph[rel.from_task.id]['outgoing'].append(rel)
        if rel.to_task.id in task_graph:
            task_graph[rel.to_task.id]['incoming'].append(rel)
    
    context = {
        'task_graph': task_graph,
        'tasks': tasks,
        'projects': Project.objects.filter(user=request.user).order_by('priority', 'name'),
    }
    return render(request, 'tasks/task_mind_map.html', context)

@login_required
def event_delete(request, event_id):
    """Delete an event"""
    event = get_object_or_404(Event, id=event_id, user=request.user)
    
    if request.method == 'POST':
        delete_type = request.POST.get('delete_type', 'single')
        
        if delete_type == 'single':
            # Delete only this occurrence
            event.delete()
            messages.success(request, 'Event deleted successfully!')
        elif delete_type == 'future':
            # Delete this and all future occurrences
            Event.objects.filter(
                user=request.user,
                title=event.title,
                start_time__gte=event.start_time
            ).delete()
            messages.success(request, 'Event and all future occurrences deleted!')
        elif delete_type == 'all':
            # Delete all occurrences of this recurring event
            Event.objects.filter(
                user=request.user,
                title=event.title
            ).delete()
            messages.success(request, 'All occurrences of this event deleted!')
        
        return redirect('calendar')
    
    return render(request, 'tasks/event_delete_confirm.html', {
        'event': event,
        'projects': Project.objects.filter(user=request.user).order_by('priority', 'name')
    })

@login_required
def time_slot_delete(request, time_slot_id):
    """Delete a time slot"""
    time_slot = get_object_or_404(TimeSlot, id=time_slot_id, user=request.user)
    
    if request.method == 'POST':
        time_slot.delete()
        messages.success(request, 'Time slot deleted successfully!')
        return redirect('calendar')
    
    return render(request, 'tasks/time_slot_delete_confirm.html', {
        'time_slot': time_slot,
        'projects': Project.objects.filter(user=request.user).order_by('priority', 'name')
    })

@login_required
def sketch_list(request):
    """List all sketches"""
    sketches = Sketch.objects.filter(user=request.user)
    
    # Filter by project if specified
    project_id = request.GET.get('project')
    if project_id:
        sketches = sketches.filter(project_id=project_id)
    
    # Filter by task if specified
    task_id = request.GET.get('task')
    if task_id:
        sketches = sketches.filter(task_id=task_id)
    
    context = {
        'sketches': sketches,
        'projects': Project.objects.filter(user=request.user).order_by('priority', 'name'),
        'tasks': Task.objects.filter(user=request.user, status__in=['todo', 'in_progress']).order_by('priority', 'due_at'),
    }
    return render(request, 'tasks/sketch_list.html', context)

@login_required
def sketch_create(request):
    """Create a new sketch"""
    if request.method == 'POST':
        form = SketchForm(request.POST, user=request.user)
        if form.is_valid():
            sketch = form.save(commit=False)
            sketch.user = request.user
            sketch.image_data = request.POST.get('image_data', '')
            sketch.save()
            messages.success(request, 'Sketch created successfully!')
            return redirect('sketch_list')
    else:
        form = SketchForm(user=request.user)
        # Pre-populate task if task_id is provided in URL
        task_id = request.GET.get('task')
        if task_id:
            try:
                task = Task.objects.get(id=task_id, user=request.user)
                form.fields['task'].initial = task
            except Task.DoesNotExist:
                pass
        
        # Pre-populate project if project_id is provided in URL
        project_id = request.GET.get('project')
        if project_id:
            try:
                project = Project.objects.get(id=project_id)
                form.fields['project'].initial = project
            except Project.DoesNotExist:
                pass
    
    return render(request, 'tasks/sketch_form.html', {
        'form': form,
        'title': 'Create Sketch',
        'projects': Project.objects.filter(user=request.user).order_by('priority', 'name'),
        'tasks': Task.objects.filter(user=request.user, status__in=['todo', 'in_progress']).order_by('priority', 'due_at'),
    })

@login_required
def sketch_detail(request, sketch_id):
    """View sketch details"""
    sketch = get_object_or_404(Sketch, id=sketch_id, user=request.user)
    
    return render(request, 'tasks/sketch_detail.html', {
        'sketch': sketch,
        'projects': Project.objects.filter(user=request.user).order_by('priority', 'name'),
    })

@login_required
def sketch_edit(request, sketch_id):
    """Edit a sketch"""
    sketch = get_object_or_404(Sketch, id=sketch_id, user=request.user)
    
    if request.method == 'POST':
        form = SketchForm(request.POST, instance=sketch, user=request.user)
        if form.is_valid():
            sketch = form.save(commit=False)
            # Update image data if provided
            new_image_data = request.POST.get('image_data')
            if new_image_data:
                sketch.image_data = new_image_data
            sketch.save()
            messages.success(request, 'Sketch updated successfully!')
            return redirect('sketch_detail', sketch_id=sketch.id)
    else:
        form = SketchForm(instance=sketch, user=request.user)
    
    return render(request, 'tasks/sketch_form.html', {
        'form': form,
        'sketch': sketch,
        'title': 'Edit Sketch',
        'projects': Project.objects.filter(user=request.user).order_by('priority', 'name'),
        'tasks': Task.objects.filter(user=request.user, status__in=['todo', 'in_progress']).order_by('priority', 'due_at'),
    })

@login_required
def sketch_delete(request, sketch_id):
    """Delete a sketch"""
    sketch = get_object_or_404(Sketch, id=sketch_id, user=request.user)
    
    if request.method == 'POST':
        sketch.delete()
        messages.success(request, 'Sketch deleted successfully!')
        return redirect('sketch_list')
    
    return render(request, 'tasks/sketch_delete_confirm.html', {
        'sketch': sketch,
        'projects': Project.objects.filter(user=request.user).order_by('priority', 'name'),
    })

@login_required
def project_delete(request, slug):
    """Delete a project"""
    project = get_object_or_404(Project, slug=slug, user=request.user)
    
    if request.method == 'POST':
        project_name = project.name
        project.delete()
        messages.success(request, f'Project "{project_name}" deleted successfully!')
        return redirect('project_list')
    
    # Count related objects for confirmation
    task_count = project.task_set.count()
    sketch_count = project.sketch_set.count()
    
    return render(request, 'tasks/project_delete_confirm.html', {
        'project': project,
        'task_count': task_count,
        'sketch_count': sketch_count,
    })

@login_required
def task_delete(request, task_id):
    """Delete a task"""
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    if request.method == 'POST':
        task_title = task.title
        task.delete()
        messages.success(request, f'Task "{task_title}" deleted successfully!')
        return redirect('all_tasks')
    
    # Count related objects for confirmation
    sketch_count = task.sketch_set.count()
    relationship_count = TaskRelationship.objects.filter(
        Q(from_task=task) | Q(to_task=task)
    ).count()
    
    return render(request, 'tasks/task_delete_confirm.html', {
        'task': task,
        'sketch_count': sketch_count,
        'relationship_count': relationship_count,
    })

@login_required
def mark_task_done(request, task_id):
    """Mark a task as done via AJAX"""
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id, user=request.user)
        task.status = 'done'
        task.save()
        return JsonResponse({
            'success': True,
            'message': f'Task "{task.title}" marked as done!',
            'task_id': task.id,
            'status': 'done'
        })
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def mark_task_undone(request, task_id):
    """Mark a task as undone via AJAX"""
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id, user=request.user)
        task.status = 'todo'
        task.save()
        return JsonResponse({
            'success': True,
            'message': f'Task "{task.title}" marked as todo!',
            'task_id': task.id,
            'status': 'todo'
        })
    return JsonResponse({'success': False, 'message': 'Invalid request method'})
