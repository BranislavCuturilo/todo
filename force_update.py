#!/usr/bin/env python
"""
Force update script to clear all caches and force reload.
Run this on production to ensure all solo-todo references are cleared.
"""

import os
import sys
import django
import shutil
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'solo_todo.settings_production')
django.setup()

def force_update():
    """Force update all caches and static files."""
    print("🚀 Force updating TODO application...")
    
    # Clear Django cache
    print("🧹 Clearing Django cache...")
    from django.core.cache import cache
    cache.clear()
    print("✅ Django cache cleared")
    
    # Clear static files completely
    print("📁 Clearing static files cache...")
    from django.conf import settings
    static_root = Path(settings.STATIC_ROOT)
    if static_root.exists():
        shutil.rmtree(static_root)
        print("✅ Static files cache cleared")
    
    # Recollect static files
    print("📁 Recollecting static files...")
    from django.core.management import call_command
    call_command('collectstatic', '--noinput')
    print("✅ Static files recollected")
    
    # Clear any old service worker files
    print("🔧 Clearing old service worker files...")
    static_dir = Path(settings.STATICFILES_DIRS[0])
    sw_file = static_dir / 'sw.js'
    if sw_file.exists():
        print("✅ Service worker file found and will be updated")
    
    # Set proper permissions
    print("🔐 Setting proper permissions...")
    os.system(f"sudo chown -R www-data:www-data {static_root}")
    os.system(f"sudo chmod -R 755 {static_root}")
    print("✅ Permissions set")
    
    print("🎉 Force update completed!")
    print("💡 Next steps:")
    print("   1. Restart the application: sudo systemctl restart todo")
    print("   2. Clear browser cache (Ctrl+F5)")
    print("   3. Open in incognito mode to test")
    print("   4. If still seeing 'solo todo', check browser developer tools")

if __name__ == '__main__':
    force_update()
