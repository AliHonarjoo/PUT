# migration_script.py - ایجاد کن و اجرا کن
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # اضافه کردن فیلد role_id به کاربران موجود
    users = User.query.all()
    for user in users:
        if not hasattr(user, 'role_id'):
            # مقدار پیش‌فرض برای کاربران موجود
            user.role_id = 1  # فرض کن role_id=1 مربوط به admin هست
    
    db.session.commit()
    print("✅ Database migrated successfully!")