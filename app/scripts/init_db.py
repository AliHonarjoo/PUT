# scripts/init_db.py
import sys
import os
from pathlib import Path

# اضافه کردن مسیر پروژه به Python path
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

from app import create_app, db
from app.models import User, Organization, Area, Position, Role

def get_admin_credentials():
    print("🔧 Initial System Setup")
    print("=" * 40)
    
    # Get admin username
    while True:
        username = input("Admin username: ").strip()
        if username:
            break
        print("❌ Username is required!")
    
    # Get password with confirmation
    while True:
        password = input("Password: ").strip()
        if len(password) < 6:
            print("❌ Password must be at least 6 characters!")
            continue
            
        password2 = input("Confirm password: ").strip()
        if password != password2:
            print("❌ Passwords don't match!")
            continue
        break
    
    # Get full name
    while True:
        name = input("Full name: ").strip()
        if name:
            break
        print("❌ Full name is required!")
    
    # Get mobile number
    while True:
        mobile = input("Mobile (11 digits starting with 09): ").strip()
        if len(mobile) == 11 and mobile.startswith('09'):
            break
        print("❌ Mobile must be 11 digits and start with 09!")
    
    return username, password, name, mobile

def main():
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if admin already exists
        if User.query.first():
            print("❌ Database already initialized!")
            return
        
        # ابتدا نقش admin رو ایجاد کن (اگر وجود نداره)
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin', description='مدیر سیستم - دسترسی کامل')
            db.session.add(admin_role)
            db.session.flush()
            print("✅ نقش admin ایجاد شد")
        
        # Get admin credentials
        username, password, name, mobile = get_admin_credentials()
        
        # Create admin user - بدون فیلد role
        admin = User(
            username=username,
            name=name,
            mobile=mobile
            # ❌ role='admin' رو حذف کردیم
        )
        admin.set_password(password)
        admin.role_id = admin_role.id  # 🔥 استفاده از role_id جدید
        db.session.add(admin)
        
        # Create sample organization
        org = Organization(name='University of Petroleum Technology')
        db.session.add(org)
        db.session.flush()
        
        # Create sample areas
        areas = ['Headquarters', 'Abadan', 'Tehran', 'Ahvaz', 'Mahmoud Abad']
        for area_name in areas:
            area = Area(name=area_name, organization_id=org.id)
            db.session.add(area)
        
        # Create sample positions
        positions = ['Manager', 'Employee', 'Professor']
        for pos_name in positions:
            position = Position(name=pos_name)
            db.session.add(position)
        
        db.session.commit()
        
        print("\n✅ Setup completed successfully!")
        print(f"👤 Admin user: {username}")
        print(f"📱 Mobile: {mobile}")
        print(f"🔑 Password: {'*' * len(password)}")
        print("\n🚀 You can now run: python run.py")

if __name__ == '__main__':
    main()