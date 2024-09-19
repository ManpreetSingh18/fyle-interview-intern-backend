from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment
from core.models.teachers import Teacher  # Ensure your Teacher model is correctly imported
from .schema import TeacherSchema  # Assuming you have a TeacherSchema for serialization

from .schema import AssignmentSchema, AssignmentSubmitSchema,AssignmentGradeSchema

principal_assignments_resources = Blueprint('principal_assignments_resources', __name__)

@principal_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(p):
    """List all submitted and graded assignments"""
    # Assuming you have a method to retrieve all submitted assignments
    # This method should fetch assignments by their state
    all_assignments = Assignment.get_all_submitted_and_graded()
    all_assignments_dump = AssignmentSchema().dump(all_assignments, many=True)
    return APIResponse.respond(data=all_assignments_dump)

@principal_assignments_resources.route('/teachers', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_teachers(p):
    """List all teachers"""
    teachers = Teacher.query.all()  # Fetch all teachers from the database
    teachers_dump = TeacherSchema().dump(teachers, many=True)  # Serialize the data
    return APIResponse.respond(data=teachers_dump)


@principal_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def grade_assignment(p, incoming_payload):
    """Grade or re-grade an assignment"""
    # Load and validate the incoming payload
    grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)

     # Fetch the assignment by ID
    assignment = Assignment.get_by_id(grade_assignment_payload.id)

    # Check if the assignment is in draft state
    # set_assignment_to_draft(5)
    if assignment.state == 'DRAFT':
        return APIResponse.respond(
            data={
                'error': 'FyleError',
                'message': 'Cannot grade a draft assignment.'  # Provide a meaningful error message
            },
            status=400  # Return a 400 status code for bad request
        )
    
    
    # Call the mark_grade method from the Assignment model
    graded_assignment = Assignment.mark_grade(
        _id=grade_assignment_payload.id,
        grade=grade_assignment_payload.grade,
        auth_principal=p  # Pass the authenticated principal if needed
    )
    db.session.commit()  # Commit the changes to the database

    # Serialize the graded assignment data to return in the response
    graded_assignment_dump = AssignmentSchema().dump(graded_assignment)

    return APIResponse.respond(data={
        'id': graded_assignment_dump['id'],
        'state': graded_assignment_dump['state'],  # This should be 'GRADED'
        'grade': graded_assignment_dump['grade']  # This should match GradeEnum.C or other grades
    },
    status=200)