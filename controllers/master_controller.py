from flask import jsonify, request

from db import db
from models.masters import Masters, master_schema, masters_schema
from models.users import Users
from models.padawans import Padawans
from util.reflection import populate_object
from lib.authenticate import require_rank, authenticate_return_auth, rank_at_least


@require_rank('council')
def add_master(auth_info):
    post_data = request.form if request.form else request.get_json() or {}

    required = ['user_id', 'master_name', 'specialization']
    for field in required:
        if not post_data.get(field):
            return jsonify({"message": f"{field} is required"}), 400

    user = db.session.query(Users).filter(Users.user_id == post_data['user_id']).first()
    if not user:
        return jsonify({"message": "user does not exist"}), 400

    if db.session.query(Masters).filter(Masters.user_id == post_data['user_id']).first():
        return jsonify({"message": "user already a master"}), 400

    if db.session.query(Masters).filter(Masters.master_name == post_data['master_name']).first():
        return jsonify({"message": "master_name already taken"}), 400

    new_master = Masters.new_master_obj()
    populate_object(new_master, post_data)

    user.force_rank = 'master'

    try:
        db.session.add(new_master)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to create master"}), 400

    return jsonify({"message": "user promoted to master", "result": master_schema.dump(new_master)}), 201


@require_rank('padawan')
def get_all_masters(auth_info):
    masters = db.session.query(Masters).all()
    return jsonify({"message": "masters found", "results": masters_schema.dump(masters)}), 200


@authenticate_return_auth
def update_master_by_id(master_id, auth_info):
    master = db.session.query(Masters).filter(Masters.master_id == master_id).first()
    if not master:
        return jsonify({"message": f"master {master_id} not found"}), 404

    is_self = str(master.user_id) == str(auth_info.user_id)
    if not is_self and not rank_at_least(auth_info.user.force_rank, 'council'):
        return jsonify({"message": "unauthorized"}), 403

    post_data = request.form if request.form else request.get_json() or {}

    if 'master_name' in post_data and post_data['master_name']:
        conflict = db.session.query(Masters).filter(Masters.master_name == post_data['master_name'], Masters.master_id != master_id).first()
        if conflict:
            return jsonify({"message": "master_name already taken"}), 400

    populate_object(master, post_data)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to update master"}), 400

    return jsonify({"message": "master updated", "result": master_schema.dump(master)}), 200


@require_rank('grand_master')
def delete_master_by_id(master_id, auth_info):
    master = db.session.query(Masters).filter(Masters.master_id == master_id).first()
    if not master:
        return jsonify({"message": f"master {master_id} not found"}), 404

    padawans = db.session.query(Padawans).filter(Padawans.master_id == master_id).all()
    for padawan in padawans:
        padawan.master_id = None

    user = db.session.query(Users).filter(Users.user_id == master.user_id).first()
    if user:
        user.force_rank = 'knight'

    try:
        db.session.delete(master)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to delete master"}), 400

    return jsonify({"message": "master removed, padawans reassigned"}), 200
