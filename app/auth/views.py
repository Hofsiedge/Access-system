import base64
from flask import render_template, redirect, request, url_for, flash, g
from flask_login import login_user, login_required, logout_user, current_user
from . import auth
from .. import db
from ..models import User, Role, AnonymousUser
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, \
        PasswordResetForm, PasswordResetRequestForm, ChangeEmailForm
from ..email import send_email
from ..decorators import permission_required, admin_required
from .. import login_manager


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Неверный логин или пароль.')
    return render_template('auth/login.html', form=form)

@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('Вы вышли из учетной записи.')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    password=form.password.data,
                    name=form.name.data,
                    surname=form.surname.data,
                    patronymic=form.patronymic.data,
                    role=Role.query.filter_by(id=form.role.data).first())
        form.email.data = ''
        form.password.data = ''
        form.name.data = ''
        form.surname.data = ''
        form.patronymic.data = ''
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Подтвердите&#160;создание&#160;учётной&#160;записи',
                  'auth/email/confirm', user=user, token=token)
        flash('На Ваш адрес электронной почты было выслано письмо для подтверждения.')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('Ваш аккаунт подтверждён. Спасибо!')
    else:
        flash('Ссылка для подтверждения неверна или её срок действия истёк.')
    return redirect(url_for('main.index'))

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed and request.endpoint[:5] != 'auth.':
            return redirect(url_for('auth.unconfirmed'))
        if current_user is not AnonymousUser and not g.get('token'):
            # FIXME: "Basic ..." remove "
            g.token = 'Basic ' + base64.b64encode(bytes(current_user.generate_auth_token(expiration=3600).decode('utf-8') + ':', 'utf-8')).decode('utf-8')
        # print('Token:', g.get('token'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.confirmed or current_user.is_anonymous:
        return redirect(usr_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email,'Подтвердите&#160;Вашу&#160;учётную&#160;запись',
                'auth/email/confirm', user=current_user, token=token)
    flash('Вам было выслано новое письмо для подтверждения аккаунта.')
    return redirect(url_for('main.index'))

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Пароль успешно изменён.')
            return redirect(url_for('main.index'))
        else:
            flash('Неверный пароль.')
            return redirect(url_for('auth.change_password'))
    return render_template("auth/change_password.html", form=form)

@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Смена&#160;пароля',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
            flash('Письмо для смены пароля было отправлено '
                  'на Ваш адрес электронной почты.')
            return redirect(url_for('auth.login'))
        flash('Пользователь с таким адресом электронной почты не обнаружен.')
        return redirect(url_for('auth.password_reset_request'))
    return render_template('auth/reset_password.html', form=form)

@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            flash('Ваш пароль обновлён.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)

@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Подверждение&#160;email',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('На Ваш адрес электронной почты было отправлено письмо '
                  'с инструкциями для подтверждения.')
            return redirect(url_for('main.index'))
        else:
            flash('Неверный пароль.')
    return render_template("auth/change_email.html", form=form)

@auth.route('/change_email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Ваш email изменён.')
    else:
        flash('Неверный запрос.')
    return redirect(url_for('main.index'))
