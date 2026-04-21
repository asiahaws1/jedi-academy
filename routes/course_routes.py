from flask import Blueprint

import controllers


courses = Blueprint('courses', __name__)


@courses.route('/course', methods=['POST'])
def add_course_route():
    return controllers.add_course()


@courses.route('/courses/<difficulty_level>', methods=['GET'])
def get_courses_by_difficulty_route(difficulty_level):
    return controllers.get_courses_by_difficulty(difficulty_level)


@courses.route('/course/<course_id>', methods=['PUT'])
def update_course_route(course_id):
    return controllers.update_course_by_id(course_id)


@courses.route('/course/<course_id>', methods=['DELETE'])
def delete_course_route(course_id):
    return controllers.delete_course_by_id(course_id)
