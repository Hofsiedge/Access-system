from functools import wraps
from flask import g
from ..errors import forbidden

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user.can(permission):
                return forbidden('Недостаточно прав')
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def allowed_to_read(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if g.current_user.can_read(kwargs['user_id']):
            return f(*args, **kwargs)
        return forbidden('Недостаточно прав')
    return decorator

# def private(f):
#     @wraps(f)
#     def decorator(*args, **kwargs):
#         if g.authenticated:
#             return f(*args, **kwargs)
#         return forbidden('private - Необходима авторизация')
#     return decorator
