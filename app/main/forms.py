from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField
from wtforms.validators import Required, Email, Length


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

            

