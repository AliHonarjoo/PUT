from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, Organization, Area, Position, Role  # 🔥 Role رو اضافه کن
from app.forms.forms import CreateUserForm, EditUserForm
from flask_wtf import FlaskForm
from app.decorators import can_create_user, can_edit_user, can_delete_user

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/create', methods=['GET', 'POST'])
@login_required
@can_create_user
def create():
    form = CreateUserForm()

    # همیشه choices رو پر کن
    form.organization.choices = [(0, '--- انتخاب سازمان ---')] + [(o.id, o.name) for o in Organization.query.all()]
    form.position.choices = [(0, '--- انتخاب سمت ---')] + [(p.id, p.name) for p in Position.query.all()]
    # اضافه کردن انتخاب نقش
    roles = Role.query.all()
    print(f"🔍 تعداد نقش‌ها: {len(roles)}")
    for role in roles:
        print(f"🔍 نقش: {role.id} - {role.name}")
    form.role_id.choices = [(r.id, r.name) for r in roles]  # اگر فیلد role_id در فرم دارید
    if form.organization.data and form.organization.data != 0:
        form.area.choices = [(0, '--- انتخاب ناحیه ---')] + [
            (a.id, a.name) for a in Area.query.filter_by(organization_id=form.organization.data)
        ]
    else:
        form.area.choices = [(0, '--- ابتدا سازمان را انتخاب کنید ---')]

    if request.method == 'POST':
        print("داده‌های فرم:", request.form)
        if form.validate_on_submit():
            print("فرم validate شد!")
            if User.query.filter_by(username=form.username.data).first():
                flash('نام کاربری قبلاً استفاده شده', 'danger')
            else:
                # 🔥 ایجاد کاربر جدید با سیستم RBAC
                user = User(
                    username=form.username.data,
                    name=f"{form.first_name.data} {form.last_name.data}".strip(),
                    mobile=form.mobile.data,
                    organization_id=form.organization.data,
                    area_id=form.area.data if form.area.data != 0 else None,
                    # ❌ position=Position.query.get(form.position.data).name, - حذف شد
                    # ❌ role='user' - حذف شد
                )
                
                # ست کردن position به صورت صحیح
                position_obj = Position.query.get(form.position.data)
                if position_obj:
                    user.position = position_obj.name
                
                # ست کردن نقش user
                selected_role_id = request.form.get('role_id')
                if selected_role_id:
                    user.role_id = selected_role_id
                else:
                    # پیش‌فرض: نقش user
                    user_role = Role.query.filter_by(name='user').first()
                    user.role_id = user_role.id
                
                user.set_password(form.password.data)
                db.session.add(user)
                db.session.commit()
                
                flash(f'کاربر {user.name} با نقش {user.role.name} ساخته شد!', 'success')
                return redirect(url_for('user.list'))
        else:
            print("خطاهای فرم:", form.errors)

    return render_template('user/create.html', form=form, roles=roles, active_menu='user')

@user_bp.route('/list')
@login_required
def list():
    users = User.query.all()
    form = FlaskForm()  # فقط برای CSRF در فرم حذف
    return render_template('user/list.html', users=users, form=form, active_menu='user')

@user_bp.route('/delete/<int:user_id>', methods=['POST'])
@login_required
@can_delete_user
def delete(user_id):
    # ❌ if current_user.role != 'admin': - حذف شد (دکوراتور کافیه)
    
    user_to_delete = User.query.get_or_404(user_id)
    if user_to_delete.id == current_user.id:
        flash('نمی‌توانید خودتان را حذف کنید!', 'danger')
        return redirect(url_for('user.list'))
    
    db.session.delete(user_to_delete)
    db.session.commit()
    flash(f'کاربر {user_to_delete.name} حذف شد', 'success')
    return redirect(url_for('user.list'))

@user_bp.route('/areas/<int:org_id>')
def get_areas(org_id):
    areas = Area.query.filter_by(organization_id=org_id).all()
    return jsonify([{'id': a.id, 'name': a.name} for a in areas])

@user_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@can_edit_user
def edit(user_id):
    # ❌ if current_user.role != 'admin': - حذف شد (دکوراتور کافیه)

    user = User.query.get_or_404(user_id)
    form = EditUserForm()

    # پر کردن فرم با داده‌های فعلی کاربر
    if request.method == 'GET':
        form.first_name.data = user.name.split(' ')[0] if user.name else ''
        form.last_name.data = ' '.join(user.name.split(' ')[1:]) if user.name else ''
        form.username.data = user.username
        form.mobile.data = user.mobile
        form.organization.data = user.organization_id or 0
        form.position.data = next((p.id for p in Position.query.all() if p.name == user.position), 0)

    # پر کردن choices
    form.organization.choices = [(0, '--- انتخاب سازمان ---')] + [(o.id, o.name) for o in Organization.query.all()]
    form.position.choices = [(0, '--- انتخاب سمت ---')] + [(p.id, p.name) for p in Position.query.all()]
    
    if form.organization.data and form.organization.data != 0:
        form.area.choices = [(0, '--- انتخاب ناحیه ---')] + [
            (a.id, a.name) for a in Area.query.filter_by(organization_id=form.organization.data)
        ]
        form.area.data = user.area_id or 0
    else:
        form.area.choices = [(0, '--- ابتدا سازمان را انتخاب کنید ---')]

    if form.validate_on_submit():
        # بررسی تکراری نبودن username
        existing_user = User.query.filter(User.username == form.username.data, User.id != user_id).first()
        if existing_user:
            flash('این نام کاربری قبلاً استفاده شده', 'danger')
            return render_template('user/edit.html', form=form, user=user, active_menu='user')

        # آپدیت کاربر
        user.username = form.username.data
        user.name = f"{form.first_name.data} {form.last_name.data}".strip()
        user.mobile = form.mobile.data
        user.organization_id = form.organization.data
        user.area_id = form.area.data if form.area.data != 0 else None
        
        # 🔥 ست کردن position به صورت صحیح
        position_obj = Position.query.get(form.position.data)
        if position_obj:
            user.position = position_obj.name

        # اگر پسورد جدید وارد شده
        if form.password.data:
            user.set_password(form.password.data)

        db.session.commit()
        flash(f'کاربر {user.name} با موفقیت بروزرسانی شد!', 'success')
        return redirect(url_for('user.list'))

    return render_template('user/edit.html', form=form, user=user, active_menu='user')