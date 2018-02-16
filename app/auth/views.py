from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, logout_user
from . import auth
from .. import db
from ..models import User, Role
from .forms import LoginForm, RegistrationForm, GoToRegistrationForm

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
        db.session.add(user)
        db.session.commit()
        flash('Теперь вы можете войти в Вашу учётную запись.')
    return render_template('auth/register.html', form=form)

