from django.utils import timezone
from rest_framework import viewsets, permissions, decorators, response, status
from rest_framework.views import APIView
from rest_framework.routers import DefaultRouter

from .models import Project, Tag, Task, FocusSession, SavedFilter
from .serializers import ProjectSerializer, TagSerializer, TaskSerializer, FocusSessionSerializer, SavedFilterSerializer
from .utils import parse_quick_add
from .scheduling import shift_due_dates


class IsAuth(permissions.IsAuthenticated):
    pass


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuth]
    lookup_field = 'slug'
    filterset_fields = ['is_archived']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuth]
    lookup_field = 'slug'
    search_fields = ['name']
    ordering_fields = ['name']


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuth]
    filterset_fields = ['status', 'priority', 'project', 'tags']
    search_fields = ['title', 'description_md']
    ordering_fields = ['priority', 'due_at', 'start_at', 'created_at']

    @decorators.action(detail=False, methods=['post'], url_path='quick-add')
    def quick_add(self, request):
        text = request.data.get('text', '')
        task = parse_quick_add(text)
        return response.Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)


class FocusSessionViewSet(viewsets.ModelViewSet):
    serializer_class = FocusSessionSerializer
    permission_classes = [IsAuth]

    def get_queryset(self):
        return FocusSession.objects.filter(owner=self.request.user).order_by('-started_at')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class SavedFilterViewSet(viewsets.ModelViewSet):
    serializer_class = SavedFilterSerializer
    permission_classes = [IsAuth]

    def get_queryset(self):
        return SavedFilter.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ShiftScheduleView(APIView):
    permission_classes = [IsAuth]

    def post(self, request):
        minutes = int(request.data.get('minutes', 0))
        scope = request.data.get('scope', 'today')
        num = shift_due_dates(minutes=minutes, scope=scope)
        return response.Response({'shifted': num})


router = DefaultRouter()
router.register('projects', ProjectViewSet)
router.register('tags', TagViewSet)
router.register('tasks', TaskViewSet)
router.register('focus-sessions', FocusSessionViewSet, basename='focus-session')
router.register('saved-filters', SavedFilterViewSet, basename='saved-filter') 