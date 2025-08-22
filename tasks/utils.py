import re
from datetime import datetime, timedelta
from typing import Optional

from django.utils import timezone

from .models import Task, Project, Tag


def _parse_relative_date(token: str) -> Optional[datetime]:
    now = timezone.localtime()
    token = token.lower()
    if token in ('today', 'tod'):  # due:today
        return now.replace(hour=18, minute=0, second=0, microsecond=0)
    if token in ('tomorrow', 'tom'):  # due:tom
        d = now + timedelta(days=1)
        return d.replace(hour=18, minute=0, second=0, microsecond=0)
    if token in ('nextweek', 'next-week', 'next_wk'):  # due:nextweek
        d = now + timedelta(days=(7 - now.weekday()))
        return d.replace(hour=18, minute=0, second=0, microsecond=0)
    # YYYY-MM-DD or YYYY/MM/DD
    for fmt in ('%Y-%m-%d', '%Y/%m/%d'):
        try:
            d = datetime.strptime(token, fmt)
            return timezone.make_aware(d)
        except Exception:
            pass
    return None


def parse_quick_add(text: str) -> Task:
    """Parse text like:
    "fix cache bug @backend #perf p2 due:tom est:45m start:today link:https://..."
    Return created Task.
    """
    text = text.strip()
    if not text:
        raise ValueError('Empty quick-add input')

    # Defaults
    title_parts = []
    project: Optional[Project] = None
    tags = []
    priority = 3
    due_at: Optional[datetime] = None

    estimate_minutes = 0


    tokens = text.split()
    for token in tokens:
        if token.startswith('@') and len(token) > 1:
            proj_name = token[1:]
            project, _ = Project.objects.get_or_create(name=proj_name)
            continue
        if token.startswith('#') and len(token) > 1:
            tag_name = token[1:]
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            tags.append(tag)
            continue
        if re.fullmatch(r'p[1-5]', token, flags=re.IGNORECASE):
            priority = int(token[1])
            continue
        if token.startswith('due:'):
            v = token[4:]
            due_at = _parse_relative_date(v) or _parse_relative_date(v.replace(':', '-'))
            continue

        if token.startswith('est:'):
            v = token[4:].lower()
            m = re.match(r'^(\d+)(m|h)$', v)
            if m:
                num = int(m.group(1))
                unit = m.group(2)
                estimate_minutes = num if unit == 'm' else num * 60
            continue

        title_parts.append(token)

    title = ' '.join(title_parts).strip() or text

    task = Task.objects.create(
        title=title,
        project=project,
        priority=priority,
        due_at=due_at,
        estimate_minutes=estimate_minutes,
    )
    if tags:
        task.tags.add(*tags)
    return task 