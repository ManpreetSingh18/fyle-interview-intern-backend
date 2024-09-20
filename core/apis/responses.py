from flask import Response, jsonify, make_response


class APIResponse(Response):
    @classmethod
    def respond(cls, data, status=200, message=None):
        response_data = {
            "data": data,
            
        }
        # If the data is an error, include it accordingly
         # If the data is an error, include it accordingly
        if isinstance(data, dict) and 'error' in data:
            response_data['error'] = data['error']
            # Include message if provided
            if message:
                response_data['message'] = message
        return make_response(jsonify(response_data), status)
