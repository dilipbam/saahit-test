from flask import jsonify
from marshmallow import ValidationError


# custom validation error
def validation_error(msg, field_name=None):
    """
    Raises a validation error with the provided message and optional field name.
    """
    raise ValidationError(message=msg, field_name=field_name)


# success messages

def success_response(msg, data=[]):
    """
    Returns a success response with message, data, and status code 200.
    """
    return jsonify({'message': msg, 'data': data, 'status': 200})


# def created(msg, data):
#     """
#     Returns a response with status code 201 Created.
#     """
#     return jsonify({'message': msg, 'data': data, 'status': 201}), 201
#
#
# def accepted(msg):
#     """
#     Returns a response with status code 202 Accepted.
#     """
#     return jsonify({'message': msg, 'status': 202}), 202


def non_authoritative_information(msg):
    """
    Returns a response with status code 203 Non-Authoritative Information.
    """
    return jsonify({'message': msg, 'status': 203})


# # 3xx error codes
# def moved_permanently(msg, location):
#     """
#     Returns a response with status code 301 Moved Permanently and the specified location.
#     """
#     response = jsonify({'message': f'Moved Permanently {msg}', 'location': location, 'status': 301})
#     response.headers['Location'] = location
#     return response


def found(msg, location):
    """
    Returns a response with status code 302 Found and the specified location.
    """
    response = jsonify({'message': f'Found {msg}', 'location': location, 'status': 302})
    response.headers['Location'] = location
    return response


def temporary_redirect(msg, location):
    """
    Returns a response with status code 307 Temporary Redirect and the specified location.
    """
    response = jsonify({'message': f'Temporary Redirect : {msg}', 'location': location, 'status': 307})
    response.headers['Location'] = location
    return response


def permanent_redirect(msg, location):
    """
    Returns a response with status code 308 Permanent Redirect and the specified location.
    """
    response = jsonify({'message': f'Permanent Redirect {msg}', 'location': location, 'status': 308})
    response.headers['Location'] = location
    return response


# 4xx error codes
def unauthorized_response(msg):
    """
    Returns an unauthorized response with message and status code 401.
    """
    return jsonify({'message': msg, 'status': 401})


def not_found_error(msg):
    """
    Returns a not found error response with message and status code 404.
    """
    return jsonify({'message': msg, 'status': 404})


def bad_request_error(msg):
    """
    Returns a bad request error response with message and status code 400.
    """
    return jsonify({'message': msg, 'status': 400})


def forbidden_error(msg):
    """
    Returns a forbidden error response with message and status code 403.
    """
    return jsonify({'message': msg, 'status': 403})


def unsupported_media_type_error(msg):
    """
    Returns an unsupported media type error response with message and status code 415.
    """
    return jsonify({'message': msg, 'status': 415})


def conflict_error(msg, errors=None):
    """
    Returns a conflict error response with message and status code 409.
    """
    return jsonify({'message': msg, 'status': 409, 'errors':errors})


# 5xx error codes
def server_error(msg):
    """
    Returns a server error response with message and status code 500.
    """
    return jsonify({'message': msg, 'status': 500})


def not_implemented(msg):
    """
    Returns a response with status code 501 Not Implemented.
    """
    return jsonify({'message': msg, 'status': 501}), 501


def bad_gateway(msg):
    """
    Returns a response with status code 502 Bad Gateway.
    """
    return jsonify({'message': msg, 'status': 502}), 502


def service_unavailable(msg):
    """
    Returns a response with status code 503 Service Unavailable.
    """
    return jsonify({'message': msg, 'status': 503}), 503


def gateway_timeout(msg):
    """
    Returns a response with status code 504 Gateway Timeout.
    """
    return jsonify({'message': msg, 'status': 504}), 504


def http_version_not_supported():
    """
    Returns a response with status code 505 HTTP Version Not Supported.
    """
    return jsonify({'message': 'HTTP Version Not Supported', 'status': 505}), 505


def insufficient_storage():
    """
    Returns a response with status code 507 Insufficient Storage.
    """
    return jsonify({'message': 'Insufficient Storage', 'status': 507}), 507


def network_authentication_required():
    """
    Returns a response with status code 511 Network Authentication Required.
    """
    return jsonify({'message': 'Network Authentication Required', 'status': 511}), 511
