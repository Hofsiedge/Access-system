from flask import render_template, session, redirect, url_for
from . import main
from .forms import RegistrationForm
from .. import db
from ..models import create_user, Role


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

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

        role = Role.query.filter_by(id=int(form.role.data)).first()
        create_user(username, name, surname, patronymic, role)
        return redirect(url_for('.registration'))
    return render_template('registration.html', form=form)

