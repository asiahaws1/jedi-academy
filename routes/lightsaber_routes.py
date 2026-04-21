from flask import Blueprint

import controllers


lightsabers = Blueprint('lightsabers', __name__)


@lightsabers.route('/lightsaber', methods=['POST'])
def add_lightsaber_route():
    return controllers.add_lightsaber()


@lightsabers.route('/lightsaber/<owner_id>', methods=['GET'])
def get_lightsabers_by_owner_route(owner_id):
    return controllers.get_lightsabers_by_owner(owner_id)


@lightsabers.route('/lightsaber/<saber_id>', methods=['PUT'])
def update_lightsaber_route(saber_id):
    return controllers.update_lightsaber(saber_id)


@lightsabers.route('/lightsaber/<saber_id>', methods=['DELETE'])
def delete_lightsaber_route(saber_id):
    return controllers.delete_lightsaber(saber_id)
