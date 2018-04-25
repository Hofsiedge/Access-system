from flask import render_template, session, redirect, url_for, request, abort, flash, jsonify, make_response, g
from flask_login import login_required, current_user
import datetime
from . import main
from .forms import EditProfileForm, DBForm, CreatePassingForm, SaveDayForm
from .. import db
from ..models import Role, User, Day, Class, Passing, TimeInside, repr_history 
from ..decorators import permission_required, admin_required


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@main.route('/history', methods=['GET', 'POST'])
@login_required
def show_table():
    form = DBForm()
    history = {}
    for i in TimeInside.query.all():
        if i.user in history:
            history[i.user].append(i)
        else:
            history[i.user] = [i]
    meta_list = [str([i.id for i in history])[1:-1],
                 ', '.join([str(i.day.id) for i in history[list(history.keys())[0]]])] \
            if history else []
    days = [i for i in list(history.values())[0]] if history else []
    resp = make_response(render_template('show_table.html', form=form, history=history, meta_list=meta_list, days=days))
    resp.set_cookie('auth_token', (g.get('token') or ''))
    return resp
    # TODO: cookies added, need to add requests in show_table authorizing with JS

# TODO: API for serving AJAX requests
@main.route('/table', methods=['POST'])
@login_required
def get_DB():
    form = DBForm()
    if form.validate_on_submit():
        day = Day.query.filter_by(date=datetime.date(*list(map(int, form.day.data.split('-'))))).first()
        user = User.query.get_or_404(form.user_id.data)
        res = TimeInside.query.filter_by(day=day, user=user).all()
        return jsonify(data={'message': res})
    return jsonify(data=form.errors)

@main.route('/admin_tab', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_tab():
    # TODO: add forms for other models
    PC_form = CreatePassingForm()
    if PC_form.validate_on_submit():
        Passing.create_passing(user_id=int(PC_form.user_id.data),
                               day=list(map(int, PC_form.date.data.split('-'))),
                               time=list(map(int, PC_form.time.data.split(':'))))
        PC_form.user_id.data = ''
        PC_form.date.data = ''
        PC_form.time.data = ''
        return redirect(url_for('main.admin_tab'))
    SD_form = SaveDayForm()
    if SD_form.validate_on_submit():
        Day.query.get(SD_form.day_id.data).save_day()
        SD_form.day_id.data = ''
        return redirect(url_for('main.admin_tab'))

    return render_template('admin_tab.html', tables=[Day, User, Role, Class, Passing, TimeInside],
                           user_quantity=len(User.query.all()), passing_create_form=PC_form,
                           save_day_form=SD_form)

commands = {
    1024: lambda: 'Connection is fine',     # Test connection command
    1365: TimeInside.compute_total_inside   # The end of the day command
}

# TODO: access only for special group of accounts
# TODO: make an account for school client
@main.route('/command', methods=['POST'])
def command():
    print(request)
    command = int(request.form['command'])
    if command in commands:
        return commands[command]()
    else:
        Passing.save_pass(command)
        user = User.query.get_or_404(id=command)
        return repr(user)

@main.route('/user/<userid>')
def profile(userid):
    user = User.query.get(userid)
    if user is None:
        abort(404)
    return render_template('user.html', user=user)

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.surname = form.surname.data
        current_user.patronymic = form.patronymic.data
        db.session.add(current_user)
        flash('Ваш профиль обновлён.')
        return redirect(url_for('main.profile', userid=current_user.id))
    form.surname.data = current_user.surname
    form.name.data = current_user.name
    form.patronymic.data = current_user.patronymic
    return render_template('edit_profile.html', form=form)
