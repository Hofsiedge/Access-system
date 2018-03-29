from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField
from wtforms.validators import Required, Email, Length, Regexp


class EditProfileForm(FlaskForm):
    surname = StringField('Фамилия', validators=[Length(1,64)])
    name = StringField('Имя', validators=[Length(1,64)])
    patronymic = StringField('Отчество', validators=[Length(1,64)])
    submit = SubmitField('Подтвердить')


class EditProfileAdminForm(FlaskForm):
    surname = StringField('Фамилия', validators=[Length(1,64)])
    name = StringField('Имя', validators=[Length(1,64)])
    patronymic = StringField('Отчество', validators=[Length(1,64)])
    email = StringField('Email', validators=[Required(),
                                             Length(1, 64), Email()])
    confirmed = BooleanField('Подтверждён')
    role = SelectField('Роль', coerce=int)

    def __init__(self, rolename):
        if rolename == 'Pupil':
            self.form = SelectField('Класс')
            # TODO: AJAX StringFields with div for search
            self.parent = StringField('#')
        elif rolename == 'Parent':
            self.pupil = StringField('#')
        elif rolename == 'Teacher':
            self.forms = StringField('#')
            self.subjects = StringField('#') # Multiselect field
        elif rolename == 'Headteacher':
            # TODO:
            pass

        self.submit = SubmitField('Подтвердить')

            
class DBForm(FlaskForm):
    day = StringField('Date (YYYY-MM-DD)')
    user_id = StringField('User id')
    submit = SubmitField('Confirm')


class CreatePassingForm(FlaskForm):
    user_id = StringField('User id', validators=[Required(), Regexp(r'^\d+$')])
    date = StringField('Date', validators=[Regexp(r'^\d{4}-\d{2}-\d{2}$', message='Date must be formatted as YYYY-MM-DD'), Required()])
    # TODO: Validator for time format checking
    time = StringField('Time (HH:MM:SS)', validators=[Regexp(regex=r'^\d{2}:\d{2}:\d{2}$', message='Wrong format'), Length(8, 8), Required()])
    submit = SubmitField('Confirm')
