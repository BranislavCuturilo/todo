from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('inbox/', views.list_inbox, name='inbox'),
    path('today/', views.list_today, name='today'),
    path('upcoming/', views.list_upcoming, name='upcoming'),
    path('done/', views.list_done, name='done'),

    path('projects/', views.project_list, name='project_list'),
    path('projects/new/', views.project_create, name='project_create'),
    path('projects/<slug:slug>/', views.project_detail, name='project_detail'),
    path('projects/<slug:slug>/edit/', views.project_edit, name='project_edit'),

    path('tasks/new/', views.task_create, name='task_create'),
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('tasks/<int:task_id>/edit/', views.task_edit, name='task_edit'),
    path('tasks/<int:task_id>/snooze/', views.snooze_task, name='snooze_task'),
    path('tasks/<int:task_id>/relationships/', views.task_relationships, name='task_relationships'),

    path('quick-add/', views.quick_add, name='quick_add'),
    path('focus/start/', views.focus_start, name='focus_start'),
    path('focus/end/', views.focus_end, name='focus_end'),

    # New features
    path('optimal-order/', views.optimal_task_order, name='optimal_task_order'),
    path('create-project-from-tasks/', views.create_project_from_tasks, name='create_project_from_tasks'),
    path('task-mind-map/', views.task_mind_map, name='task_mind_map'),

    path('api/', include('tasks.api_urls')),
] 