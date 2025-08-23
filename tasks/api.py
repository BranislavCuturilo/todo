from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Q

from .models import Project, Tag, Task, FocusSession, TaskRelationship, Event, TimeSlot, CalendarTask
from .serializers import (
    ProjectSerializer, TagSerializer, TaskSerializer, FocusSessionSerializer, 
    TaskRelationshipSerializer, EventSerializer, TimeSlotSerializer, CalendarTaskSerializer
)

class IsAuth(permissions.IsAuthenticated):
    pass

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuth]
    ordering_fields = ['name', 'created_at', 'priority']
    
    def get_queryset(self):
        return Project.objects.filter(user=self.request.user).order_by('priority', 'name')

class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    permission_classes = [IsAuth]
    
    def get_queryset(self):
        return Tag.objects.all()

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuth]
    ordering_fields = ['title', 'created_at', 'due_at', 'priority']
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

class FocusSessionViewSet(viewsets.ModelViewSet):
    serializer_class = FocusSessionSerializer
    permission_classes = [IsAuth]
    
    def get_queryset(self):
        return FocusSession.objects.filter(user=self.request.user)

class TaskRelationshipViewSet(viewsets.ModelViewSet):
    serializer_class = TaskRelationshipSerializer
    permission_classes = [IsAuth]
    
    def get_queryset(self):
        return TaskRelationship.objects.filter(from_task__user=self.request.user)

# New calendar viewsets
class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsAuth]
    
    def get_queryset(self):
        return Event.objects.filter(user=self.request.user)

class TimeSlotViewSet(viewsets.ModelViewSet):
    serializer_class = TimeSlotSerializer
    permission_classes = [IsAuth]
    
    def get_queryset(self):
        return TimeSlot.objects.filter(user=self.request.user)

class CalendarTaskViewSet(viewsets.ModelViewSet):
    serializer_class = CalendarTaskSerializer
    permission_classes = [IsAuth]
    
    def get_queryset(self):
        return CalendarTask.objects.filter(user=self.request.user)

# API Views
from rest_framework.views import APIView

class ShiftScheduleView(APIView):
    permission_classes = [IsAuth]
    
    def post(self, request):
        """Shift task schedule by specified minutes"""
        minutes = request.data.get('minutes', 30)
        task_id = request.data.get('task_id')
        
        try:
            task = Task.objects.get(id=task_id, user=request.user)
            if task.due_at:
                task.due_at += timedelta(minutes=int(minutes))
                task.save()
                return Response({'success': True})
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)

class TaskRelationshipView(APIView):
    permission_classes = [IsAuth]
    
    def post(self, request):
        """Create a new task relationship"""
        from_task_id = request.data.get('from_task_id')
        to_task_id = request.data.get('to_task_id')
        relationship_type = request.data.get('relationship_type')
        
        try:
            from_task = Task.objects.get(id=from_task_id, user=request.user)
            to_task = Task.objects.get(id=to_task_id, user=request.user)
            
            relationship, created = TaskRelationship.objects.get_or_create(
                from_task=from_task,
                to_task=to_task,
                relationship_type=relationship_type
            )
            
            return Response({
                'success': True,
                'created': created,
                'relationship_id': relationship.id
            })
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

class ProjectPriorityView(APIView):
    permission_classes = [IsAuth]

    def post(self, request):
        """Update project priorities via drag and drop reordering"""
        project_orders = request.data.get('project_orders', [])

        try:
            for order_data in project_orders:
                project_id = order_data.get('project_id')
                new_priority = order_data.get('priority')

                if project_id is not None and new_priority is not None:
                    project = Project.objects.get(id=project_id)
                    project.priority = new_priority
                    project.save()

            return Response({'success': True, 'message': 'Project priorities updated successfully'})
        except Project.DoesNotExist:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Router setup
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('projects', ProjectViewSet, basename='project')
router.register('tags', TagViewSet, basename='tag')
router.register('tasks', TaskViewSet, basename='task')
router.register('focus-sessions', FocusSessionViewSet, basename='focus-session')
router.register('task-relationships', TaskRelationshipViewSet, basename='task-relationship')
router.register('events', EventViewSet, basename='event')
router.register('time-slots', TimeSlotViewSet, basename='time-slot')
router.register('calendar-tasks', CalendarTaskViewSet, basename='calendar-task') 