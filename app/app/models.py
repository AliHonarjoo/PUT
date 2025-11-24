# app/models.py
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json
from datetime import datetime

# 🔥 مدل‌های جدید برای RBAC
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # admin, manager, user, viewer
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    permissions = db.relationship('Permission', backref='role', lazy=True)

class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)  # user.create, user.edit, form.delete
    description = db.Column(db.String(200))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 🔥 آپدیت مدل User
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    mobile = db.Column(db.String(11), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'))
    position = db.Column(db.String(50))
    
    # 🔥 تغییر از role ساده به سیستم RBAC
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    role = db.relationship('Role', backref='users')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    organization = db.relationship('Organization', backref='users', lazy=True)
    area = db.relationship('Area', backref='users', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 🔥 متدهای جدید برای دسترسی‌ها
    def has_permission(self, permission_name):
        """بررسی آیا کاربر دسترسی خاصی دارد"""
        # ادمین به همه چیز دسترسی داره
        if self.role.name == 'admin':
            return True
        
        # بررسی دسترسی در نقش کاربر
        return any(perm.name == permission_name for perm in self.role.permissions)

    def can_create_user(self): return self.has_permission('user.create')
    def can_edit_user(self): return self.has_permission('user.edit')
    def can_delete_user(self): return self.has_permission('user.delete')
    def can_view_users(self): return self.has_permission('user.view')

    def can_create_form(self): return self.has_permission('form.create')
    def can_edit_form(self): return self.has_permission('form.edit')
    def can_delete_form(self): return self.has_permission('form.delete')
    def can_view_forms(self): return self.has_permission('form.view')
    def can_manage_all_forms(self): return self.has_permission('form.manage_all')
    
    def can_manage_settings(self): return self.has_permission('settings.manage')
    def can_manage_roles(self): return self.has_permission('role.manage')
    
    def can_view_reports(self): return self.has_permission('reports.view')
    def can_generate_reports(self): return self.has_permission('reports.generate')

    def is_admin(self): return self.has_permission('system.admin')

# مدل‌های موجود (بدون تغییر)
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    areas = db.relationship('Area', backref='organization', lazy=True)

class Area(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)

class Position(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# app/models.py - آپدیت مدل Form
class Form(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    structure = db.Column(db.Text, nullable=False)  # JSON با ساختار جدید
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    creator = db.relationship('User', backref='forms', lazy=True)
    
    def get_structure(self):
        return json.loads(self.structure) if self.structure else []
    
    accesses = db.relationship('FormAccess', backref='form', lazy=True, cascade='all, delete-orphan')




class FormResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('form.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    responses = db.Column(db.Text)  # ذخیره پاسخ‌ها به صورت JSON
    filled_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # روابط
    form = db.relationship('Form', backref=db.backref('form_responses', lazy=True))
    user = db.relationship('User', backref=db.backref('form_responses', lazy=True))

class UserPermission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    form_id = db.Column(db.Integer, db.ForeignKey('form.id'), nullable=False)
    can_view = db.Column(db.Boolean, default=False)
    can_fill = db.Column(db.Boolean, default=False)
    can_edit = db.Column(db.Boolean, default=False)
    can_delete = db.Column(db.Boolean, default=False)



class FormAccess(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('form.id'))
    access_type = db.Column(db.String(20))  # 'user' یا 'role'
    target_id = db.Column(db.Integer)  # user_id یا role_id
    permissions = db.Column(db.String(100))  # 'view,fill,edit' یا 'full'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<FormAccess {self.id}>'
