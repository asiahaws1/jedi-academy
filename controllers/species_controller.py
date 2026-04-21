from flask import jsonify, request

from db import db
from models.species import Species, species_schema, species_many_schema
from util.reflection import populate_object
from lib.authenticate import require_rank


@require_rank('master')
def add_species(auth_info):
    post_data = request.form if request.form else request.get_json() or {}

    required = ['species_name', 'homeworld']
    for field in required:
        if not post_data.get(field):
            return jsonify({"message": f"{field} is required"}), 400

    if db.session.query(Species).filter(Species.species_name == post_data['species_name']).first():
        return jsonify({"message": "species already documented"}), 400

    new_species = Species.new_species_obj()
    populate_object(new_species, post_data)

    try:
        db.session.add(new_species)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to document species"}), 400

    return jsonify({"message": "species documented", "result": species_schema.dump(new_species)}), 201


@require_rank('youngling')
def get_species_by_id(species_id, auth_info):
    species = db.session.query(Species).filter(Species.species_id == species_id).first()
    if not species:
        return jsonify({"message": f"species {species_id} not found"}), 404
    return jsonify({"message": "species found", "result": species_schema.dump(species)}), 200
