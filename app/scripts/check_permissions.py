# check_permissions.py
import sys
import os
from pathlib import Path

# اضافه کردن مسیر پروژه
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

from app import create_app, db
from app.models import User, Role, Permission

app = create_app()

with app.app_context():
    print("🔍 بررسی وضعیت دسترسی‌های سیستم")
    print("=" * 50)
    
    # ۱. بررسی کاربر admin
    print("\n👤 بررسی کاربر admin:")
    admin_user = User.query.filter_by(username='admin').first()
    if admin_user:
        print(f"   ✅ کاربر admin پیدا شد")
        print(f"   📛 نام: {admin_user.name}")
        print(f"   🔢 ID: {admin_user.id}")
        print(f"   🆔 نقش ID: {admin_user.role_id}")
    else:
        print("   ❌ کاربر admin پیدا نشد!")
    
    # ۲. بررسی نقش admin
    print("\n🎭 بررسی نقش admin:")
    admin_role = Role.query.filter_by(name='admin').first()
    if admin_role:
        print(f"   ✅ نقش admin پیدا شد")
        print(f"   🔢 ID: {admin_role.id}")
        print(f"   📝 توضیحات: {admin_role.description}")
    else:
        print("   ❌ نقش admin پیدا نشد!")
    
    # ۳. بررسی دسترسی‌های نقش admin
    if admin_role:
        print(f"\n🔑 دسترسی‌های نقش admin:")
        permissions = Permission.query.filter_by(role_id=admin_role.id).all()
        if permissions:
            for perm in permissions:
                print(f"   ✅ {perm.name}")
        else:
            print("   ❌ هیچ دسترسی‌ای برای نقش admin تعریف نشده!")
    
    # ۴. بررسی ارتباط کاربر و نقش
    if admin_user and admin_role:
        print(f"\n🔗 ارتباط کاربر و نقش:")
        if admin_user.role_id == admin_role.id:
            print("   ✅ کاربر admin به نقش admin منتسب شده")
        else:
            print(f"   ❌ کاربر admin به نقش دیگری منتسب شده (role_id: {admin_user.role_id})")
    
    # ۵. تست دسترسی‌های مهم
    if admin_user:
        print(f"\n🧪 تست دسترسی‌های کاربر admin:")
        test_permissions = [
            'user.create', 'user.edit', 'user.delete', 'user.view',
            'form.create', 'form.edit', 'form.delete', 'form.view'
        ]
        
        for perm in test_permissions:
            has_perm = admin_user.has_permission(perm)
            status = "✅" if has_perm else "❌"
            print(f"   {status} {perm}: {has_perm}")
    
    print("\n" + "=" * 50)