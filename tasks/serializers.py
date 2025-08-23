from rest_framework import serializers
from .models import Project, Tag, Task, FocusSession, TaskRelationship, Event, TimeSlot, CalendarTask


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all().order_by('priority', 'name'),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Task
        fields = '__all__'


class FocusSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FocusSession
        fields = '__all__'


class TaskRelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskRelationship
        fields = '__all__'

# New calendar serializers
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = '__all__'

class CalendarTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarTask
        fields = '__all__' 