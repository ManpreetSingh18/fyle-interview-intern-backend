from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment

from .schema import AssignmentSchema, AssignmentSubmitSchema
student_assignments_resources = Blueprint('student_assignments_resources', __name__)


@student_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(p):
    """Returns list of assignments"""
    students_assignments = Assignment.get_assignments_by_student(p.student_id)
    students_assignments_dump = AssignmentSchema().dump(students_assignments, many=True)
    return APIResponse.respond(data=students_assignments_dump)


@student_assignments_resources.route('/assignments', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def upsert_assignment(p, incoming_payload):
    """Create or Edit an assignment"""
     # Check if content is None
    if incoming_payload.get('content') is None:
        return APIResponse.respond(
            data={'error': 'Content cannot be null.'},
            status=400
        )
    
    assignment = AssignmentSchema().load(incoming_payload)
    assignment.student_id = p.student_id

    upserted_assignment = Assignment.upsert(assignment)
    db.session.commit()
    upserted_assignment_dump = AssignmentSchema().dump(upserted_assignment)
    return APIResponse.respond(data=upserted_assignment_dump)


@student_assignments_resources.route('/assignments/submit', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def submit_assignment(p, incoming_payload):
    """Submit an assignment"""
    submit_assignment_payload = AssignmentSubmitSchema().load(incoming_payload)


    # Fetch the assignment by ID
    assignment = Assignment.get_by_id(submit_assignment_payload.id)

    # Check if the assignment exists
    if assignment is None:
        return APIResponse.respond(
            data={'error': 'Assignment not found.'},
            status=404  # Not found status
        )
    
    # # Check if the assignment is already graded
    # if assignment.state == 'GRADED':
    #     return APIResponse.respond(
    #         data={
    #             'error': 'Cannot submit an already graded assignment.',
    #             'teacher_id': assignment.teacher_id ,
    #             'student_id': assignment.student_id ,
    #             'state': 'SUBMITTED'
    #         },
    #         status=200
    #     )
    
    # Check if the assignment is in DRAFT state before submitting
    if assignment.state != 'DRAFT':
        return APIResponse.respond(
            data={
                'error': 'FyleError',
                'message': 'only a draft assignment can be submitted'
            },
            status=400  
        )
    
    submitted_assignment = Assignment.submit(
        _id=submit_assignment_payload.id,
        teacher_id=submit_assignment_payload.teacher_id,
        auth_principal=p
    )
    db.session.commit()
    
    submitted_assignment_dump = AssignmentSchema().dump(submitted_assignment)
    return APIResponse.respond(
        data=submitted_assignment_dump,
        status=200
    )