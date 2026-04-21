from flask import jsonify, request

from db import db
from models.padawan_courses import PadawanCourses, enrollment_schema, enrollments_schema
from models.padawans import Padawans
from models.courses import Courses
from util.reflection import populate_object
from lib.authenticate import require_rank


@require_rank('master')
def add_enrollment(auth_info):
    post_data = request.form if request.form else request.get_json() or {}

    padawan_id = post_data.get('padawan_id')
    course_id = post_data.get('course_id')

    if not padawan_id or not course_id:
        return jsonify({"message": "padawan_id and course_id are required"}), 400

    padawan = db.session.query(Padawans).filter(Padawans.padawan_id == padawan_id).first()
    if not padawan:
        return jsonify({"message": "padawan does not exist"}), 400

    course = db.session.query(Courses).filter(Courses.course_id == course_id).first()
    if not course:
        return jsonify({"message": "course does not exist"}), 400

    existing = db.session.query(PadawanCourses).filter(
        PadawanCourses.padawan_id == padawan_id,
        PadawanCourses.course_id == course_id,
    ).first()
    if existing:
        return jsonify({"message": "padawan already enrolled in this course"}), 400

    current_enrollment_count = db.session.query(PadawanCourses).filter(PadawanCourses.course_id == course_id).count()
    if current_enrollment_count >= course.max_students:
        return jsonify({"message": "course is full"}), 400

    new_enrollment = PadawanCourses.new_enrollment_obj()
    populate_object(new_enrollment, post_data)

    try:
        db.session.add(new_enrollment)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to enroll padawan"}), 400

    return jsonify({"message": "padawan enrolled", "result": enrollment_schema.dump(new_enrollment)}), 201


@require_rank('master')
def delete_enrollment(padawan_id, course_id, auth_info):
    enrollment = db.session.query(PadawanCourses).filter(
        PadawanCourses.padawan_id == padawan_id,
        PadawanCourses.course_id == course_id,
    ).first()

    if not enrollment:
        return jsonify({"message": "enrollment not found"}), 404

    try:
        db.session.delete(enrollment)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to remove enrollment"}), 400

    return jsonify({"message": "enrollment removed"}), 200
