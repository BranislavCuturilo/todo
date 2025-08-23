#!/usr/bin/env python
"""
Django management command to clear service worker caches.
Run this after deployment to ensure old caches are cleared.
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'solo_todo.settings_production')
django.setup()

from django.core.management import execute_from_command_line

def clear_cache():
    """Clear all Django caches and static files."""
    print("🧹 Clearing Django caches...")
    
    # Clear Django cache
    from django.core.cache import cache
    cache.clear()
    print("✅ Django cache cleared")
    
    # Clear static files
    from django.conf import settings
    import shutil
    
    static_root = Path(settings.STATIC_ROOT)
    if static_root.exists():
        shutil.rmtree(static_root)
        print("✅ Static files cache cleared")
    
    # Recollect static files
    print("📁 Recollecting static files...")
    from django.core.management import call_command
    call_command('collectstatic', '--noinput')
    print("✅ Static files recollected")
    
    print("🎉 Cache clearing completed!")
    print("💡 Remember to hard refresh your browser (Ctrl+F5) to clear browser cache")

if __name__ == '__main__':
    clear_cache()
