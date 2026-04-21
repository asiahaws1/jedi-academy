from flask import Blueprint

import controllers


auth = Blueprint('auth', __name__)


@auth.route('/user/auth', methods=['POST'])
def auth_login_route():
    return controllers.auth_token_add()


@auth.route('/user/auth/refresh', methods=['PUT'])
def auth_refresh_route():
    return controllers.auth_token_refresh()


@auth.route('/user/auth', methods=['DELETE'])
def auth_logout_route():
    return controllers.auth_token_delete()
