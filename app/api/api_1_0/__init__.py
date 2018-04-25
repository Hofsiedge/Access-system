from flask import Blueprint

api = Blueprint('api', __name__)

from .. import authentication, users
from . import ajax_handling
