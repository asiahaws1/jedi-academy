from flask import Blueprint

import controllers


enrollments = Blueprint('enrollments', __name__)


@enrollments.route('/enrollment', methods=['POST'])
def add_enrollment_route():
    return controllers.add_enrollment()


@enrollments.route('/enrollment/<padawan_id>/<course_id>', methods=['DELETE'])
def delete_enrollment_route(padawan_id, course_id):
    return controllers.delete_enrollment(padawan_id, course_id)
