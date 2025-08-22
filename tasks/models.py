from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
import uuid

class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#0ea5e9')
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'slug': self.slug})

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#64748b')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Task(models.Model):
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('blocked', 'Blocked'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        (1, 'P1 - Critical'),
        (2, 'P2 - High'),
        (3, 'P3 - Medium'),
        (4, 'P4 - Low'),
        (5, 'P5 - Minimal'),
    ]
    
    REPEAT_CHOICES = [
        ('none', 'No Repeat'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=3)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    due_at = models.DateTimeField(null=True, blank=True)
    estimate_minutes = models.IntegerField(null=True, blank=True)
    repeat = models.CharField(max_length=20, choices=REPEAT_CHOICES, default='none')
    parent_task = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subtasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['priority', 'due_at', 'created_at']

    def __str__(self):
        return self.title

    @property
    def is_subtask(self):
        return self.parent_task is not None

    def mark_done(self):
        self.status = 'done'
        self.completed_at = timezone.now()
        self.save()

    def get_absolute_url(self):
        return reverse('task_detail', kwargs={'task_id': self.id})

class TaskRelationship(models.Model):
    RELATIONSHIP_TYPES = [
        ('blocks', 'Blocks'),
        ('depends_on', 'Depends On'),
        ('related_to', 'Related To'),
        ('duplicates', 'Duplicates'),
        ('subtask_of', 'Subtask Of'),
    ]

    from_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='outgoing_relationships')
    to_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='incoming_relationships')
    relationship_type = models.CharField(max_length=20, choices=RELATIONSHIP_TYPES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['from_task', 'to_task', 'relationship_type']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.from_task.title} {self.get_relationship_type_display()} {self.to_task.title}"

class TaskDependency(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='dependencies')
    depends_on = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='dependents')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['task', 'depends_on']
        verbose_name_plural = 'Task dependencies'

    def __str__(self):
        return f"{self.task.title} depends on {self.depends_on.title}"

class Attachment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename

class LinkAttachment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='link_attachments')
    url = models.URLField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class SavedFilter(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    filters = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class FocusSession(models.Model):
    KIND_CHOICES = [
        ('work', 'Work'),
        ('break', 'Break'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)
    kind = models.CharField(max_length=10, choices=KIND_CHOICES)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(null=True, blank=True)

    def end(self):
        self.end_time = timezone.now()
        if self.start_time and self.end_time:
            self.duration_minutes = int((self.end_time - self.start_time).total_seconds() / 60)
        self.save()

    def __str__(self):
        return f"{self.get_kind_display()} session - {self.start_time}"
