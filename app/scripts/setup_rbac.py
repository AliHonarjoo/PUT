#!/usr/bin/env python3
"""
RBAC System Setup Script
Version: 1.0
Description: Setup Role-Based Access Control system for Form Management System
"""

import sys
import os
from pathlib import Path

# اضافه کردن مسیر پروژه به Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app, db
from app.models import Role, Permission, User


class RBACSetup:
    """کلاس مدیریت راه‌اندازی سیستم RBAC"""
    
    def __init__(self):
        self.app = create_app()
        self.roles_permissions = {
            'admin': {
                'description': 'مدیر سیستم - دسترسی کامل',
                'permissions': [
                    'user.create', 'user.edit', 'user.delete', 'user.view',
                    'form.create', 'form.edit', 'form.delete', 'form.view', 
                    'form.manage_all', 'settings.manage', 'role.manage',
                    'system.admin', 'reports.view', 'reports.generate'
                ]
            },
            'manager': {
                'description': 'مدیر میانی - مدیریت کاربران و فرم‌ها',
                'permissions': [
                    'user.create', 'user.edit', 'user.view',
                    'form.create', 'form.edit', 'form.view', 'form.manage_all',
                    'reports.view', 'reports.generate'
                ]
            },
            'user': {
                'description': 'کاربر عادی - ایجاد و مدیریت فرم‌های خود',
                'permissions': [
                    'form.create', 'form.edit', 'form.view', 
                    'profile.edit', 'reports.view'
                ]
            },
            'viewer': {
                'description': 'ناظر - فقط مشاهده',
                'permissions': [
                    'form.view',
                    'reports.view'
                ]
            }
        }
    
    def setup_roles(self):
        #ایجاد نقش‌های پایه
        with self.app.app_context():
            print("🔧 در حال راه‌اندازی سیستم RBAC...")
            print("=" * 50)
        
            created_roles = 0
            created_permissions = 0
        
            # ابتدا تمام دسترسی‌های موجود رو بررسی کن
            existing_permissions = {perm.name for perm in Permission.query.all()}
        
            # ایجاد نقش‌ها
            for role_name, role_data in self.roles_permissions.items():
                role = Role.query.filter_by(name=role_name).first()
                if not role:
                    role = Role(
                        name=role_name, 
                        description=role_data['description']
                    )
                    db.session.add(role)
                    db.session.flush()
                    created_roles += 1
                    print(f"✅ نقش ایجاد شد: {role_name}")
                    print(f"   📝 {role_data['description']}")
                else:
                    print(f"⚠️ نقش موجود: {role_name}")
                    # آپدیت توضیحات اگر تغییر کرده
                    if role.description != role_data['description']:
                        role.description = role_data['description']
                        print(f"   🔄 توضیحات آپدیت شد")
            
                # ایجاد دسترسی‌ها - با بررسی تکراری نبودن
                for perm_name in role_data['permissions']:
                    # بررسی کن آیا این دسترسی قبلاً برای این نقش ایجاد شده
                    existing_perm = Permission.query.filter_by(
                        name=perm_name, 
                        role_id=role.id
                    ).first()
                
                    if existing_perm:
                        # دسترسی از قبل برای این نقش وجود داره
                        continue
                
                    # بررسی کن آیا این دسترسی برای نقش دیگه‌ای وجود داره
                    if perm_name in existing_permissions:
                        print(f"   ⚠️ دسترسی '{perm_name}' برای نقش دیگر وجود دارد - نادیده گرفته شد")
                        continue
                
                    # ایجاد دسترسی جدید
                    permission = Permission(
                        name=perm_name,
                        description=f'اجازه {perm_name.replace(".", " ")}',
                        role_id=role.id
                    )
                    db.session.add(permission)
                    existing_permissions.add(perm_name)  # اضافه کردن به لیست موجود
                    created_permissions += 1
                    print(f"   ➕ دسترسی: {perm_name}")
        
            db.session.commit()
            print(f"\n📊 ایجاد شده: {created_roles} نقش, {created_permissions} دسترسی")
    
    def assign_default_roles(self):
        """انتساب نقش پیش‌فرض به کاربران موجود"""
        with self.app.app_context():
            admin_role = Role.query.filter_by(name='admin').first()
            if not admin_role:
                print("❌ نقش admin یافت نشد!")
                return
            
            users = User.query.all()
            updated_count = 0
            
            for user in users:
                if not user.role_id:
                    user.role_id = admin_role.id
                    updated_count += 1
                    print(f"👤 کاربر {user.username} نقش admin گرفت")
            
            if updated_count > 0:
                db.session.commit()
                print(f"✅ {updated_count} کاربر به نقش admin منتسب شدند")
            else:
                print("ℹ️ همه کاربران قبلاً نقش داشتند")
    
    def migrate_old_roles(self):
        """مهاجرت از سیستم نقش قدیمی به RBAC"""
        with self.app.app_context():
            print("\n🔄 مهاجرت از سیستم نقش قدیمی...")
            
            admin_role = Role.query.filter_by(name='admin').first()
            user_role = Role.query.filter_by(name='user').first()
            
            if not admin_role or not user_role:
                print("❌ نقش‌های پایه یافت نشدند!")
                return
            
            migrated_count = 0
            
            # اگر کاربران هنوز فیلد role قدیمی رو دارن
            users_with_old_role = User.query.filter(User.role != None).all()
            for user in users_with_old_role:
                if user.role == 'admin' and user.role_id != admin_role.id:
                    user.role_id = admin_role.id
                    migrated_count += 1
                    print(f"👤 کاربر {user.username} → admin")
                elif user.role == 'user' and user.role_id != user_role.id:
                    user.role_id = user_role.id
                    migrated_count += 1
                    print(f"👤 کاربر {user.username} → user")
            
            if migrated_count > 0:
                db.session.commit()
                print(f"✅ {migrated_count} کاربر مهاجرت داده شدند")
            else:
                print("ℹ️ هیچ کاربری نیاز به مهاجرت نداشت")
    
    def show_summary(self):
        """نمایش خلاصه سیستم"""
        with self.app.app_context():
            print("\n" + "=" * 50)
            print("📊 خلاصه سیستم RBAC")
            print("=" * 50)
            
            roles = Role.query.all()
            total_users = User.query.count()
            
            print(f"\n👥 کل کاربران سیستم: {total_users}")
            
            for role in roles:
                permissions = Permission.query.filter_by(role_id=role.id).all()
                users_count = User.query.filter_by(role_id=role.id).count()
                
                print(f"\n🎭 نقش: {role.name}")
                print(f"   📝 توضیح: {role.description}")
                print(f"   👥 کاربران: {users_count}")
                print(f"   🔑 دسترسی‌ها ({len(permissions)}):")
                
                # گروه‌بندی دسترسی‌ها
                perm_groups = {}
                for perm in permissions:
                    group = perm.name.split('.')[0]  # user, form, settings, etc.
                    if group not in perm_groups:
                        perm_groups[group] = []
                    perm_groups[group].append(perm.name)
                
                for group, perms in perm_groups.items():
                    print(f"      📂 {group}: {', '.join([p.split('.')[1] for p in perms])}")
    
    def verify_system(self):
        """بررسی سلامت سیستم"""
        with self.app.app_context():
            print("\n🔍 بررسی سلامت سیستم...")
            
            # بررسی نقش‌های ضروری
            essential_roles = ['admin', 'user']
            for role_name in essential_roles:
                role = Role.query.filter_by(name=role_name).first()
                if not role:
                    print(f"❌ نقش ضروری '{role_name}' یافت نشد!")
                    return False
            
            # بررسی دسترسی‌های پایه
            essential_permissions = ['user.create', 'form.create', 'form.view']
            for perm_name in essential_permissions:
                perm = Permission.query.filter_by(name=perm_name).first()
                if not perm:
                    print(f"❌ دسترسی ضروری '{perm_name}' یافت نشد!")
                    return False
            
            # بررسی کاربران بدون نقش
            users_without_role = User.query.filter_by(role_id=None).count()
            if users_without_role > 0:
                print(f"⚠️ {users_without_role} کاربر بدون نقش وجود دارد")
            
            print("✅ سیستم RBAC سالم است")
            return True
    
    def run(self):
        """اجرای کامل راه‌اندازی"""
        try:
            print("🚀 سیستم مدیریت دسترسی RBAC")
            print("Version 0.1.2 - Professional RBAC Setup")
            print("=" * 50)
            
            self.setup_roles()
            self.assign_default_roles()
            self.migrate_old_roles()
            self.show_summary()
            
            if self.verify_system():
                print("\n🎉 راه‌اندازی سیستم RBAC با موفقیت انجام شد!")
                print("\n💡 نکته: حالا باید routeها رو برای استفاده از سیستم جدید آپدیت کنی")
            else:
                print("\n❌ راه‌اندازی با مشکل مواجه شد!")
                
        except Exception as e:
            print(f"❌ خطا در راه‌اندازی: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()


def main():
    """تابع اصلی"""
    setup = RBACSetup()
    setup.run()


if __name__ == '__main__':
    main()