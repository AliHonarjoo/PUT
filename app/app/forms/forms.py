from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, NumberRange, Regexp

class LoginForm(FlaskForm):
    username = StringField('نام کاربری', validators=[DataRequired()])
    password = PasswordField('رمز عبور', validators=[DataRequired()])
    submit = SubmitField('ورود')

class CreateUserForm(FlaskForm):
    first_name = StringField('نام', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('نام خانوادگی', validators=[DataRequired(), Length(max=50)])
    username = StringField('نام کاربری', validators=[DataRequired(), Length(max=80)])
    password = PasswordField('رمز عبور', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('تکرار رمز عبور', validators=[DataRequired(), EqualTo('password', message='رمزها یکسان نیستند')])
    mobile = StringField('موبایل', validators=[
        DataRequired(message='شماره موبایل الزامی است'),
        Length(min=11, max=11, message='شماره موبایل باید ۱۱ رقم باشد'),
        Regexp(r'^09[0-9]{9}$', message='فرمت شماره موبایل صحیح نیست ( باید با 09 شروع شود )')
    ])

    # مهم: coerce=int و validator برای اینکه 0 رو قبول نکنه
    organization = SelectField('سازمان', coerce=int, validators=[DataRequired(), NumberRange(min=1, message='لطفاً سازمان را انتخاب کنید')])
    area = SelectField('ناحیه', coerce=int, validators=[DataRequired(), NumberRange(min=1, message='لطفاً ناحیه را انتخاب کنید')])
    position = SelectField('سمت', coerce=int, validators=[DataRequired(), NumberRange(min=1, message='لطفاً سمت را انتخاب کنید')])
    role_id = SelectField('نقش', coerce=int, validators=[DataRequired()])

    submit = SubmitField('ایجاد کاربر')



class EditUserForm(FlaskForm):
    first_name = StringField('نام', validators=[
        DataRequired(message='نام الزامی است'),
        Length(max=50, message='نام نمی‌تواند بیشتر از ۵۰ کاراکتر باشد')
    ])
    
    last_name = StringField('نام خانوادگی', validators=[
        DataRequired(message='نام خانوادگی الزامی است'),
        Length(max=50, message='نام خانوادگی نمی‌تواند بیشتر از ۵۰ کاراکتر باشد')
    ])
    
    username = StringField('نام کاربری', validators=[
        DataRequired(message='نام کاربری الزامی است'),
        Length(min=3, max=80, message='نام کاربری باید بین ۳ تا ۸۰ کاراکتر باشد'),
        Regexp(r'^[a-zA-Z0-9_]+$', message='نام کاربری فقط می‌تواند شامل حروف انگلیسی، اعداد و underline باشد')
    ])
    
    password = PasswordField('رمز عبور جدید', validators=[
        Length(min=6, message='رمز عبور باید حداقل ۶ کاراکتر باشد')
    ])  # ❌ بدون DataRequired چون اختیاری هست
    
    mobile = StringField('موبایل', validators=[
        DataRequired(message='شماره موبایل الزامی است'),
        Length(min=11, max=11, message='شماره موبایل باید ۱۱ رقم باشد'),
        Regexp(r'^09[0-9]{9}$', message='فرمت شماره موبایل صحیح نیست (باید با 09 شروع شود)')
    ])

    organization = SelectField('سازمان', coerce=int, validators=[
        DataRequired(message='انتخاب سازمان الزامی است'),
        NumberRange(min=1, message='لطفاً سازمان را انتخاب کنید')
    ])
    
    area = SelectField('ناحیه', coerce=int, validators=[
        DataRequired(message='انتخاب ناحیه الزامی است'),
        NumberRange(min=1, message='لطفاً ناحیه را انتخاب کنید')
    ])
    
    position = SelectField('سمت', coerce=int, validators=[
        DataRequired(message='انتخاب سمت الزامی است'),
        NumberRange(min=1, message='لطفاً سمت را انتخاب کنید')
    ])

    submit = SubmitField('بروزرسانی کاربر')