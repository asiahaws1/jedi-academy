from flask import Blueprint

import controllers


padawans = Blueprint('padawans', __name__)


@padawans.route('/padawan', methods=['POST'])
def add_padawan_route():
    return controllers.add_padawan()


@padawans.route('/padawans', methods=['GET'])
def get_padawans_route():
    return controllers.get_padawans_in_temple()


@padawans.route('/padawans/active', methods=['GET'])
def get_active_padawans_route():
    return controllers.get_active_padawans()


@padawans.route('/padawan/<padawan_id>', methods=['PUT'])
def update_padawan_route(padawan_id):
    return controllers.update_padawan_by_id(padawan_id)


@padawans.route('/padawan/<padawan_id>/promote', methods=['PUT'])
def promote_padawan_route(padawan_id):
    return controllers.promote_padawan(padawan_id)


@padawans.route('/padawan/<padawan_id>', methods=['DELETE'])
def delete_padawan_route(padawan_id):
    return controllers.delete_padawan_by_id(padawan_id)
