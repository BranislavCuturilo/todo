from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from tasks.models import Event

class Command(BaseCommand):
    help = 'Test recurring events functionality'

    def handle(self, *args, **options):
        # Get current date and next week
        today = timezone.now().date()
        next_week = today + timedelta(days=7)
        
        self.stdout.write(f"Testing recurring events from {today} to {next_week}")
        
        # Get all recurring events
        recurring_events = Event.objects.filter(is_recurring=True)
        
        if not recurring_events.exists():
            self.stdout.write("No recurring events found")
            return
        
        for event in recurring_events:
            self.stdout.write(f"\nEvent: {event.title}")
            self.stdout.write(f"  Type: {event.recurrence_type}")
            self.stdout.write(f"  Interval: {event.recurrence_interval}")
            self.stdout.write(f"  Weekdays: {event.weekdays}")
            self.stdout.write(f"  Max occurrences: {event.max_occurrences}")
            self.stdout.write(f"  End date: {event.end_date}")
            
            # Generate instances
            instances = event.get_recurring_events(today, next_week)
            self.stdout.write(f"  Generated {len(instances)} instances:")
            
            for i, instance in enumerate(instances):
                self.stdout.write(f"    {i+1}. {instance['start_time'].date()} at {instance['start_time'].time()}")
            
            # Test with longer range to see if max_occurrences works
            if event.max_occurrences:
                long_range_instances = event.get_recurring_events(today, today + timedelta(days=30))
                self.stdout.write(f"  With 30-day range: {len(long_range_instances)} instances (should be max {event.max_occurrences})")
