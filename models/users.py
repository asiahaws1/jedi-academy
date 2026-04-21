import marshmallow as ma
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID

from db import db


VALID_RANKS = {'youngling', 'padawan', 'knight', 'master', 'council', 'grand_master'}


class Users(db.Model):
    __tablename__ = 'Users'

    user_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    temple_id = db.Column(UUID(as_uuid=True), db.ForeignKey('Temples.temple_id'), nullable=True)
    username = db.Column(db.String(), nullable=False, unique=True)
    email = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)
    force_rank = db.Column(db.String(), nullable=False, default='youngling')
    midi_count = db.Column(db.Integer(), nullable=False, default=0)
    is_active = db.Column(db.Boolean(), nullable=False, default=True)
    joined_date = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)

    temple = db.relationship('Temples', back_populates='users')
    auth = db.relationship('AuthTokens', back_populates='user', cascade='all, delete-orphan')
    master_profile = db.relationship('Masters', back_populates='user', uselist=False, cascade='all, delete-orphan')
    padawan_profile = db.relationship('Padawans', back_populates='user', uselist=False, cascade='all, delete-orphan')
    lightsabers = db.relationship('Lightsabers', back_populates='owner', cascade='all, delete-orphan')

    def __init__(self, username, email, password, force_rank='youngling', midi_count=0, temple_id=None, is_active=True):
        self.username = username
        self.email = email
        self.password = password
        self.force_rank = force_rank
        self.midi_count = midi_count
        self.temple_id = temple_id
        self.is_active = is_active

    def new_user_obj():
        return Users('', '', '', 'youngling', 0, None, True)


class UsersSchema(ma.Schema):
    class Meta:
        fields = ['user_id', 'temple_id', 'username', 'email', 'force_rank', 'midi_count', 'is_active', 'joined_date', 'temple']

    user_id = ma.fields.UUID()
    temple_id = ma.fields.UUID(allow_none=True)
    username = ma.fields.String(required=True)
    email = ma.fields.Email(required=True)
    force_rank = ma.fields.String(required=True, dump_default='youngling')
    midi_count = ma.fields.Integer(required=True, dump_default=0)
    is_active = ma.fields.Boolean(required=True, dump_default=True)
    joined_date = ma.fields.DateTime()

    temple = ma.fields.Nested('TemplesSchema', only=['temple_id', 'temple_name', 'planet'])


user_schema = UsersSchema()
users_schema = UsersSchema(many=True)
