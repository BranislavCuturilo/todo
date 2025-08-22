from datetime import timedelta
from django.utils import timezone
from .models import Task


def shift_due_dates(minutes: int, scope: str = 'today') -> int:
    """Shift due_at for tasks by N minutes.
    scope: 'today' -> only tasks due today; 'all' -> all future tasks.
    Returns number of tasks updated.
    """
    if minutes == 0:
        return 0
    now = timezone.now()
    qs = Task.objects.filter(due_at__isnull=False, status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS])
    if scope == 'today':
        today = timezone.localdate()
        qs = qs.filter(due_at__date=today)
    else:
        qs = qs.filter(due_at__gte=now)
    count = 0
    for task in qs.iterator():
        task.due_at = task.due_at + timedelta(minutes=minutes)
        task.save(update_fields=['due_at', 'updated_at'])
        count += 1
    return count 