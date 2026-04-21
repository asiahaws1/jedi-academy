from flask import jsonify, request

from db import db
from models.crystals import Crystals, crystal_schema, crystals_schema
from util.reflection import populate_object
from lib.authenticate import require_rank


@require_rank('master')
def add_crystal(auth_info):
    post_data = request.form if request.form else request.get_json() or {}

    required = ['crystal_type', 'origin_planet']
    for field in required:
        if not post_data.get(field):
            return jsonify({"message": f"{field} is required"}), 400

    if db.session.query(Crystals).filter(Crystals.crystal_type == post_data['crystal_type']).first():
        return jsonify({"message": "crystal already cataloged"}), 400

    new_crystal = Crystals.new_crystal_obj()
    populate_object(new_crystal, post_data)

    try:
        db.session.add(new_crystal)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to catalog crystal"}), 400

    return jsonify({"message": "crystal cataloged", "result": crystal_schema.dump(new_crystal)}), 201


@require_rank('master')
def get_crystals_by_rarity(rarity_level, auth_info):
    crystals = db.session.query(Crystals).filter(Crystals.rarity_level == rarity_level).all()
    return jsonify({"message": "crystals found", "results": crystals_schema.dump(crystals)}), 200
