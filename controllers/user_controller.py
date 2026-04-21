from flask import jsonify, request
from flask_bcrypt import generate_password_hash

from db import db
from models.users import Users, VALID_RANKS, user_schema, users_schema
from models.temples import Temples
from util.reflection import populate_object
from lib.authenticate import authenticate_return_auth, require_rank, rank_at_least


def add_user():
    post_data = request.form if request.form else request.get_json() or {}

    required = ['username', 'email', 'password']
    for field in required:
        if not post_data.get(field):
            return jsonify({"message": f"{field} is required"}), 400

    if db.session.query(Users).filter(Users.email == post_data['email']).first():
        return jsonify({"message": "email already registered"}), 400

    if db.session.query(Users).filter(Users.username == post_data['username']).first():
        return jsonify({"message": "username already taken"}), 400

    force_rank = (post_data.get('force_rank') or 'youngling').lower()
    if force_rank not in VALID_RANKS:
        return jsonify({"message": f"invalid force_rank; must be one of {sorted(VALID_RANKS)}"}), 400
    post_data['force_rank'] = force_rank

    temple_id = post_data.get('temple_id')
    if temple_id:
        temple = db.session.query(Temples).filter(Temples.temple_id == temple_id).first()
        if not temple:
            return jsonify({"message": "temple does not exist"}), 400

    new_user = Users.new_user_obj()
    populate_object(new_user, post_data)

    new_user.password = generate_password_hash(post_data['password']).decode('utf8')

    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to create user"}), 400

    return jsonify({"message": "user created", "result": user_schema.dump(new_user)}), 201


@require_rank('council')
def users_get_all(auth_info):
    users_query = db.session.query(Users).all()
    return jsonify({"message": "users found", "results": users_schema.dump(users_query)}), 200


@authenticate_return_auth
def user_profile(auth_info):
    user = db.session.query(Users).filter(Users.user_id == auth_info.user_id).first()
    if not user:
        return jsonify({"message": "user not found"}), 404
    return jsonify({"message": "profile", "result": user_schema.dump(user)}), 200


@authenticate_return_auth
def update_user_by_id(user_id, auth_info):
    user = db.session.query(Users).filter(Users.user_id == user_id).first()
    if not user:
        return jsonify({"message": f"user {user_id} not found"}), 404

    is_self = str(auth_info.user_id) == str(user_id)
    is_council_plus = rank_at_least(auth_info.user.force_rank, 'council')

    if not is_self and not is_council_plus:
        return jsonify({"message": "unauthorized"}), 403

    post_data = request.form if request.form else request.get_json() or {}

    if 'username' in post_data and post_data['username']:
        conflict = db.session.query(Users).filter(Users.username == post_data['username'], Users.user_id != user_id).first()
        if conflict:
            return jsonify({"message": "username already taken"}), 400

    if 'email' in post_data and post_data['email']:
        conflict = db.session.query(Users).filter(Users.email == post_data['email'], Users.user_id != user_id).first()
        if conflict:
            return jsonify({"message": "email already registered"}), 400

    if 'force_rank' in post_data and post_data['force_rank']:
        if not is_council_plus:
            return jsonify({"message": "only council+ may change force_rank"}), 403
        new_rank = post_data['force_rank'].lower()
        if new_rank not in VALID_RANKS:
            return jsonify({"message": "invalid force_rank"}), 400
        post_data['force_rank'] = new_rank

    if 'temple_id' in post_data and post_data['temple_id']:
        temple = db.session.query(Temples).filter(Temples.temple_id == post_data['temple_id']).first()
        if not temple:
            return jsonify({"message": "temple does not exist"}), 400

    new_password = post_data.pop('password', None) if isinstance(post_data, dict) else None

    populate_object(user, post_data)

    if new_password:
        user.password = generate_password_hash(new_password).decode('utf8')

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to update user"}), 400

    return jsonify({"message": "user updated", "result": user_schema.dump(user)}), 200


@require_rank('grand_master')
def delete_user_by_id(user_id, auth_info):
    user = db.session.query(Users).filter(Users.user_id == user_id).first()
    if not user:
        return jsonify({"message": f"user {user_id} not found"}), 404

    try:
        db.session.delete(user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to delete user"}), 400

    return jsonify({"message": "user deleted"}), 200
