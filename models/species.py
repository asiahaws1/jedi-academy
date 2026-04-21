import marshmallow as ma
import uuid
from sqlalchemy.dialects.postgresql import UUID

from db import db


class Species(db.Model):
    __tablename__ = 'Species'

    species_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    species_name = db.Column(db.String(), nullable=False, unique=True)
    homeworld = db.Column(db.String(), nullable=False)
    force_sensitive = db.Column(db.Boolean(), nullable=False, default=False)
    avg_lifespan = db.Column(db.Integer(), nullable=False, default=80)

    padawans = db.relationship('Padawans', back_populates='species', cascade='all')

    def __init__(self, species_name, homeworld, force_sensitive=False, avg_lifespan=80):
        self.species_name = species_name
        self.homeworld = homeworld
        self.force_sensitive = force_sensitive
        self.avg_lifespan = avg_lifespan

    def new_species_obj():
        return Species('', '', False, 80)


class SpeciesSchema(ma.Schema):
    class Meta:
        fields = ['species_id', 'species_name', 'homeworld', 'force_sensitive', 'avg_lifespan', 'padawans']

    species_id = ma.fields.UUID()
    species_name = ma.fields.String(required=True)
    homeworld = ma.fields.String(required=True)
    force_sensitive = ma.fields.Boolean(required=True, dump_default=False)
    avg_lifespan = ma.fields.Integer(required=True, dump_default=80)

    padawans = ma.fields.Nested('PadawansSchema', many=True, only=['padawan_id', 'padawan_name', 'training_level'])


species_schema = SpeciesSchema()
species_many_schema = SpeciesSchema(many=True)
