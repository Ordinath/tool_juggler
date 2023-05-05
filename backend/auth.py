from functools import wraps
from flask import request, jsonify
import jwt
from db_models import User


def get_authenticated_user(app):
    token = request.headers.get('Authorization')
    if not token:
        return None

    try:
        payload = jwt.decode(
            token, app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

    user = User.query.get(payload['user_id'])
    return user


def require_auth(app, f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_authenticated_user(app)
        if user is None:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function
