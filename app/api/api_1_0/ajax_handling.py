from flask import g
from . import api
from .decorators import permission_required, allowed_to_read #, private
from ..authentication import auth
from ...models import User, Permission 

@api.route('/passings/<int:user_id>/<int:day_id>')
# @private
@allowed_to_read
def get_passings(user_id, day_id):
    return str(User.get_passings(user_id, day_id))

