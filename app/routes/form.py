from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import Role, User, Form, UserPermission,FormResponse, FormAccess
from app.decorators import can_create_form, can_edit_form, can_delete_form, can_manage_form, permission_required
import json

form_bp = Blueprint('form', __name__, url_prefix='/form')

@form_bp.route('/create', methods=['GET', 'POST'])
@login_required
@can_create_form
def create():
    from app import db
    if request.method == 'POST':
        try:
            # اصلاح این قسمت - استفاده از get_json() به جای form
            if request.is_json:
                data = request.get_json()
                title = data.get('title')
                structure = data.get('structure')
            else:
                title = request.form.get('title')
                structure = request.form.get('structure')
            
            if not title or not structure:
                flash('عنوان و ساختار فرم الزامی است', 'danger')
                return redirect(url_for('form.create'))
            
            print(f"📝 دریافت داده‌ها - عنوان: {title}")  # 🔥 برای دیباگ
            print(f"📦 ساختار: {structure[:100]}...")    # 🔥 برای دیباگ
            
            # اصلاح: structure رو به صورت string ذخیره کن
            form = Form(
                title=title, 
                structure=structure,  # همینطور string باشه
                created_by=current_user.id
            )
            db.session.add(form)
            db.session.commit()
            
            flash('فرم با موفقیت ایجاد شد!', 'success')
            return redirect(url_for('form.list'))
            
        except Exception as e:
            print(f"❌ خطا در ایجاد فرم: {e}")
            flash('خطا در ایجاد فرم', 'danger')
            return redirect(url_for('form.create'))
    
    return render_template('form/create_matrix.html')

@form_bp.route('/list')
@login_required
def list():
    forms = Form.query.all()
    return render_template('form/list.html', forms=forms)

@form_bp.route('/fill/<int:form_id>', methods=['GET', 'POST'])
@login_required
def fill(form_id):
    from app import db
    form = Form.query.get_or_404(form_id)
    
    if request.method == 'POST':
        try:
            print("🔍 دریافت داده‌های فرم...")
            
            # استخراج پاسخ‌ها
            responses = {}
            for key, value in request.form.items():
                if key.startswith('cell_'):
                    responses[key] = value
            
            print(f"📦 پاسخ‌های استخراج شده: {responses}")
            
            # ذخیره در دیتابیس
            form_response = FormResponse(
                form_id=form_id,
                user_id=current_user.id,
                responses=json.dumps(responses, ensure_ascii=False),
                filled_at=datetime.utcnow()
            )
            
            db.session.add(form_response)
            db.session.commit()
            
            print("✅✅✅ ذخیره موفق! ✅✅✅")
            flash('فرم با موفقیت پر و ذخیره شد!', 'success')
            return redirect(url_for('form.list'))
            
        except Exception as e:
            print(f"❌ خطا: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            flash('خطا در ذخیره فرم', 'danger')
    
    structure = json.loads(form.structure)
    return render_template('form/fill.html', form=form, structure=structure)

# تابع کمکی برای چک دسترسی
def can_user_fill_form(user, form):
    return (
        form.created_by == user.id or
        user.role == 'admin' or
        UserPermission.query.filter_by(
            user_id=user.id, 
            form_id=form.id, 
            can_fill=True
        ).first() is not None
    )

# تابع کمکی برای استخراج پاسخ‌ها
def extract_form_responses(form_data):
    return {
        key: value 
        for key, value in form_data.to_dict().items() 
        if key.startswith('cell_')
    }

@form_bp.route('/permissions/<int:form_id>', methods=['GET', 'POST'])
@login_required
@permission_required('form.manage_all')
def permissions(form_id):
    from app import db
    if current_user.role != 'admin':
        flash('فقط ادمین', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = Form.query.get_or_404(form_id)
    if request.method == 'POST':
        for user_id in request.form:
            perm = UserPermission.query.filter_by(user_id=user_id, form_id=form_id).first()
            if not perm:
                perm = UserPermission(user_id=user_id, form_id=form_id)
                db.session.add(perm)
            perm.can_view = 'view_' + user_id in request.form
            perm.can_fill = 'fill_' + user_id in request.form
            perm.can_edit = 'edit_' + user_id in request.form
            perm.can_delete = 'delete_' + user_id in request.form
        db.session.commit()
        flash('دسترسی‌ها ذخیره شد', 'success')
    
    users = User.query.all()
    permissions = {p.user_id: p for p in UserPermission.query.filter_by(form_id=form_id)}
    return render_template('form/permissions.html', form=form, users=users, permissions=permissions)


@form_bp.route('/create_advanced', methods=['GET', 'POST'])
@login_required
@can_create_form
def create_advanced():
    from app import db
    if request.method == 'POST':
        title = request.form['title']
        structure = request.form['structure']
        
        form = Form(title=title, structure=structure, created_by=current_user.id)
        db.session.add(form)
        db.session.commit()
        
        flash('فرم با موفقیت ایجاد شد!', 'success')
        return redirect(url_for('form.list'))
    
    return render_template('form/create_advanced.html')



@form_bp.route('/create_matrix', methods=['GET', 'POST'])
@login_required
@can_create_form
def create_matrix():
    from app import db
    if request.method == 'POST':
        title = request.form['title']
        structure = request.form['structure']
        
        form = Form(title=title, structure=structure, created_by=current_user.id)
        db.session.add(form)
        db.session.commit()
        
        flash('فرم جدولی با موفقیت ایجاد شد!', 'success')
        return redirect(url_for('form.list'))
    
    return render_template('form/create_matrix.html')


@form_bp.route('/fill_matrix/<int:form_id>', methods=['GET', 'POST'])
@login_required
@can_edit_form
def fill_matrix(form_id):
    form = Form.query.get_or_404(form_id)
    structure = form.get_structure()
    
    if request.method == 'POST':
        # پردازش داده‌های ارسالی
        data = request.form.to_dict()
        print("داده‌های دریافت شده:", data)
        flash('داده‌ها با موفقیت ذخیره شد!', 'success')
        return redirect(url_for('form.list'))
    
    return render_template('form/fill_matrix.html', 
                         form=form, 
                         structure_json=json.dumps(structure),
                         current_user_id=current_user.id,
                         form_creator_id=form.created_by)


@form_bp.route('/view/<int:form_id>')
@login_required
@can_edit_form
def view(form_id):
    form = Form.query.get_or_404(form_id)
    
    # اگر structure رشته JSON هست، به object تبدیل کن
    if isinstance(form.structure, str):
        try:
            structure_data = json.loads(form.structure)
        except:
            structure_data = {'rows': 0, 'columns': [], 'default_data': []}
    else:
        structure_data = form.structure
    
    return render_template('form/view.html', form=form, structure=structure_data)


@form_bp.route('/all_responses')
@login_required
def all_responses():
    # دریافت صفحه از پارامتر URL
    page = request.args.get('page', 1, type=int)
    per_page = 15  # تعداد در هر صفحه
    
    # محاسبه offset
    offset = (page - 1) * per_page
    
    # تمام پاسخ‌های کاربر (یا اگر ادمین هست، همه پاسخ‌ها)
    if current_user.role == 'admin':
        query = FormResponse.query.order_by(FormResponse.filled_at.desc())
        total_responses = query.count()
        responses = query.offset(offset).limit(per_page).all()
    else:
        # فقط پاسخ‌های فرم‌هایی که کاربر ساخته
        user_forms = Form.query.filter_by(created_by=current_user.id).all()
        form_ids = [form.id for form in user_forms]
        query = FormResponse.query.filter(FormResponse.form_id.in_(form_ids)).order_by(FormResponse.filled_at.desc())
        total_responses = query.count()
        responses = query.offset(offset).limit(per_page).all()
    
    # محاسبه تعداد صفحات
    total_pages = (total_responses + per_page - 1) // per_page
    
    return render_template('form/all_responses.html', 
                         responses=responses,
                         page=page,
                         per_page=per_page,
                         total_responses=total_responses,
                         total_pages=total_pages)



@form_bp.route('/responses/<int:form_id>')
@login_required
@can_edit_form
def view_responses(form_id):
    form = Form.query.get_or_404(form_id)
    
    # اگر response_id مشخص شده، فقط اون پاسخ رو نشون بده
    response_id = request.args.get('response_id')
    if response_id:
        response = FormResponse.query.get_or_404(response_id)
        responses = [response]
    else:
        # همه پاسخ‌های این فرم
        responses = FormResponse.query.filter_by(form_id=form_id).all()
    
    # پردازش پاسخ‌ها (همون کد قبلی)
    processed_responses = []
    for response in responses:
        try:
            if isinstance(response.responses, str):
                response_data = json.loads(response.responses)
            else:
                response_data = response.responses
            processed_responses.append({
                'id': response.id,
                'user': response.user,
                'filled_at': response.filled_at,
                'data': response_data
            })
        except:
            processed_responses.append({
                'id': response.id,
                'user': response.user,
                'filled_at': response.filled_at,
                'data': {}
            })
    
    # تبدیل structure فرم
    if isinstance(form.structure, str):
        try:
            structure = json.loads(form.structure)
        except:
            structure = {'rows': 0, 'columns': [], 'default_data': []}
    else:
        structure = form.structure
    
    return render_template('form/responses.html', 
                         form=form, 
                         responses=processed_responses, 
                         structure=structure)


# مدیریت دسترسی فرم
@form_bp.route('/access/<int:form_id>')
@login_required
@can_manage_form  # ✅ استفاده از دکوراتور
def manage_access(form_id):
    form = Form.query.get_or_404(form_id)
    roles = Role.query.all()
    users = User.query.all()
    current_accesses = FormAccess.query.filter_by(form_id=form_id).all()
    
    return render_template('form/access_management.html', 
                         form=form,
                         roles=roles,
                         users=users,
                         accesses=current_accesses)

# ذخیره دسترسی
@form_bp.route('/access/save', methods=['POST'])
@login_required
def save_form_access():
    from app import db
    try:
        print("🔍 دریافت درخواست save_form_access")
        
        form_id = request.form.get('form_id')
        access_type = request.form.get('access_type')
        target_id = request.form.get('target_id')
        permissions = request.form.getlist('permissions')
        
        print(f"📥 داده‌ها: form_id={form_id}, access_type={access_type}, target_id={target_id}, permissions={permissions}")
        
        # بررسی داده‌های ضروری
        if not all([form_id, access_type, target_id]):
            return jsonify({'error': 'داده‌های ناقص'}), 400
        
        form = Form.query.get_or_404(form_id)
        
        # ✅ استفاده از RBAC - چک permission
        if not current_user.has_permission('form.manage_all') and form.created_by != current_user.id:
            return jsonify({'error': 'دسترسی غیرمجاز'}), 403
        
        # حذف دسترسی‌های قبلی
        FormAccess.query.filter_by(form_id=form_id, access_type=access_type, target_id=target_id).delete()
        
        # ایجاد دسترسی جدید
        if permissions:
            access = FormAccess(
                form_id=form_id,
                access_type=access_type,
                target_id=target_id,
                permissions=','.join(permissions)
            )
            db.session.add(access)
        
        db.session.commit()
        print("✅ دسترسی ذخیره شد")
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"❌ خطا: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500