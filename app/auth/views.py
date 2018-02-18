from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from . import auth
from .. import db
from ..models import User, Role
from .forms import LoginForm, RegistrationForm, GoToRegistrationForm
from ..email import send_email

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    form2 = GoToRegistrationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Неверный логин или пароль.')
    if form2.validate_on_submit():
        return redirect(url_for('auth.register'))
    return render_template('auth/login.html', form=form, form2=form2)

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
        send_email(user.email, 'Подтвердите создание учётной записи',
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
    if current_user.is_authenticated \
       and not current_user.confirmed \
       and request.endpoint[:5] != 'auth.':
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.confirmed or current_user.is_anonymous:
        return redirect(usr_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email,'Подтвердите Вашу учётную запись',
                'auth/email/confirm', user=current_user, token=token)
    flash('Вам было выслано новое письмо для подтверждения аккаунта.')
    return redirect(url_for('main.index'))

