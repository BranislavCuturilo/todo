from django.contrib import admin
from .models import Project, Tag, Task, TaskRelationship, FocusSession, Event, TimeSlot, CalendarTask, UserPreferences

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
    inlines = [TaskRelationshipInline]

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'priority', 'created_at', 'updated_at']
    list_filter = ['created_at', 'priority']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(TaskRelationship)
class TaskRelationshipAdmin(admin.ModelAdmin):
    list_display = ['from_task', 'relationship_type', 'to_task', 'created_at']
    list_filter = ['relationship_type', 'created_at']
    search_fields = ['from_task__title', 'to_task__title']

@admin.register(FocusSession)
class FocusSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'task', 'kind', 'start_time', 'end_time', 'duration_minutes']
    list_filter = ['kind', 'start_time', 'end_time']
    search_fields = ['user__username', 'task__title']

# New calendar models
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_time', 'end_time', 'user', 'is_recurring']
    list_filter = ['is_recurring', 'start_time', 'user']
    search_fields = ['title', 'description']
    date_hierarchy = 'start_time'

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_time', 'end_time', 'days_of_week', 'user', 'is_active']
    list_filter = ['is_active', 'user']
    search_fields = ['name']

@admin.register(CalendarTask)
class CalendarTaskAdmin(admin.ModelAdmin):
    list_display = ['task', 'scheduled_start', 'scheduled_end', 'calendar_date', 'user']
    list_filter = ['calendar_date', 'user']
    search_fields = ['task__title']
    date_hierarchy = 'calendar_date'

@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ['user', 'work_start_time', 'work_end_time', 'daily_work_hours', 'updated_at']
    list_filter = ['daily_work_hours']
    search_fields = ['user__username', 'user__email']
