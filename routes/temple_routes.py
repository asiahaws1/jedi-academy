from flask import Blueprint

import controllers


temples = Blueprint('temples', __name__)


@temples.route('/temple', methods=['POST'])
def add_temple_route():
    return controllers.add_temple()


@temples.route('/temple/<temple_id>', methods=['GET'])
def get_temple_route(temple_id):
    return controllers.get_temple_by_id(temple_id)


@temples.route('/temple/<temple_id>', methods=['PUT'])
def update_temple_route(temple_id):
    return controllers.update_temple_by_id(temple_id)


@temples.route('/temple/<temple_id>', methods=['DELETE'])
def delete_temple_route(temple_id):
    return controllers.deactivate_temple(temple_id)
