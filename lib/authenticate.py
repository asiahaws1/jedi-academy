import functools
from flask import jsonify, request
from datetime import datetime
from uuid import UUID

from db import db
from models.auth_tokens import AuthTokens


FORCE_RANKS = {
    'youngling': 1,
    'padawan': 2,
    'knight': 3,
    'master': 4,
    'council': 5,
    'grand_master': 6,
}


def rank_value(rank):
    if not rank:
        return 0
    return FORCE_RANKS.get(rank.lower(), 0)


def rank_at_least(user_rank, required_rank):
    return rank_value(user_rank) >= rank_value(required_rank)


def validate_uuid4(uuid_string):
    try:
        UUID(str(uuid_string), version=4)
        return True
    except Exception:
        return False


def validate_token():
    auth_token = request.headers.get('Authorization') or request.headers.get('auth')

    if not auth_token or not validate_uuid4(auth_token):
        return False

    existing_token = db.session.query(AuthTokens).filter(AuthTokens.auth_token == auth_token).first()

    if existing_token and existing_token.expiration_date > datetime.now():
        return existing_token

    return False


def fail_response():
    return jsonify({"message": "authentication required"}), 401


def forbidden_response():
    return jsonify({"message": "insufficient force rank"}), 403


def authenticate(func):
    @functools.wraps(func)
    def wrapper_authenticate(*args, **kwargs):
        auth_info = validate_token()
        return func(*args, **kwargs) if auth_info else fail_response()
    return wrapper_authenticate


def authenticate_return_auth(func):
    @functools.wraps(func)
    def wrapper_authenticate(*args, **kwargs):
        auth_info = validate_token()
        if not auth_info:
            return fail_response()
        kwargs['auth_info'] = auth_info
        return func(*args, **kwargs)
    return wrapper_authenticate


def require_rank(required_rank):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            auth_info = validate_token()
            if not auth_info:
                return fail_response()
            if not rank_at_least(auth_info.user.force_rank, required_rank):
                return forbidden_response()
            kwargs['auth_info'] = auth_info
            return func(*args, **kwargs)
        return wrapper
    return decorator
