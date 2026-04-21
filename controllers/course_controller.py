from flask import jsonify, request

from db import db
from models.courses import Courses, course_schema, courses_schema
from models.masters import Masters
from util.reflection import populate_object
from lib.authenticate import require_rank, authenticate_return_auth, rank_at_least


@require_rank('master')
def add_course(auth_info):
    post_data = request.form if request.form else request.get_json() or {}

    required = ['course_name', 'instructor_id']
    for field in required:
        if not post_data.get(field):
            return jsonify({"message": f"{field} is required"}), 400

    if db.session.query(Courses).filter(Courses.course_name == post_data['course_name']).first():
        return jsonify({"message": "course_name already exists"}), 400

    instructor = db.session.query(Masters).filter(Masters.master_id == post_data['instructor_id']).first()
    if not instructor:
        return jsonify({"message": "instructor does not exist"}), 400

    new_course = Courses.new_course_obj()
    populate_object(new_course, post_data)

    try:
        db.session.add(new_course)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to create course"}), 400

    return jsonify({"message": "course created", "result": course_schema.dump(new_course)}), 201


@authenticate_return_auth
def get_courses_by_difficulty(difficulty_level, auth_info):
    courses = db.session.query(Courses).filter(Courses.difficulty == difficulty_level).all()
    return jsonify({"message": "courses found", "results": courses_schema.dump(courses)}), 200


@authenticate_return_auth
def update_course_by_id(course_id, auth_info):
    course = db.session.query(Courses).filter(Courses.course_id == course_id).first()
    if not course:
        return jsonify({"message": f"course {course_id} not found"}), 404

    is_instructor = False
    if course.instructor_id:
        instructor = db.session.query(Masters).filter(Masters.master_id == course.instructor_id).first()
        if instructor and str(instructor.user_id) == str(auth_info.user_id):
            is_instructor = True

    if not is_instructor and not rank_at_least(auth_info.user.force_rank, 'council'):
        return jsonify({"message": "unauthorized"}), 403

    post_data = request.form if request.form else request.get_json() or {}

    if 'course_name' in post_data and post_data['course_name']:
        conflict = db.session.query(Courses).filter(Courses.course_name == post_data['course_name'], Courses.course_id != course_id).first()
        if conflict:
            return jsonify({"message": "course_name already exists"}), 400
    if 'instructor_id' in post_data and post_data['instructor_id']:
        instructor = db.session.query(Masters).filter(Masters.master_id == post_data['instructor_id']).first()
        if not instructor:
            return jsonify({"message": "instructor does not exist"}), 400

    populate_object(course, post_data)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to update course"}), 400

    return jsonify({"message": "course updated", "result": course_schema.dump(course)}), 200


@authenticate_return_auth
def delete_course_by_id(course_id, auth_info):
    course = db.session.query(Courses).filter(Courses.course_id == course_id).first()
    if not course:
        return jsonify({"message": f"course {course_id} not found"}), 404

    is_instructor = False
    if course.instructor_id:
        instructor = db.session.query(Masters).filter(Masters.master_id == course.instructor_id).first()
        if instructor and str(instructor.user_id) == str(auth_info.user_id):
            is_instructor = True

    if not is_instructor and not rank_at_least(auth_info.user.force_rank, 'council'):
        return jsonify({"message": "unauthorized"}), 403

    try:
        db.session.delete(course)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to cancel course"}), 400

    return jsonify({"message": "course canceled"}), 200
