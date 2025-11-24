from app import create_app, db
from app.models import Role, Permission, User

app = create_app()
with app.app_context():
    print("=== وضعیت فعلی RBAC ===")
    
    # چک کردن نقش‌ها
    roles = Role.query.all()
    print(f"تعداد نقش‌ها: {len(roles)}")
    for role in roles:
        print(f" - {role.name}: {[p.name for p in role.permissions]}")
    
    # چک کردن دسترسی‌ها
    permissions = Permission.query.all()
    print(f"تعداد دسترسی‌ها: {len(permissions)}")
    
    # چک کردن یک کاربر
    user = User.query.first()
    if user and user.role:
        print(f"کاربر نمونه: {user.username}, نقش: {user.role.name}")