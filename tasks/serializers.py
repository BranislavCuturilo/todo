from rest_framework import serializers
from .models import Project, Tag, Task, FocusSession, SavedFilter, TaskDependency, LinkAttachment, Attachment


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'slug', 'description', 'is_archived', 'created_at', 'updated_at']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'color_hex']


class TaskSerializer(serializers.ModelSerializer):
    project = serializers.SlugRelatedField(slug_field='slug', queryset=Project.objects.all(), allow_null=True, required=False)
    tags = serializers.SlugRelatedField(slug_field='slug', queryset=Tag.objects.all(), many=True, required=False)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description_md', 'status', 'priority',
            'project', 'tags', 'parent', 'start_at', 'due_at', 'completed_at',
            'estimate_minutes', 'repeat', 'external_url', 'created_at', 'updated_at'
        ]


class FocusSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FocusSession
        fields = ['id', 'owner', 'task', 'kind', 'started_at', 'ended_at', 'duration_minutes', 'notes', 'created_at']
        read_only_fields = ['owner', 'created_at']


class SavedFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedFilter
        fields = ['id', 'owner', 'name', 'query', 'is_favorite', 'created_at']
        read_only_fields = ['owner', 'created_at'] 