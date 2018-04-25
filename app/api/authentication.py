from flask_httpauth import HTTPBasicAuth
from flask import g, jsonify
from .api_1_0 import api
from .errors import unauthorized, forbidden
from ..models import User, AnonymousUser

auth = HTTPBasicAuth()

# TODO: HTTPS

@auth.verify_password
def verify_password(email_or_token, password):
    print('email_or_token:', email_or_token, 'pw:', password)
    if email_or_token == '':
        g.current_user = AnonymousUser()
        # g.authenticated = False
        return False # As there is nothing public in API
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        # g.authenticated = False
        return False
    g.current_user = user
    g.token_used = False
    if user.verify_password(password):
        # g.authenticated = True
        g.token = g.current_user.generate_auth_token(expiration=3600)
        return True
    return False

@auth.error_handler
def auth_error():
    return unauthorized('Неверный логин или пароль')

@api.before_request
@auth.login_required
def before_request():
    if not g.current_user.is_anonymous \
       and not g.current_user.confirmed:
        return forbidden('Аккаунт не подтверждён')
    # print('Auth Token:', g.get('token'))


@api.route('/token')
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Неверный логин или пароль')
    return jsonify({
        'token': g.current_user.generate_auth_token(expiration=3600).decode('utf-8'),
        'expiration': 3600})

