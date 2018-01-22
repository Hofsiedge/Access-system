from flask import render_template, session, redirect, url_for, request
from . import main
from .forms import RegistrationForm
from .. import db
from ..models import create_user, Role, User, save_pass, save_day


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@main.route('/history', methods=['GET', 'POST'])
def show_table():
    return render_template('show_table.html')

@main.route('/registration', methods=['POST', 'GET'])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        form.username.data = ''
        name = form.name.data
        form.name.data = ''
        surname = form.surname.data
        form.surname.data = ''
        patronymic = form.patronymic.data
        form.patronymic.data = ''
        #TODO: e-mail
        role = Role.query.filter_by(id=int(form.role.data)).first()
        print(int(form.role.data), role)
        create_user(username, name, surname, patronymic, role)
        return redirect(url_for('.registration'))
    return render_template('registration.html', form=form)

commands = {
    1024: lambda: 'Connection is fine', # Test connection command
    1365: save_day # The end of the day command
}

@main.route('/command', methods=['POST'])
def command():
    print(request)
    command = int(request.form['command'])
    if command in commands:
        return commands[command]()
    else:
        #FIXME
        save_pass(command)
        user = User.query.filter_by(id=command).first()
        return repr(user)
