from functools import wraps
from flask import request, jsonify, g, current_app, session
import jwt
from db_models import User


def get_authenticated_user():

    # this should work on register and login routes to initate all required tools for user
    user_id = session.get('user_id')
    if user_id is not None:
        user = User.query.get(user_id)
        return user

    token = request.headers.get('Authorization')

    if not token:
        return None

    try:
        payload = jwt.decode(
            token, current_app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

    user = User.query.get(payload['user_id'])
    return user


def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function
