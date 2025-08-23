from django import forms
from .models import Task, Project, Tag, TaskRelationship, Event, TimeSlot, UserPreferences, Sketch


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'priority', 'project', 'tags', 'due_at', 'estimate_minutes']
        widgets = {
            'due_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filter projects for the current user
            self.fields['project'].queryset = Project.objects.filter(user=user)


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']


class TaskRelationshipForm(forms.ModelForm):
    class Meta:
        model = TaskRelationship
        fields = ['to_task', 'relationship_type']

# New calendar forms
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'start_time', 'end_time', 
            'is_recurring', 'recurrence_type', 'recurrence_interval',
            'weekdays', 'end_date', 'max_occurrences'
        ]
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'recurrence_interval': forms.NumberInput(attrs={'min': 1, 'max': 365}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'max_occurrences': forms.NumberInput(attrs={'min': 1, 'max': 1000}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Create custom choices for weekdays
        self.fields['weekdays'] = forms.MultipleChoiceField(
            choices=Event.WEEKDAY_CHOICES,
            widget=forms.CheckboxSelectMultiple,
            required=False,
            help_text="Select the days when this event repeats (for weekly recurrence)"
        )
        
        # Make end_date and max_occurrences not required
        self.fields['end_date'].required = False
        self.fields['max_occurrences'].required = False
        
        # Initialize weekdays if editing an existing event
        if self.instance and self.instance.pk:
            if self.instance.weekdays:
                self.fields['weekdays'].initial = [str(day) for day in self.instance.weekdays]

class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ['name', 'start_time', 'end_time', 'days_of_week', 'is_active']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Create custom choices for days of week
        self.fields['days_of_week'] = forms.MultipleChoiceField(
            choices=TimeSlot.DAYS_OF_WEEK,
            widget=forms.CheckboxSelectMultiple,
            required=False,
            help_text="Select the days when this time slot applies"
        )

class UserPreferencesForm(forms.ModelForm):
    class Meta:
        model = UserPreferences
        fields = ['work_start_time', 'work_end_time', 'daily_work_hours']
        widgets = {
            'work_start_time': forms.TimeInput(attrs={'type': 'time'}),
            'work_end_time': forms.TimeInput(attrs={'type': 'time'}),
            'daily_work_hours': forms.NumberInput(attrs={'min': 1, 'max': 24}),
        } 

class SketchForm(forms.ModelForm):
    class Meta:
        model = Sketch
        fields = ['title', 'description', 'project', 'task']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filter tasks and projects for the current user
            self.fields['task'].queryset = Task.objects.filter(user=user)
            self.fields['project'].queryset = Project.objects.filter(user=user)
        
        # Make project and task optional
        self.fields['project'].required = False
        self.fields['task'].required = False 