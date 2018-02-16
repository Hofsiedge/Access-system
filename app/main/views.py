from flask import render_template, session, redirect, url_for, request
from flask_login import login_required
from . import main
from .forms import RegistrationForm
from .. import db
from ..models import create_user, Role, User, Day, Class, save_pass, save_day, repr_history, get_dates


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@main.route('/history', methods=['GET', 'POST'])
@login_required
def show_table():
    return render_template('show_table.html')

@main.route('/registration', methods=['POST', 'GET'])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data
        form.email.data = ''
        name = form.name.data
        form.name.data = ''
        surname = form.surname.data
        form.surname.data = ''
        patronymic = form.patronymic.data
        form.patronymic.data = ''
        #TODO: e-mail
        role = Role.query.filter_by(id=int(form.role.data)).first()
        print(int(form.role.data), role)
        create_user(email, name, surname, patronymic, role)
        return redirect(url_for('.registration'))
    return render_template('registration.html', form=form)

@main.route('/admin_tab', methods=['GET', 'POST'])
@login_required
def admin_tab():
    return render_template('admin_tab.html', tables=[Day, User, Role, Class], dates=get_dates(), repr_history=repr_history, user_quantity=len(User.query.all()))

commands = {
    1024: lambda: 'Connection is fine', # Test connection command
    1365: save_day # The end of the day command
}

# TODO: access only for special group of accounts
@main.route('/command', methods=['POST'])
def command():
    print(request)
    command = int(request.form['command'])
    if command in commands:
        return commands[command]()
    else:
        save_pass(command)
        user = User.query.filter_by(id=command).first()
        return repr(user)
