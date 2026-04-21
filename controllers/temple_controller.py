from flask import jsonify, request

from db import db
from models.temples import Temples, temple_schema, temples_schema
from models.users import Users
from util.reflection import populate_object
from lib.authenticate import require_rank, authenticate_return_auth


@require_rank('grand_master')
def add_temple(auth_info):
    post_data = request.form if request.form else request.get_json() or {}

    required = ['temple_name', 'planet']
    for field in required:
        if not post_data.get(field):
            return jsonify({"message": f"{field} is required"}), 400

    if db.session.query(Temples).filter(Temples.temple_name == post_data['temple_name']).first():
        return jsonify({"message": "temple name already exists"}), 400

    new_temple = Temples.new_temple_obj()
    populate_object(new_temple, post_data)

    try:
        db.session.add(new_temple)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to create temple"}), 400

    return jsonify({"message": "temple established", "result": temple_schema.dump(new_temple)}), 201


@authenticate_return_auth
def get_temple_by_id(temple_id, auth_info):
    temple = db.session.query(Temples).filter(Temples.temple_id == temple_id).first()
    if not temple:
        return jsonify({"message": f"temple {temple_id} not found"}), 404
    return jsonify({"message": "temple found", "result": temple_schema.dump(temple)}), 200


@require_rank('grand_master')
def update_temple_by_id(temple_id, auth_info):
    temple = db.session.query(Temples).filter(Temples.temple_id == temple_id).first()
    if not temple:
        return jsonify({"message": f"temple {temple_id} not found"}), 404

    post_data = request.form if request.form else request.get_json() or {}

    if 'temple_name' in post_data and post_data['temple_name']:
        conflict = db.session.query(Temples).filter(Temples.temple_name == post_data['temple_name'], Temples.temple_id != temple_id).first()
        if conflict:
            return jsonify({"message": "temple name already exists"}), 400

    populate_object(temple, post_data)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to update temple"}), 400

    return jsonify({"message": "temple updated", "result": temple_schema.dump(temple)}), 200


@require_rank('grand_master')
def deactivate_temple(temple_id, auth_info):
    temple = db.session.query(Temples).filter(Temples.temple_id == temple_id).first()
    if not temple:
        return jsonify({"message": f"temple {temple_id} not found"}), 404

    temple.is_active = False
    members = db.session.query(Users).filter(Users.temple_id == temple_id).all()
    for member in members:
        member.temple_id = None

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to deactivate temple"}), 400

    return jsonify({"message": "temple deactivated, members relocated"}), 200
