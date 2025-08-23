from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Cache test page
    path('cache-test/', views.cache_test, name='cache_test'),
    
    # New main navigation
    path('all-tasks/', views.all_tasks, name='all_tasks'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('calendar/regenerate/', views.regenerate_calendar, name='regenerate_calendar'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/<int:event_id>/edit/', views.event_edit, name='event_edit'),
    path('events/<int:event_id>/delete/', views.event_delete, name='event_delete'),
    path('time-slots/create/', views.time_slot_create, name='time_slot_create'),
    path('time-slots/<int:time_slot_id>/delete/', views.time_slot_delete, name='time_slot_delete'),
    path('preferences/', views.user_preferences_edit, name='user_preferences_edit'),

    path('projects/', views.project_list, name='project_list'),
    path('projects/new/', views.project_create, name='project_create'),
    path('projects/<slug:slug>/', views.project_detail, name='project_detail'),
    path('projects/<slug:slug>/edit/', views.project_edit, name='project_edit'),
    path('projects/<slug:slug>/delete/', views.project_delete, name='project_delete'),

    path('tasks/new/', views.task_create, name='task_create'),
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('tasks/<int:task_id>/edit/', views.task_edit, name='task_edit'),
    path('tasks/<int:task_id>/delete/', views.task_delete, name='task_delete'),
    path('tasks/<int:task_id>/snooze/', views.snooze_task, name='snooze_task'),
    path('tasks/<int:task_id>/relationships/', views.task_relationships, name='task_relationships'),
    path('tasks/<int:task_id>/mark-done/', views.mark_task_done, name='mark_task_done'),
    path('tasks/<int:task_id>/mark-undone/', views.mark_task_undone, name='mark_task_undone'),

    path('quick-add/', views.quick_add, name='quick_add'),
    path('focus/start/', views.focus_start, name='focus_start'),
    path('focus/end/', views.focus_end, name='focus_end'),

    # New features
    path('optimal-order/', views.optimal_task_order, name='optimal_task_order'),
    path('create-project-from-tasks/', views.create_project_from_tasks, name='create_project_from_tasks'),
    path('task-mind-map/', views.task_mind_map, name='task_mind_map'),
    
    # Sketch functionality
    path('sketches/', views.sketch_list, name='sketch_list'),
    path('sketches/new/', views.sketch_create, name='sketch_create'),
    path('sketches/<int:sketch_id>/', views.sketch_detail, name='sketch_detail'),
    path('sketches/<int:sketch_id>/edit/', views.sketch_edit, name='sketch_edit'),
    path('sketches/<int:sketch_id>/delete/', views.sketch_delete, name='sketch_delete'),

    path('api/', include('tasks.api_urls')),
] 