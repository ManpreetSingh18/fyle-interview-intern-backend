from flask import Response, jsonify, make_response


class APIResponse(Response):
    @classmethod
    def respond(cls, data, status=200, message=None):
        response_data = {
            "data": data,
            
        }
        return make_response(jsonify(response_data), status,message)  # Include status in the response
