# فایل debug_system.py ایجاد کن
import sys
import os
from pathlib import Path

current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

from app import create_app, db
from app.models import User, Role, Permission

app = create_app()

with app.app_context():
    print("🐛 دیباگ کامل سیستم:")
    print("=" * 50)
    
    # کاربر
    admin = User.query.filter_by(username='admin').first()
    print(f"👤 کاربر: {admin.username} (ID: {admin.id})")
    print(f"🔗 role_id: {admin.role_id}")
    
    # نقش
    role = Role.query.get(admin.role_id) if admin.role_id else None
    print(f"🎭 نقش: {role.name if role else 'None'} (ID: {admin.role_id})")
    
    # دسترسی‌ها
    if role:
        perms = Permission.query.filter_by(role_id=role.id).all()
        print(f"🔑 تعداد دسترسی‌ها: {len(perms)}")
        for p in perms:
            print(f"   • {p.name}")
    
    # تست متد has_permission
    print(f"\n🧪 تست متد has_permission:")
    print(f"   user.create: {admin.has_permission('user.create')}")
    print(f"   role.name == 'admin': {role.name == 'admin' if role else False}")
    
    # بررسی داخلی متد
    print(f"\n🔍 بررسی داخلی متد has_permission:")
    if hasattr(admin, 'has_permission'):
        print("✅ متد has_permission وجود داره")
        # تست مستقیم
        if role and role.name == 'admin':
            print("✅ چون admin هست، باید True برگردونه")
        else:
            print("❌ نقش admin نیست!")
    else:
        print("❌ متد has_permission وجود نداره!")
