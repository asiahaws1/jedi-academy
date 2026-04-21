from flask import jsonify, request
from flask_bcrypt import check_password_hash
from datetime import datetime, timedelta

from db import db
from models.auth_tokens import AuthTokens, auth_token_schema
from models.users import Users
from util.reflection import populate_object
from lib.authenticate import authenticate_return_auth, rank_value


RANK_SESSION_HOURS = {
    'youngling': 2,
    'padawan': 4,
    'knight': 8,
    'master': 12,
    'council': 24,
    'grand_master': 48,
}


def session_hours_for_rank(force_rank):
    return RANK_SESSION_HOURS.get((force_rank or 'youngling').lower(), 2)


def auth_token_add():
    post_data = request.form if request.form else request.get_json() or {}
    email = post_data.get('email')
    password = post_data.get('password')

    if not email or not password:
        return jsonify({"message": "email and password are required"}), 400

    user_query = db.session.query(Users).filter(Users.email == email).first()

    if not user_query:
        return jsonify({"message": "invalid credentials"}), 401

    if not user_query.is_active:
        return jsonify({"message": "user is inactive"}), 401

    if not check_password_hash(user_query.password, password):
        return jsonify({"message": "invalid credentials"}), 401

    now_datetime = datetime.now()
    expiration_datetime = now_datetime + timedelta(hours=session_hours_for_rank(user_query.force_rank))

    existing_tokens = db.session.query(AuthTokens).filter(AuthTokens.user_id == user_query.user_id).all()
    for token in existing_tokens:
        if token.expiration_date < now_datetime:
            db.session.delete(token)

    new_token = AuthTokens.new_token_obj()
    populate_object(new_token, {'user_id': user_query.user_id, 'expiration_date': expiration_datetime})

    try:
        db.session.add(new_token)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to create auth token"}), 400

    return jsonify({"message": "may the force be with you", "auth_info": auth_token_schema.dump(new_token)}), 201


@authenticate_return_auth
def auth_token_refresh(auth_info):
    new_expiration = datetime.now() + timedelta(hours=session_hours_for_rank(auth_info.user.force_rank))
    auth_info.expiration_date = new_expiration

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to refresh token"}), 400

    return jsonify({"message": "token refreshed", "auth_info": auth_token_schema.dump(auth_info)}), 200


@authenticate_return_auth
def auth_token_delete(auth_info):
    try:
        db.session.delete(auth_info)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to log out"}), 400

    return jsonify({"message": "logout successful"}), 200
