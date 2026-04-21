import marshmallow as ma
import uuid
from sqlalchemy.dialects.postgresql import UUID

from db import db


class Padawans(db.Model):
    __tablename__ = 'Padawans'

    padawan_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    master_id = db.Column(UUID(as_uuid=True), db.ForeignKey('Masters.master_id', ondelete='SET NULL'), nullable=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('Users.user_id', ondelete='CASCADE'), nullable=False, unique=True)
    species_id = db.Column(UUID(as_uuid=True), db.ForeignKey('Species.species_id', ondelete='SET NULL'), nullable=True)
    padawan_name = db.Column(db.String(), nullable=False, unique=True)
    age = db.Column(db.Integer(), nullable=False)
    training_level = db.Column(db.Integer(), nullable=False, default=1)
    graduation_date = db.Column(db.DateTime(), nullable=True)

    master = db.relationship('Masters', back_populates='padawans')
    user = db.relationship('Users', back_populates='padawan_profile')
    species = db.relationship('Species', back_populates='padawans')
    enrollments = db.relationship('PadawanCourses', back_populates='padawan', cascade='all, delete-orphan')

    def __init__(self, user_id, padawan_name, age, master_id=None, species_id=None, training_level=1, graduation_date=None):
        self.user_id = user_id
        self.padawan_name = padawan_name
        self.age = age
        self.master_id = master_id
        self.species_id = species_id
        self.training_level = training_level
        self.graduation_date = graduation_date

    def new_padawan_obj():
        return Padawans(None, '', 0, None, None, 1, None)


class PadawansSchema(ma.Schema):
    class Meta:
        fields = ['padawan_id', 'master_id', 'user_id', 'species_id', 'padawan_name', 'age', 'training_level', 'graduation_date', 'master', 'species']

    padawan_id = ma.fields.UUID()
    master_id = ma.fields.UUID(allow_none=True)
    user_id = ma.fields.UUID(required=True)
    species_id = ma.fields.UUID(allow_none=True)
    padawan_name = ma.fields.String(required=True)
    age = ma.fields.Integer(required=True)
    training_level = ma.fields.Integer(required=True, dump_default=1)
    graduation_date = ma.fields.DateTime(allow_none=True)

    master = ma.fields.Nested('MastersSchema', only=['master_id', 'master_name', 'specialization'])
    species = ma.fields.Nested('SpeciesSchema', only=['species_id', 'species_name', 'homeworld'])


padawan_schema = PadawansSchema()
padawans_schema = PadawansSchema(many=True)
