import marshmallow as ma
import uuid
from sqlalchemy.dialects.postgresql import UUID

from db import db


class AuthTokens(db.Model):
    __tablename__ = 'AuthTokens'

    auth_token = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('Users.user_id', ondelete='CASCADE'), nullable=False)
    expiration_date = db.Column(db.DateTime(), nullable=False)

    user = db.relationship('Users', back_populates='auth')

    def __init__(self, user_id, expiration_date):
        self.user_id = user_id
        self.expiration_date = expiration_date


    def new_token_obj():
        return AuthTokens(None, None)


class AuthTokensSchema(ma.Schema):
    class Meta:
        fields = ['auth_token', 'user_id', 'expiration_date', 'user']

    auth_token = ma.fields.UUID()
    user_id = ma.fields.UUID()
    expiration_date = ma.fields.DateTime()

    user = ma.fields.Nested('UsersSchema', only=['user_id', 'username', 'email', 'force_rank', 'is_active', 'temple_id'])


auth_token_schema = AuthTokensSchema()
