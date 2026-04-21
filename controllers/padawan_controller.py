from flask import jsonify, request
from datetime import datetime

from db import db
from models.padawans import Padawans, padawan_schema, padawans_schema
from models.users import Users
from models.masters import Masters
from models.species import Species
from util.reflection import populate_object
from lib.authenticate import require_rank, authenticate_return_auth, rank_at_least


@require_rank('master')
def add_padawan(auth_info):
    post_data = request.form if request.form else request.get_json() or {}

    required = ['user_id', 'padawan_name', 'age']
    for field in required:
        if post_data.get(field) in (None, ''):
            return jsonify({"message": f"{field} is required"}), 400

    user = db.session.query(Users).filter(Users.user_id == post_data['user_id']).first()
    if not user:
        return jsonify({"message": "user does not exist"}), 400

    if db.session.query(Padawans).filter(Padawans.user_id == post_data['user_id']).first():
        return jsonify({"message": "user is already a padawan"}), 400

    if db.session.query(Padawans).filter(Padawans.padawan_name == post_data['padawan_name']).first():
        return jsonify({"message": "padawan_name already taken"}), 400

    master_id = post_data.get('master_id')
    if master_id:
        master = db.session.query(Masters).filter(Masters.master_id == master_id).first()
        if not master:
            return jsonify({"message": "master does not exist"}), 400
        current_padawans = db.session.query(Padawans).filter(Padawans.master_id == master_id).count()
        if current_padawans >= master.max_padawans:
            return jsonify({"message": "master is at padawan capacity"}), 400

    species_id = post_data.get('species_id')
    if species_id:
        species = db.session.query(Species).filter(Species.species_id == species_id).first()
        if not species:
            return jsonify({"message": "species does not exist"}), 400

    new_padawan = Padawans.new_padawan_obj()
    populate_object(new_padawan, post_data)

    if user.force_rank == 'youngling':
        user.force_rank = 'padawan'

    try:
        db.session.add(new_padawan)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to create padawan"}), 400

    return jsonify({"message": "padawan created", "result": padawan_schema.dump(new_padawan)}), 201


@require_rank('master')
def get_padawans_in_temple(auth_info):
    temple_id = auth_info.user.temple_id
    if not temple_id:
        return jsonify({"message": "user not assigned to a temple", "results": []}), 200

    padawans = (
        db.session.query(Padawans)
        .join(Users, Padawans.user_id == Users.user_id)
        .filter(Users.temple_id == temple_id)
        .all()
    )
    return jsonify({"message": "padawans found", "results": padawans_schema.dump(padawans)}), 200


@authenticate_return_auth
def get_active_padawans(auth_info):
    padawans = db.session.query(Padawans).filter(Padawans.graduation_date.is_(None)).all()
    return jsonify({"message": "active padawans found", "results": padawans_schema.dump(padawans)}), 200


@authenticate_return_auth
def update_padawan_by_id(padawan_id, auth_info):
    padawan = db.session.query(Padawans).filter(Padawans.padawan_id == padawan_id).first()
    if not padawan:
        return jsonify({"message": f"padawan {padawan_id} not found"}), 404

    is_assigned_master = False
    if padawan.master_id:
        master = db.session.query(Masters).filter(Masters.master_id == padawan.master_id).first()
        if master and str(master.user_id) == str(auth_info.user_id):
            is_assigned_master = True

    if not is_assigned_master and not rank_at_least(auth_info.user.force_rank, 'council'):
        return jsonify({"message": "unauthorized"}), 403

    post_data = request.form if request.form else request.get_json() or {}

    if 'padawan_name' in post_data and post_data['padawan_name']:
        conflict = db.session.query(Padawans).filter(Padawans.padawan_name == post_data['padawan_name'], Padawans.padawan_id != padawan_id).first()
        if conflict:
            return jsonify({"message": "padawan_name already taken"}), 400
    if 'master_id' in post_data and post_data['master_id']:
        master = db.session.query(Masters).filter(Masters.master_id == post_data['master_id']).first()
        if not master:
            return jsonify({"message": "master does not exist"}), 400
    if 'species_id' in post_data and post_data['species_id']:
        species = db.session.query(Species).filter(Species.species_id == post_data['species_id']).first()
        if not species:
            return jsonify({"message": "species does not exist"}), 400

    populate_object(padawan, post_data)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to update padawan"}), 400

    return jsonify({"message": "padawan updated", "result": padawan_schema.dump(padawan)}), 200


@require_rank('council')
def promote_padawan(padawan_id, auth_info):
    padawan = db.session.query(Padawans).filter(Padawans.padawan_id == padawan_id).first()
    if not padawan:
        return jsonify({"message": f"padawan {padawan_id} not found"}), 404

    padawan.graduation_date = datetime.utcnow()
    user = db.session.query(Users).filter(Users.user_id == padawan.user_id).first()
    if user:
        user.force_rank = 'knight'

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to promote padawan"}), 400

    return jsonify({"message": "padawan promoted to knight", "result": padawan_schema.dump(padawan)}), 200


@require_rank('council')
def delete_padawan_by_id(padawan_id, auth_info):
    padawan = db.session.query(Padawans).filter(Padawans.padawan_id == padawan_id).first()
    if not padawan:
        return jsonify({"message": f"padawan {padawan_id} not found"}), 404

    try:
        db.session.delete(padawan)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to delete padawan"}), 400

    return jsonify({"message": "padawan removed"}), 200
