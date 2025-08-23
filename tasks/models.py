from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from datetime import datetime, timedelta

class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    priority = models.IntegerField(default=0, help_text="Priority order for sorting (lower number = higher priority)")
    
    class Meta:
        ordering = ['priority', 'name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class Task(models.Model):
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('blocked', 'Blocked'),
        ('done', 'Done'),
    ]
    
    PRIORITY_CHOICES = [
        (1, 'P1 - Critical'),
        (2, 'P2 - High'),
        (3, 'P3 - Medium'),
        (4, 'P4 - Low'),
        (5, 'P5 - Minimal'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=3)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)
    due_at = models.DateTimeField(null=True, blank=True)
    estimate_minutes = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class TaskRelationship(models.Model):
    RELATIONSHIP_TYPES = [
        ('blocks', 'Blocks'),
        ('depends_on', 'Depends On'),
        ('subtask_of', 'Subtask Of'),
        ('related_to', 'Related To'),
    ]
    
    from_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='outgoing_relationships')
    to_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='incoming_relationships')
    relationship_type = models.CharField(max_length=20, choices=RELATIONSHIP_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['from_task', 'to_task', 'relationship_type']
    
    def __str__(self):
        return f"{self.from_task} {self.get_relationship_type_display()} {self.to_task}"

class FocusSession(models.Model):
    KIND_CHOICES = [
        ('work', 'Work'),
        ('break', 'Break'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)
    kind = models.CharField(max_length=10, choices=KIND_CHOICES, default='work')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    
    @property
    def duration_minutes(self):
        if self.end_time:
            return int((self.end_time - self.start_time).total_seconds() / 60)
        return int((timezone.now() - self.start_time).total_seconds() / 60)
    
    def end(self):
        self.end_time = timezone.now()
        self.save()
    
    def __str__(self):
        return f"{self.user.username} - {self.kind} session"

# New models for calendar functionality

class Event(models.Model):
    """Model for calendar events like meetings"""
    RECURRENCE_CHOICES = [
        ('none', 'No Recurrence'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('custom', 'Custom'),
    ]
    
    WEEKDAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # New recurring event fields
    is_recurring = models.BooleanField(default=False)
    recurrence_type = models.CharField(max_length=20, choices=RECURRENCE_CHOICES, default='none')
    recurrence_interval = models.IntegerField(default=1, help_text="Every X days/weeks/months/years")
    weekdays = models.JSONField(default=list, help_text="List of weekdays for weekly recurrence (0=Monday, 6=Sunday)")
    end_date = models.DateField(null=True, blank=True, help_text="End date for recurring events")
    max_occurrences = models.IntegerField(null=True, blank=True, help_text="Maximum number of occurrences")
    
    # Legacy field for backward compatibility
    recurrence_pattern = models.CharField(max_length=100, blank=True, help_text="Cron-like pattern for recurring events")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} ({self.start_time.strftime('%Y-%m-%d %H:%M')})"
    
    def get_recurring_events(self, start_date, end_date):
        """Generate recurring event instances for a date range"""
        if not self.is_recurring or self.recurrence_type == 'none':
            return [self]
        
        events = []
        current_date = self.start_time.date()
        current_time = self.start_time.time()
        end_time = self.end_time.time()
        occurrence_count = 0
        
        # Calculate the maximum date to check (either end_date or end_date parameter)
        max_date = end_date
        if self.end_date:
            max_date = min(end_date, self.end_date)
        
        # For weekly events, we need to track weeks
        week_count = 0
        current_week_start = current_date - timedelta(days=current_date.weekday())
        
        while current_date <= max_date:
            # Check if we've reached max occurrences
            if self.max_occurrences and occurrence_count >= self.max_occurrences:
                break
            
            # Check if this date should have an event based on recurrence rules
            should_create = False
            
            if self.recurrence_type == 'daily':
                should_create = True
            elif self.recurrence_type == 'weekly':
                weekday = current_date.weekday()
                # Only create if it's a selected weekday and we're in the right week interval
                if weekday in self.weekdays and week_count % self.recurrence_interval == 0:
                    should_create = True
            elif self.recurrence_type == 'monthly':
                # Same day of month
                should_create = current_date.day == self.start_time.day
            elif self.recurrence_type == 'yearly':
                # Same day and month
                should_create = (current_date.day == self.start_time.day and 
                               current_date.month == self.start_time.month)
            
            if should_create and current_date >= start_date:
                # Create event instance with timezone-aware datetimes
                event_start = timezone.make_aware(datetime.combine(current_date, current_time))
                event_end = timezone.make_aware(datetime.combine(current_date, end_time))
                
                events.append({
                    'title': self.title,
                    'description': self.description,
                    'start_time': event_start,
                    'end_time': event_end,
                    'is_recurring_instance': True,
                    'original_event': self,
                })
                occurrence_count += 1
            
            # Move to next occurrence based on recurrence type and interval
            if self.recurrence_type == 'daily':
                current_date += timedelta(days=self.recurrence_interval)
            elif self.recurrence_type == 'weekly':
                # For weekly, move to next day
                current_date += timedelta(days=1)
                
                # Check if we've moved to a new week
                new_week_start = current_date - timedelta(days=current_date.weekday())
                if new_week_start > current_week_start:
                    week_count += 1
                    current_week_start = new_week_start
            elif self.recurrence_type == 'monthly':
                # Move to next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
            elif self.recurrence_type == 'yearly':
                current_date = current_date.replace(year=current_date.year + self.recurrence_interval)
        
        return events

class TimeSlot(models.Model):
    """Model for time slots when user is not available (breaks, etc.)"""
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    name = models.CharField(max_length=100, help_text="e.g., Lunch Break, Coffee Break")
    start_time = models.TimeField(help_text="Start time (e.g., 12:00)")
    end_time = models.TimeField(help_text="End time (e.g., 13:00)")
    days_of_week = models.JSONField(default=list, help_text="List of days (0=Monday, 6=Sunday)")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"

class CalendarTask(models.Model):
    """Model for task scheduling in calendar (doesn't modify original task)"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()
    calendar_date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['task', 'calendar_date']
    
    def __str__(self):
        return f"{self.task.title} on {self.calendar_date} ({self.scheduled_start.strftime('%H:%M')}-{self.scheduled_end.strftime('%H:%M')})"

class UserPreferences(models.Model):
    """Model for user preferences including working hours"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    work_start_time = models.TimeField(default='09:00', help_text="Start of working hours")
    work_end_time = models.TimeField(default='17:00', help_text="End of working hours")
    daily_work_hours = models.IntegerField(default=6, help_text="Maximum hours to work per day")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} preferences"
    
    @classmethod
    def get_or_create_for_user(cls, user):
        """Get user preferences or create default ones"""
        preferences, created = cls.objects.get_or_create(
            user=user,
            defaults={
                'work_start_time': '09:00',
                'work_end_time': '17:00',
                'daily_work_hours': 6,
            }
        )
        return preferences

class Sketch(models.Model):
    """Model for storing sketches/drawings"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image_data = models.TextField(help_text="Base64 encoded image data")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} by {self.user.username}"
    
    class Meta:
        ordering = ['-created_at']
