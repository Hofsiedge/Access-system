from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField,\
        ValidationError
from wtforms.validators import Required, Email, Length, EqualTo, DataRequired
from ..models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired(), Length(1, 64)])
    surname = StringField('Фамилия', validators=[DataRequired(), Length(1, 64)])
    patronymic = StringField('Отчество', validators=[DataRequired(), Length(1, 64)])

    # TODO: 'have no patronymic' option

    role =  SelectField('Кто Вы?', choices=[('3', 'Ученик'),
                                            ('4', 'Родитель'),
                                            ('2', 'Учитель')])
    email = StringField('Адрес электронной почты', validators=[Email(), DataRequired(),
                                                               Length(1, 64)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(1, 64),
                             EqualTo('password2', message='Пароли должны совпадать.')])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email занят')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Старый пароль', validators=[DataRequired()])
    password = PasswordField('Новый пароль', validators=[
        DataRequired(), EqualTo('password2', message='Пароли должны совпадать.')])
    password2 = PasswordField('Подтвердите новый пароль',
                              validators=[DataRequired()])
    submit = SubmitField('Сменить пароль')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Адрес электронной почты', validators=[
        DataRequired(), Length(1, 64), Email()])
    submit = SubmitField('Сменить пароль')


class PasswordResetForm(FlaskForm):
    password = PasswordField('Новый пароль', validators=[
        DataRequired(), EqualTo('password2', message='Пароли должны совпадать.')])
    password2 = PasswordField('Подтвердите новый пароль', validators=[DataRequired()])
    submit = SubmitField('Сохранить новый пароль')

# TODO: Написать дополнительную форму для Parent


class ChangeEmailForm(FlaskForm):
    email = StringField('Новый адрес электронной почты', validators=[
        DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Сменить email')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Данный адрес элетронной '
                                  'почты уже зарегистрирован.')
