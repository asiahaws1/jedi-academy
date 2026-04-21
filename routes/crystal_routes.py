from flask import Blueprint

import controllers


crystals = Blueprint('crystals', __name__)


@crystals.route('/crystal', methods=['POST'])
def add_crystal_route():
    return controllers.add_crystal()


@crystals.route('/crystals/<rarity_level>', methods=['GET'])
def get_crystals_by_rarity_route(rarity_level):
    return controllers.get_crystals_by_rarity(rarity_level)
