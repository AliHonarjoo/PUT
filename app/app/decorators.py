# app/decorators.py
from functools import wraps
from venv import logger
from app.models import Form
from flask import flash, redirect, url_for, request
from flask_login import current_user
import logging


def permission_required(permission_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('لطفاً ابتدا وارد سیستم شوید', 'danger')
                return redirect(url_for('auth.login'))
            
            # 🔥 این خط باید درست باشه:
            if not current_user.has_permission(permission_name):
                flash('شما دسترسی لازم برای این صفحه را ندارید', 'danger')
                return redirect(url_for('main.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """
    دکوراتور برای دسترسی ادمین
    """
    return permission_required('system.admin')(f)

def can_create_user(f):
    """
    دکوراتور برای ایجاد کاربر
    """
    return permission_required('user.create')(f)

def can_edit_user(f):
    """
    دکوراتور برای ویرایش کاربر
    """
    return permission_required('user.edit')(f)

def can_delete_user(f):
    """
    دکوراتور برای حذف کاربر
    """
    return permission_required('user.delete')(f)

def can_create_form(f):
    """
    دکوراتور برای ایجاد فرم
    """
    return permission_required('form.create')(f)

def can_edit_form(f):
    """
    دکوراتور برای ویرایش فرم
    """
    return permission_required('form.edit')(f)

def can_delete_form(f):
    """
    دکوراتور برای حذف فرم
    """
    return permission_required('form.delete')(f)

def can_manage_settings(f):
    """
    دکوراتور برای مدیریت تنظیمات
    """
    return permission_required('settings.manage')(f)

def can_view_reports(f):
    """
    دکوراتور برای مشاهده گزارشات
    """
    return permission_required('reports.view')(f)

def admin_required(f):
    return permission_required('system.admin')(f)

def can_manage_form(f):
    @wraps(f)
    def decorated_function(form_id, *args, **kwargs):
        form = Form.query.get_or_404(form_id)
        if form.created_by != current_user.id and not current_user.has_permission('form.manage_all'):
            flash('دسترسی غیرمجاز', 'danger')
            return redirect(url_for('form.list'))
        return f(form_id, *args, **kwargs)
    return decorated_function
