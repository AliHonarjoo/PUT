# app/decorators.py
from functools import wraps
from flask import flash, redirect, url_for, request
from flask_login import current_user
import logging

# تنظیمات لاگینگ
logger = logging.getLogger(__name__)

def permission_required(permission_name):
    """
    دکوراتور برای بررسی دسترسی کاربر
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # بررسی احراز هویت
            if not current_user.is_authenticated:
                flash('لطفاً ابتدا وارد سیستم شوید', 'danger')
                return redirect(url_for('auth.login'))
            
            # بررسی دسترسی
            if not current_user.has_permission(permission_name):
                logger.warning(f"دسترسی رد شد: کاربر {current_user.username} به {permission_name}")
                flash('شما دسترسی لازم برای این صفحه را ندارید', 'danger')
                
                # اگر درخواست AJAX باشه
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return {'error': 'دسترسی رد شد'}, 403
                
                return redirect(url_for('main.dashboard'))
            
            # اگر همه چیز اوکی بود
            logger.debug(f"دسترسی تایید شد: کاربر {current_user.username} به {permission_name}")
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