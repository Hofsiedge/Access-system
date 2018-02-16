from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField,\
        ValidationError
from wtforms.validators import Required, Email, Length, EqualTo
from ..models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    password = PasswordField('Пароль', validators=[Required()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    name = StringField('Имя', validators=[Required(), Length(1, 64)])
    surname = StringField('Фамилия', validators=[Required(), Length(1, 64)])
    patronymic = StringField('Отчество', validators=[Required(), Length(1, 64)])
    role =  SelectField('Кто Вы?', choices=[('3', 'Ученик'),
                                            ('4', 'Родитель'),
                                            ('2', 'Учитель')])
    email = StringField('Адрес электронной почты', validators=[Email(), Required(),
                                                               Length(1, 64)])
    password = PasswordField('Пароль', validators=[Required(), Length(1, 64),
                             EqualTo('password2', message='Пароли должны совпадать.')])
    password2 = PasswordField('Повторите пароль', validators=[Required()])
    submit = SubmitField('Подтвердить')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email занят')


class GoToRegistrationForm(FlaskForm):
    submit = SubmitField('Зарегистрироваться')

# TODO: Написать дополнительную форму для Parent

