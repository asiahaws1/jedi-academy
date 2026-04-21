import marshmallow as ma
import uuid
from sqlalchemy.dialects.postgresql import UUID

from db import db


class Courses(db.Model):
    __tablename__ = 'Courses'

    course_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    instructor_id = db.Column(UUID(as_uuid=True), db.ForeignKey('Masters.master_id', ondelete='SET NULL'), nullable=True)
    course_name = db.Column(db.String(), nullable=False, unique=True)
    difficulty = db.Column(db.String(), nullable=False, default='beginner')
    duration_weeks = db.Column(db.Integer(), nullable=False, default=4)
    max_students = db.Column(db.Integer(), nullable=False, default=10)

    instructor = db.relationship('Masters', back_populates='courses')
    enrollments = db.relationship('PadawanCourses', back_populates='course', cascade='all, delete-orphan')

    def __init__(self, course_name, difficulty='beginner', duration_weeks=4, max_students=10, instructor_id=None):
        self.course_name = course_name
        self.difficulty = difficulty
        self.duration_weeks = duration_weeks
        self.max_students = max_students
        self.instructor_id = instructor_id

    def new_course_obj():
        return Courses('', 'beginner', 4, 10, None)


class CoursesSchema(ma.Schema):
    class Meta:
        fields = ['course_id', 'instructor_id', 'course_name', 'difficulty', 'duration_weeks', 'max_students', 'instructor']

    course_id = ma.fields.UUID()
    instructor_id = ma.fields.UUID(allow_none=True)
    course_name = ma.fields.String(required=True)
    difficulty = ma.fields.String(required=True, dump_default='beginner')
    duration_weeks = ma.fields.Integer(required=True, dump_default=4)
    max_students = ma.fields.Integer(required=True, dump_default=10)

    instructor = ma.fields.Nested('MastersSchema', only=['master_id', 'master_name', 'specialization'])


course_schema = CoursesSchema()
courses_schema = CoursesSchema(many=True)
