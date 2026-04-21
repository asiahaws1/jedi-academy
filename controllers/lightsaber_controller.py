from flask import jsonify, request

from db import db
from models.lightsabers import Lightsabers, lightsaber_schema, lightsabers_schema
from models.crystals import Crystals
from models.users import Users
from util.reflection import populate_object
from lib.authenticate import require_rank, authenticate_return_auth, rank_at_least


@require_rank('padawan')
def add_lightsaber(auth_info):
    post_data = request.form if request.form else request.get_json() or {}

    required = ['saber_name', 'hilt_material', 'blade_color']
    for field in required:
        if not post_data.get(field):
            return jsonify({"message": f"{field} is required"}), 400

    owner_id = post_data.get('owner_id') or str(auth_info.user_id)
    post_data['owner_id'] = owner_id

    owner = db.session.query(Users).filter(Users.user_id == owner_id).first()
    if not owner:
        return jsonify({"message": "owner does not exist"}), 400

    if str(owner_id) != str(auth_info.user_id) and not rank_at_least(auth_info.user.force_rank, 'council'):
        return jsonify({"message": "cannot build a lightsaber for another user"}), 403

    if db.session.query(Lightsabers).filter(Lightsabers.saber_name == post_data['saber_name']).first():
        return jsonify({"message": "saber_name already exists"}), 400

    crystal_id = post_data.get('crystal_id')
    if crystal_id:
        crystal = db.session.query(Crystals).filter(Crystals.crystal_id == crystal_id).first()
        if not crystal:
            return jsonify({"message": "crystal does not exist"}), 400

    new_saber = Lightsabers.new_saber_obj()
    populate_object(new_saber, post_data)

    try:
        db.session.add(new_saber)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to begin construction"}), 400

    return jsonify({"message": "lightsaber construction begun", "result": lightsaber_schema.dump(new_saber)}), 201


@authenticate_return_auth
def get_lightsabers_by_owner(owner_id, auth_info):
    owner = db.session.query(Users).filter(Users.user_id == owner_id).first()
    if not owner:
        return jsonify({"message": f"owner {owner_id} not found"}), 404

    sabers = db.session.query(Lightsabers).filter(Lightsabers.owner_id == owner_id).all()
    return jsonify({"message": "lightsabers found", "results": lightsabers_schema.dump(sabers)}), 200


@authenticate_return_auth
def update_lightsaber(saber_id, auth_info):
    saber = db.session.query(Lightsabers).filter(Lightsabers.saber_id == saber_id).first()
    if not saber:
        return jsonify({"message": f"lightsaber {saber_id} not found"}), 404

    if str(saber.owner_id) != str(auth_info.user_id):
        return jsonify({"message": "only the owner may update this lightsaber"}), 403

    post_data = request.form if request.form else request.get_json() or {}

    if 'saber_name' in post_data and post_data['saber_name']:
        conflict = db.session.query(Lightsabers).filter(Lightsabers.saber_name == post_data['saber_name'], Lightsabers.saber_id != saber_id).first()
        if conflict:
            return jsonify({"message": "saber_name already exists"}), 400
    if 'crystal_id' in post_data and post_data['crystal_id']:
        crystal = db.session.query(Crystals).filter(Crystals.crystal_id == post_data['crystal_id']).first()
        if not crystal:
            return jsonify({"message": "crystal does not exist"}), 400

    populate_object(saber, post_data)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to update lightsaber"}), 400

    return jsonify({"message": "lightsaber updated", "result": lightsaber_schema.dump(saber)}), 200


@authenticate_return_auth
def delete_lightsaber(saber_id, auth_info):
    saber = db.session.query(Lightsabers).filter(Lightsabers.saber_id == saber_id).first()
    if not saber:
        return jsonify({"message": f"lightsaber {saber_id} not found"}), 404

    is_owner = str(saber.owner_id) == str(auth_info.user_id)
    if not is_owner and not rank_at_least(auth_info.user.force_rank, 'council'):
        return jsonify({"message": "unauthorized"}), 403

    try:
        db.session.delete(saber)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to destroy lightsaber"}), 400

    return jsonify({"message": "lightsaber destroyed"}), 200
