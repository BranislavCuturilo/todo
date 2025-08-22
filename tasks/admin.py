from django.contrib import admin
from .models import Task, Project, Tag, TaskDependency, Attachment, LinkAttachment, SavedFilter, FocusSession, TaskRelationship

class TaskDependencyInline(admin.TabularInline):
    model = TaskDependency
    fk_name = 'task'
    extra = 1

class TaskRelationshipInline(admin.TabularInline):
    model = TaskRelationship
    fk_name = 'from_task'
    extra = 1

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'priority', 'project', 'due_at', 'user']
    list_filter = ['status', 'priority', 'project', 'due_at', 'user']
    search_fields = ['title', 'description']
    date_hierarchy = 'created_at'
    inlines = [TaskDependencyInline, TaskRelationshipInline]

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'created_at']
    search_fields = ['name']

@admin.register(TaskDependency)
class TaskDependencyAdmin(admin.ModelAdmin):
    list_display = ['task', 'depends_on', 'created_at']
    list_filter = ['created_at']
    search_fields = ['task__title', 'depends_on__title']

@admin.register(TaskRelationship)
class TaskRelationshipAdmin(admin.ModelAdmin):
    list_display = ['from_task', 'relationship_type', 'to_task', 'created_at']
    list_filter = ['relationship_type', 'created_at']
    search_fields = ['from_task__title', 'to_task__title', 'description']

@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['filename', 'task', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['filename', 'task__title']

@admin.register(LinkAttachment)
class LinkAttachmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'task', 'url', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'url', 'task__title']

@admin.register(SavedFilter)
class SavedFilterAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'user__username']

@admin.register(FocusSession)
class FocusSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'task', 'kind', 'start_time', 'end_time', 'duration_minutes']
    list_filter = ['kind', 'start_time', 'end_time']
    search_fields = ['user__username', 'task__title']
