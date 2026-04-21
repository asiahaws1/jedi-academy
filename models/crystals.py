import marshmallow as ma
import uuid
from sqlalchemy.dialects.postgresql import UUID

from db import db


class Crystals(db.Model):
    __tablename__ = 'Crystals'

    crystal_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crystal_type = db.Column(db.String(), nullable=False, unique=True)
    origin_planet = db.Column(db.String(), nullable=False)
    rarity_level = db.Column(db.String(), nullable=False, default='common')
    force_amplify = db.Column(db.Float(), nullable=False, default=1.0)

    lightsabers = db.relationship('Lightsabers', back_populates='crystal', cascade='all')

    def __init__(self, crystal_type, origin_planet, rarity_level='common', force_amplify=1.0):
        self.crystal_type = crystal_type
        self.origin_planet = origin_planet
        self.rarity_level = rarity_level
        self.force_amplify = force_amplify

    def new_crystal_obj():
        return Crystals('', '', 'common', 1.0)


class CrystalsSchema(ma.Schema):
    class Meta:
        fields = ['crystal_id', 'crystal_type', 'origin_planet', 'rarity_level', 'force_amplify']

    crystal_id = ma.fields.UUID()
    crystal_type = ma.fields.String(required=True)
    origin_planet = ma.fields.String(required=True)
    rarity_level = ma.fields.String(required=True, dump_default='common')
    force_amplify = ma.fields.Float(required=True, dump_default=1.0)


crystal_schema = CrystalsSchema()
crystals_schema = CrystalsSchema(many=True)
