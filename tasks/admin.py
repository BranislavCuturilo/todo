from django.contrib import admin
from .models import Task, Project, Tag, TaskRelationship, Event, TimeSlot, CalendarTask, UserPreferences, Sketch


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'status', 'priority', 'project', 'due_at', 'created_at']
    list_filter = ['status', 'priority', 'project', 'created_at']
    search_fields = ['title', 'description']
    date_hierarchy = 'created_at'
    list_per_page = 20


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'priority', 'created_at']
    list_filter = ['priority', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(TaskRelationship)
class TaskRelationshipAdmin(admin.ModelAdmin):
    list_display = ['from_task', 'to_task', 'relationship_type']
    list_filter = ['relationship_type']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'start_time', 'end_time', 'is_recurring', 'recurrence_type']
    list_filter = ['is_recurring', 'recurrence_type', 'start_time']
    search_fields = ['title', 'description']


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'start_time', 'end_time', 'is_active']
    list_filter = ['is_active', 'start_time']


@admin.register(CalendarTask)
class CalendarTaskAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'scheduled_start', 'scheduled_end', 'calendar_date']
    list_filter = ['calendar_date', 'scheduled_start']


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ['user', 'work_start_time', 'work_end_time', 'daily_work_hours']
    list_filter = ['daily_work_hours']


@admin.register(Sketch)
class SketchAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'project', 'task', 'created_at']
    list_filter = ['created_at', 'project', 'task']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'user')
        }),
        ('Assignment', {
            'fields': ('project', 'task'),
            'classes': ('collapse',)
        }),
        ('Image Data', {
            'fields': ('image_data',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
