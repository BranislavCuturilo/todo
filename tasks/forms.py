from django import forms
from .models import Task, Project, SavedFilter, Attachment, LinkAttachment, TaskRelationship


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'priority', 'project', 'tags', 'due_at', 'estimate_minutes', 'repeat', 'parent_task']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'project': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'due_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'estimate_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'repeat': forms.Select(attrs={'class': 'form-control'}),
            'parent_task': forms.Select(attrs={'class': 'form-control'}),
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
        }


class SavedFilterForm(forms.ModelForm):
    class Meta:
        model = SavedFilter
        fields = ['name', 'filters']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'filters': forms.HiddenInput(),
        }


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }


class LinkAttachmentForm(forms.ModelForm):
    class Meta:
        model = LinkAttachment
        fields = ['url', 'title', 'description']
        widgets = {
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class TaskRelationshipForm(forms.ModelForm):
    class Meta:
        model = TaskRelationship
        fields = ['to_task', 'relationship_type', 'description']
        widgets = {
            'to_task': forms.Select(attrs={'class': 'form-control'}),
            'relationship_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        } 