## -- Importing External Modules -- ##
from flask import make_response, json, wrappers, g, request
from timeit import default_timer as timer
from functools import wraps

## -- Importing Internal Modules -- ##
from app.resources.folder_structure import folder_structure_get, folder_structure_post
from app.resources.image_serving import image_serving_get
from app.server import app


def add_body(generic_function: callable):
    """
    Add the json data or url params to the data received by the endpoint

    Args:
        generic_function (callable): The endpoint

    Returns:
        any: Whatever the endpoint returns
    """

    @wraps(generic_function)
    def wrapper(*args, **kwargs):

        request_data = {}

        if request.args:
            hold_args = {
                str(key).lower(): value 
                for key, value in request.args.items()
            }

            request_data.update(hold_args)

        if request.data:
        
            json_data = request.get_json()
            if json_data and isinstance(json_data, dict):

                hold_json = {
                    str(key).lower(): value 
                    for key, value in json_data.items()
                }
                request_data.update(hold_json)

        if request_data:
            kwargs["request"] = request_data
              
        response = generic_function(*args, **kwargs)
        return response

    return wrapper


def add_files(generic_function: callable):
    """
    Add the form-data to the request data

    Args:
        generic_function (callable): The endpoint

    Returns:
        any: Whatever the endpoint returns
    """

    @wraps(generic_function)
    def wrapper(*args, **kwargs):

        request_data = {}

        hold = dict(request.files)
    
        for key, value in hold.items():
            request_data[str(key).lower()] = value

        if request_data:
            kwargs["files"] = request_data
              
        response = generic_function(*args, **kwargs)
        return response

    return wrapper


# Cors handler
def add_cors_return(resp) -> json:

    response = make_response(resp)
    
    if not response.headers.get("Content-Type"):
        response.headers['Content-Type'] = 'application/json'
    
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    response.headers.add("Access-Control-Expose-Headers", "Content-Disposition")
    response.headers.add("Access-Control-Allow-Credentials", True)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


# Generic
@app.errorhandler(Exception)
def internal_server_error(e):

    # You can add some logging here or even add some error handlers for especific cases
    return {
        "status": False,
        "message": "Internal Server Error"
    }

# Not found
@app.errorhandler(404)
def not_found_error(e):

    # You can add some logging here or even add some error handlers for especific cases
    return {
        "status": False,
        "message": "Not Found"
    }

# Especific
@app.errorhandler(400)
def bad_request_error(e):

    # You can add some logging here or even add some error handlers for especific cases
    description = e.description
    message: str = None

    if isinstance(description, str):
        message = description

    elif isinstance(description, dict):
        message = description.get('message') if description.get("message") else description

    else:
        message = description

    return {
        "status": False,
        "message": message
    }


# Before request
@app.before_request
def before_request():
    
    g.start = timer()


# After request
@app.after_request
def after_request(resp):

    g.finish = timer()
    
    resp = add_cors_return(resp)

    if g.get("start") and g.get("finish"):
        resp.headers.add("X-Process-Time", "{:.5f}".format(g.finish - g.start))
    
    return resp


#### routing
@app.route("/image/<path:full_path>", methods = ['GET'])
@add_body
def image_service(**kwargs) -> wrappers.Response:
    """
    Returns a saved image

    kwargs:
        full_path (str): Path to the image.
    """

    return image_serving_get(**kwargs)


@app.route("/structure", methods = ['GET', "POST"])
@add_body
@add_files
def folder_structure(**kwargs) -> wrappers.Response:
    """
    Returns a saved image

    kwargs:
        full_path (str): Path to the image.
    """

    if request.method.upper() == 'GET':
        return folder_structure_get(**kwargs)
    
    else:
        return folder_structure_post(**kwargs)