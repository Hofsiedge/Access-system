from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Required, Email

class RegistrationForm(FlaskForm):
    name = StringField('Имя', validators=[Required()])
    surname = StringField('Фамилия', validators=[Required()])
    patronymic = StringField('Отчество', validators=[Required()])
    email = StringField('Адрес электронной почты', validators=[Email()])
    role =  SelectField('Кто Вы?', choices=[('3', 'Ученик'),
                                            ('4', 'Родитель'),
                                            ('2', 'Учитель')])
    submit = SubmitField('Подтвердить')
# TODO: Написать дополнительную форму для Parent

