from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.decorators import permission_required
from app.decorators import can_manage_settings
import os

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/logo', methods=['GET', 'POST'])
@login_required
@can_manage_settings
def logo():
    if current_user.role != 'admin':
        flash('دسترسی ندارید', 'danger')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        file = request.files['logo']
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], 'logo.png'))
            flash('لوگو آپلود شد', 'success')
    return render_template('settings/logo.html')