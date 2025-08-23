from django.urls import path, include
from .api import router, ShiftScheduleView, TaskRelationshipView, ProjectPriorityView

urlpatterns = [
    path('', include(router.urls)),
    path('schedule/shift/', ShiftScheduleView.as_view(), name='api_schedule_shift'),
    path('task-relationships/', TaskRelationshipView.as_view(), name='api_task_relationships'),
    path('project-priorities/', ProjectPriorityView.as_view(), name='api_project_priorities'),
] 